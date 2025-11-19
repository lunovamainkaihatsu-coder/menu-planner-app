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

from datetime import date, datetime
inject_css()

PHOTOS = assets_dir() / "meals"

st.title("写真ログ（サクッと保存）")
d = st.date_input("日付", value=date.today())
slot = st.selectbox("時間帯", ["朝","昼","夜"])
up = st.file_uploader("写真", type=["png","jpg","jpeg"])
if up and st.button("保存", type="primary"):
    PHOTOS.mkdir(parents=True, exist_ok=True)
    fn = PHOTOS / f"{d}_{slot}_{datetime.now().strftime('%H%M%S')}.jpg"
    fn.write_bytes(up.getvalue())
    st.success(f"保存しました：{fn.name}")
    st.image(str(fn), use_column_width=True)
