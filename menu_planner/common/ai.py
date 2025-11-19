from __future__ import annotations
import os, json, base64, hashlib, time
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv

# OpenAI (>=1.0.0)
try:
    from openai import OpenAI
except Exception:  # 古いSDKなど
    OpenAI = None  # type: ignore

# .env 読み込み
load_dotenv()

_CLIENT: Optional["OpenAI"] = None

def get_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    if OpenAI is None:
        return None
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY") or os.getenv("OPENAI")
    if not key:
        return None
    _CLIENT = OpenAI(api_key=key)
    return _CLIENT


# ---------------------------
#  テキスト（通常）
# ---------------------------
def ai_text(prompt: str, model_text: str = "gpt-4o-mini", system: str | None = None, temperature: float = 0.6):
    """
    シンプルなテキスト生成。 (chat.completions)
    戻り値: (text, error)
    """
    c = get_client()
    if not c:
        return None, "NO_CLIENT_OR_API_KEY"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        rsp = c.chat.completions.create(
            model=model_text,
            messages=messages,
            temperature=temperature,
        )
        text = rsp.choices[0].message.content
        return text, None
    except Exception as e:
        return None, str(e)


# ---------------------------
#  JSON（堅牢版：JSONモード + フォールバック + リトライ）
# ---------------------------
def ai_json(prompt: str, schema_hint: str | None = None, model_json: str = "gpt-4o"):
    """
    JSONを高確率で返すための堅牢版。
    1) chat.completions + response_format=json_object
    2) ダメなら通常テキスト→パース
    3) 2回までリトライ
    戻り値: (obj|dict|list|str, error|None)
    """
    c = get_client()
    if not c:
        return None, "NO_CLIENT_OR_API_KEY"

    sysmsg = "You are a strict JSON generator. Output ONLY valid JSON, no prose."
    if schema_hint:
        sysmsg += f" Schema (not literal, just hints): {schema_hint}"

    last_text = None
    for attempt in range(2):  # 最大2回
        # 1) JSONモード
        try:
            rsp = c.chat.completions.create(
                model=model_json,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": sysmsg},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            text = rsp.choices[0].message.content
            last_text = text
            return json.loads(text), None
        except Exception:
            pass

        # 2) テキスト→パース（フォールバック）
        try:
            t, err = ai_text(
                f"{sysmsg}\nReturn ONLY JSON. No backticks, no comments.\n\n{prompt}",
                model_text=model_json,
            )
            if err and attempt == 1:
                return None, err
            last_text = (t or "").strip()
            if "```" in last_text:
                parts = last_text.split("```")
                # 後ろからJSONっぽい塊を拾う
                for i in range(len(parts) - 1, -1, -1):
                    if "{" in parts[i] or "[" in parts[i]:
                        last_text = parts[i]
                        break
            s = last_text.replace(", }", " }").replace(", ]", " ]")
            return json.loads(s), None
        except Exception:
            if attempt == 1:
                # 最後は生テキストも返してUIで確認できるようにする
                return {"raw": last_text or ""}, None

    return None, "UNKNOWN_JSON_ERROR"


# ---------------------------
#  画像（保存まで）
# ---------------------------
def _safe_filename_from_text(text: str, ext: str = ".png") -> str:
    h = hashlib.md5((text + str(time.time())).encode("utf-8")).hexdigest()[:10]
    return f"img_{h}{ext}"

def ai_image(prompt: str, out_dir: Path, size: str = "1024x1024"):
    """
    画像を生成し、out_dirに保存してパスを返す。
    戻り値: (Path|None, error|None)
    """
    c = get_client()
    if not c:
        return None, "NO_CLIENT_OR_API_KEY"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        rsp = c.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
        )
        b64 = rsp.data[0].b64_json
        img_bytes = base64.b64decode(b64)
        out_path = out_dir / _safe_filename_from_text(prompt, ".png")
        out_path.write_bytes(img_bytes)
        return out_path, None
    except Exception as e:
        return None, str(e)
