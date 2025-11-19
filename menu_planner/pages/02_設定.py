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

from pathlib import Path
inject_css()

DATA = data_dir()
SETTINGS = DATA / "settings.json"

DEFAULTS = {
    "budget_mode": "いつもどおり",
    "leftover_priority": True,
    "allergies": [],
    "dislikes": {},
    "rules": {"noodle_per_week_max": 2, "soup_per_week_min": 4, "fried_per_week_max": 1, "fish_per_week_min": 2}
}

DATA.mkdir(parents=True, exist_ok=True)
if not SETTINGS.exists():
    write_json(SETTINGS, DEFAULTS)

st.title("設定")
cfg = read_json(SETTINGS, default=DEFAULTS)

st.subheader("予算モード")
cfg["budget_mode"] = st.radio("週の雰囲気", ["節約","いつもどおり","ちょっと豪勢"],
    index=["節約","いつもどおり","ちょっと豪勢"].index(cfg.get("budget_mode","いつもどおり")))

st.subheader("残り優先")
cfg["leftover_priority"] = st.toggle("期限が近い在庫を優先的に使う", value=cfg.get("leftover_priority",True))

st.subheader("アレルギー（絶対NG）")
colA, colB = st.columns([3,1])
with colA:
    add = st.text_input("食材名を追加", "")
with colB:
    if st.button("追加"):
        if add and add not in cfg["allergies"]:
            cfg["allergies"].append(add)
if st.button("全クリア", help="リストを空にします"):
    cfg["allergies"] = []
st.write("現在：", ", ".join(cfg["allergies"]) or "なし")

st.subheader("苦手食材（0=平気, 3=ほぼ無理）")
col1,col2,col3 = st.columns([2,2,1])
with col1:
    n = st.text_input("食材名", "")
with col2:
    lv = st.slider("苦手レベル", 0, 3, 2)
with col3:
    if st.button("登録/更新"):
        if n:
            cfg["dislikes"][n] = lv
if cfg["dislikes"]:
    st.table([{"食材":k,"レベル":v} for k,v in cfg["dislikes"].items()])

st.subheader("ルール")
cfg["rules"]["noodle_per_week_max"] = st.number_input("麺の回数 上限/週", 0, 21, cfg["rules"].get("noodle_per_week_max",2))
cfg["rules"]["soup_per_week_min"]   = st.number_input("汁物の回数 下限/週", 0, 21, cfg["rules"].get("soup_per_week_min",4))
cfg["rules"]["fried_per_week_max"]  = st.number_input("揚げ物の回数 上限/週", 0, 21, cfg["rules"].get("fried_per_week_max",1))
cfg["rules"]["fish_per_week_min"]   = st.number_input("魚料理の回数 下限/週", 0, 21, cfg["rules"].get("fish_per_week_min",2))

if st.button("保存", type="primary", use_container_width=True):
    write_json(SETTINGS, cfg)
    st.success("保存しました ✅")
