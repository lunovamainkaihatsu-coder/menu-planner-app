import streamlit as st
from pathlib import Path

# ===== インポート（ここ修正済み） =====
from common.style import inject_css, card, endcard, bubble
from common.fileio import read_json, write_json
from common.pathkit import data_dir

inject_css()

# -----------------------------
# データ読込
# -----------------------------
DATA = data_dir()
SETTINGS = DATA / "prefs.json"

DEFAULT_PREFS = {
    "theme_color": "pink",
    "show_bubble": True,
    "voice_type": "normal"
}

DATA.mkdir(exist_ok=True, parents=True)
if not SETTINGS.exists():
    write_json(SETTINGS, DEFAULT_PREFS)

cfg = read_json(SETTINGS, default=DEFAULT_PREFS)

st.title("見た目と応援（ポップ設定）")

# -----------------------------
# カラーテーマ
# -----------------------------
st.subheader("テーマカラー")
cfg["theme_color"] = st.selectbox(
    "テーマカラーを選んでください",
    ["pink", "blue", "green", "orange"],
    index=["pink", "blue", "green", "orange"].index(cfg.get("theme_color", "pink"))
)

# -----------------------------
# 応援バブル
# -----------------------------
st.subheader("応援バブル")
cfg["show_bubble"] = st.toggle(
    "AIの応援バブルを表示する",
    value=cfg.get("show_bubble", True)
)

# -----------------------------
# 声の種類
# -----------------------------
st.subheader("声のタイプ")
cfg["voice_type"] = st.radio(
    "声の種類",
    ["normal", "cute", "cool"],
    index=["normal", "cute", "cool"].index(cfg.get("voice_type", "normal"))
)

# -----------------------------
# 保存
# -----------------------------
if st.button("設定を保存する 💾"):
    write_json(SETTINGS, cfg)
    st.success("保存しました！")

if cfg.get("show_bubble", True):
    bubble("今日も一歩ずつ進んでいこうね、ご主人！")
