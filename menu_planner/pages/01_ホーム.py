# pages/01_ホーム.py

import sys
from pathlib import Path

import streamlit as st
from common.style import inject_css, card, endcard, bubble
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image


# --- プロジェクトルートをパスに追加（Luna-dev/menu_planner 配下用） ---
ROOT = Path(__file__).resolve().parents[1]  # menu_planner フォルダ
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ここがポイント！ もう src.common ではなく utils から読む

# CSS 適用
inject_css()

# タイトル
st.title("おかえり、ごはんの時間だよ 🍚")

# =========================
# 今日のメニューカード
# =========================
card("今日のメニュー")
st.markdown(
    """
**朝**：ソース焼うどん  
**昼**：ひじき煮（作り置き）  
**夜**：一汁三菜セット
""",
    unsafe_allow_html=True,
)
endcard()

# =========================
# 今すぐ作れる（在庫×時間フィルタ）カード
# =========================
card("今すぐ作れる（在庫×時間フィルタ）カード")

cols = st.columns(3)

with cols[0]:
    st.markdown(
        "🍳 **豚バラ塩キャベツ**  \n"
        "<span class='chip'>10分</span>",
        unsafe_allow_html=True,
    )

with cols[1]:
    st.markdown(
        "🍲 **豆腐とわかめの味噌汁**  \n"
        "<span class='chip'>8分</span>",
        unsafe_allow_html=True,
    )

with cols[2]:
    st.markdown(
        "🥗 **大根ツナサラダ**  \n"
        "<span class='chip'>7分</span>",
        unsafe_allow_html=True,
    )

endcard()

# =========================
# ルナからひとこと
# =========================
bubble(
    "今日はちょっと肌寒いから、汁物を温かめにしよっか。"
    "だし多めにすると体ぽかぽかだよ。"
)
