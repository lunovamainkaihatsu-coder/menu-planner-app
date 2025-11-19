# --- bootstrap（相対パスを通す） ---
import sys
from pathlib import Path

# menu_planner/app.py の 1 つ上を基準にする
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ----------------------------------

import json
from datetime import datetime, date
import streamlit as st

# ★ ここが今回の一番重要ポイント ★
# src ではなく、同じフォルダ内の common/utils/logic/components を使う
from common.style import inject_css
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image

# --- データパス ---
DATA = data_dir()
ASSETS = assets_dir()

RECIPES = DATA / "recipes.json"
SETTINGS = DATA / "settings.json"
PANTRY = DATA / "pantry.json"
CHAT_LOG = DATA / "ai_chat_history.json"

# --- UI ---
st.title("AI料理相談（ルナと一緒に考える）")
inject_css()

# --- セッション ---
if "ai_chat" not in st.session_state:
    st.session_state.ai_chat = []

if "last_proposal" not in st.session_state:
    st.session_state.last_proposal = ""

if "last_recipe_struct" not in st.session_state:
    st.session_state.last_recipe_struct = {}

# --- メインUI ---
tab1, tab2 = st.tabs(["🍳 AIに相談", "📘 レシピ管理"])

with tab1:
    st.subheader("今日の献立どうする？ルナが一緒に考えるよ！")

    user_msg = st.text_area("相談したい内容を書いてね：", height=100)

    if st.button("ルナに相談 ↓"):
        if user_msg.strip():
            st.session_state.ai_chat.append(
                {"role": "user", "content": user_msg, "time": str(datetime.now())}
            )

            with st.spinner("ルナが考え中…"):
                reply = ai_text(
                    prompt=user_msg,
                    system="あなたは料理と献立の専門AIアシスタントのルナです。親しみやすく答えてください。"
                )

            st.session_state.ai_chat.append(
                {"role": "assistant", "content": reply, "time": str(datetime.now())}
            )

            # 保存
            write_json(CHAT_LOG, st.session_state.ai_chat)

    # --- 会話ログ表示 ---
    for chat in st.session_state.ai_chat:
        if chat["role"] == "user":
            st.markdown(f"**👤 ご主人：** {chat['content']}")
        else:
            st.markdown(f"**🌙 ルナ：** {chat['content']}")

with tab2:
    st.subheader("レシピ管理（β）")

    # レシピ読み込み
    recipes = read_json(RECIPES, default=[])

    for r in recipes:
        st.markdown(f"### 🍽 {r.get('name','(名前なし)')}")
        st.markdown(f"- **時間**: {r.get('time','--')} 分")
        st.markdown(f"- **食材**: {', '.join(r.get('ingredients', []))}")
        st.divider()

