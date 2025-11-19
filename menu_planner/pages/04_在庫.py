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

from datetime import date
inject_css()

DATA = data_dir()
ASSETS = assets_dir()
PANTRY = DATA / "pantry.json"

st.title("在庫管理（冷蔵庫/パントリー）")

db = read_json(PANTRY, default={"items":[]})

st.subheader("追加")
name = st.text_input("品名", "")
col1,col2,col3 = st.columns(3)
with col1: qty = st.number_input("数量", 0.0, 9999.0, 1.0, step=1.0)
with col2: unit = st.text_input("単位", "個")
with col3: expires = st.date_input("消費/賞味期限", value=date.today()).isoformat()

photo_file = st.file_uploader("写真（任意）", type=["jpg","jpeg","png"])
photo_path = None
if photo_file:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "pantry").mkdir(parents=True, exist_ok=True)
    photo_path = ASSETS / "pantry" / f"{date.today().isoformat()}_{name}.jpg"
    photo_path.write_bytes(photo_file.getvalue())
    st.image(str(photo_path), width=200)

if st.button("在庫に追加", type="primary"):
    item = {"name":name, "qty":qty, "unit":unit, "expires":expires}
    if photo_path: item["photo"] = str(photo_path)
    db["items"].append(item)
    write_json(PANTRY, db)
    st.success("追加しました")

st.subheader("一覧")
if db["items"]:
    for i, it in enumerate(db["items"]):
        with st.expander(f"{i+1}. {it['name']} ({it['qty']}{it['unit']}) / {it.get('expires','-')}"):
            colA,colB,colC = st.columns(3)
            with colA: new_qty = st.number_input("数量", 0.0, 9999.0, it["qty"], key=f"qty_{i}")
            with colB: new_unit = st.text_input("単位", it["unit"], key=f"unit_{i}")
            with colC: new_exp = st.text_input("期限(YYYY-MM-DD)", it.get("expires",""), key=f"exp_{i}")
            if st.button("更新", key=f"upd_{i}"):
                it["qty"], it["unit"], it["expires"] = new_qty, new_unit, new_exp
                write_json(PANTRY, db); st.success("更新しました")
            if st.button("削除", key=f"del_{i}"):
                db["items"].pop(i); write_json(PANTRY, db); st.success("削除しました"); st.rerun()
else:
    st.info("在庫がありません。上で追加してね。")
