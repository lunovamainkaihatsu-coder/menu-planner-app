# --- bootstrap ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
# ------------------
import streamlit as st
from common.style import inject_css, card, endcard, bubble
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image

inject_css()

DATA = data_dir()
GOALS = DATA / "goals.json"

defaults = {"fish":2, "soup":4, "prep":1}  # prep=作り置き
g = read_json(GOALS, default=defaults.copy())

st.title("週の目標")
col1,col2,col3 = st.columns(3)
with col1: g["fish"] = st.number_input("魚料理（回/週）", 0, 21, g.get("fish",2))
with col2: g["soup"] = st.number_input("汁物（回/週）", 0, 21, g.get("soup",4))
with col3: g["prep"] = st.number_input("作り置き（回/週）", 0, 21, g.get("prep",1))
if st.button("保存", type="primary"):
    write_json(GOALS, g); st.success("保存しました ✅")
st.caption("※ 種類判定はレシピのtypeに『魚』『汁物』『作り置き』などが含まれるとカウント。")
