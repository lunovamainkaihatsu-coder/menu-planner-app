# --- bootstrap ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------
import streamlit as st
from common.style import inject_css, card, endcard, bubble
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image

inject_css()

st.title("AIサポート")

mode = st.radio("機能を選択", ["調理Q&A","代替提案","SNS用キャプション"])

if mode == "調理Q&A":
    q = st.text_area("質問", "賽の目切りの手順を教えて。要点だけ短く。")
    if st.button("聞く", type="primary"):
        text, err = ai_text(
            f"家庭料理の先生として、手順→コツ→失敗しがちな点→対策 の順で簡潔に。質問: {q}",
            model_text="gpt-4o-mini"
        )
        st.write(text if text else f"エラー: {err}")

elif mode == "代替提案":
    dish = st.text_input("料理名", "ハンバーグ")
    avoid = st.text_input("避けたい/不足の食材（カンマ区切り）", "卵, パン粉")
    if st.button("代替を提案", type="primary"):
        schema = """{
          "subs":[{"target":"置き換え対象","alternative":"代替食材/方法","reason":"理由","ratio":"比率や分量"}]
        }"""
        data, err = ai_json(
            prompt=f"料理『{dish}』で [{avoid}] を使わずに作る代替案を日本の家庭向けに3件。各項目は target/alternative/reason/ratio。",
            schema_hint=schema,
            model_json="gpt-4o"
        )
        if err:
            st.error(err)
        else:
            subs = data.get("subs") if isinstance(data, dict) else None
            if not subs:
                st.code(data, language="json")
            else:
                for r in subs:
                    st.markdown(f"- **{r.get('target')} → {r.get('alternative')}**（比率: {r.get('ratio','-')}）\n  - 理由: {r.get('reason')}")

else:
    name = st.text_input("料理名", "豚汁")
    tags = st.text_input("ハッシュタグ", "#おうちごはん #節約 #作り置き")
    if st.button("文章を作る", type="primary"):
        text, err = ai_text(
            f"X/Instagram投稿文を日本語で2案。各120字以内。自然体でやさしいトーン。料理名:{name}。最後にハッシュタグ:{tags}",
            model_text="gpt-4o-mini"
        )
        st.write(text if text else f"エラー: {err}")
