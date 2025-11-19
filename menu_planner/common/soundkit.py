# src/common/soundkit.py
from __future__ import annotations
from pathlib import Path
import base64
import streamlit as st

# ==== assets ディレクトリの自動検出（どこに置いても動く） ====
THIS = Path(__file__).resolve()
ROOT = THIS.parents[2]           # .../Luna-app
SRC  = THIS.parents[1]           # .../Luna-app/src

def _guess_assets_dir() -> Path:
    # 1) 一般的な今回の構成: src/luna_heal_room/assets
    cand1 = SRC / "luna_heal_room" / "assets"
    # 2) ルート直下: Luna-app/assets
    cand2 = ROOT / "assets"
    # 3) soundkit と同階層に assets がある場合（保険）
    cand3 = THIS.parent / "assets"
    for p in (cand1, cand2, cand3):
        if p.exists():
            return p
    return cand2  # 最終フォールバック

ASSETS = _guess_assets_dir()
SFX_DIR = ASSETS / "sounds" / "sfx"
VOICES_DIR = ASSETS / "sounds" / "voices"

@st.cache_resource(show_spinner=False)
def _load_audio_b64(path: Path) -> str | None:
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return None

def _mime_for(ext: str) -> str:
    ext = ext.lower()
    if ext == ".wav": return "audio/wav"
    if ext == ".ogg": return "audio/ogg"
    return "audio/mpeg"  # mp3既定

def _audio_tag(b64: str, mime: str, volume: float=1.0, autoplay: bool=True, controls: bool=False) -> str:
    auto = "autoplay" if autoplay else ""
    ctr  = "controls" if controls else ""
    vol = max(0.0, min(1.0, float(volume)))
    return f"""
    <audio {ctr} {auto} onplay="this.volume={vol}">
      <source src="data:{mime};base64,{b64}">
    </audio>
    """

def play_sfx(name: str, volume: float=1.0, autoplay: bool=True, show_controls: bool=False):
    """assets/sounds/sfx/{name}.(mp3|wav|ogg) を探して再生"""
    for ext in (".mp3",".wav",".ogg"):
        f = SFX_DIR / f"{name}{ext}"
        if f.exists():
            b64 = _load_audio_b64(f)
            if b64:
                html = _audio_tag(b64, _mime_for(ext), volume, autoplay, show_controls)
                st.markdown(html, unsafe_allow_html=True)
            return  # 見つかったら終了

def play_voice(pack_id: str, key: str, volume: float=1.0, autoplay: bool=True, show_controls: bool=False) -> bool:
    """assets/sounds/voices/{pack_id}/{key}.(mp3|wav|ogg) を探して再生"""
    base = VOICES_DIR / pack_id
    for ext in (".mp3",".wav",".ogg"):
        f = base / f"{key}{ext}"
        if f.exists():
            b64 = _load_audio_b64(f)
            if b64:
                html = _audio_tag(b64, _mime_for(ext), volume, autoplay, show_controls)
                st.markdown(html, unsafe_allow_html=True)
                return True
    return False
