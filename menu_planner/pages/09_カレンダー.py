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

import pandas as pd
from datetime import date
inject_css()

DATA = data_dir()
WEEK  = DATA / "week_plan.json"
LOCKS = DATA / "plan_locks.json"
DONE  = DATA / "done_today.json"
RECIPES = DATA / "recipes.json"
GOALS = DATA / "goals.json"

st.title("カレンダー（週ビュー）")

week  = read_json(WEEK,  default={"week_of":str(date.today()), "plan":{}})
locks = read_json(LOCKS, default={})
done  = read_json(DONE,  default={})
recipes = {r["name"]: r for r in read_json(RECIPES, default={"recipes":[]}).get("recipes",[])}
goals   = read_json(GOALS, default={"fish":2,"soup":4,"prep":1})

jpD = {"Mon":"月","Tue":"火","Wed":"水","Thu":"木","Fri":"金","Sat":"土","Sun":"日"}
DAYS= ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
JP_T= {"breakfast":"朝","lunch":"昼","dinner":"夜"}
COLS= ["main","side","soup","dessert"]

# --- 進捗カウント ---
cnt = {"fish":0,"soup":0,"prep":0}
def bump(name):
    r = recipes.get(name); 
    if not r: return
    types = r.get("type",[]) or []
    if "魚" in types: cnt["fish"] += 1
    if "汁物" in types: cnt["soup"] += 1
    if "作り置き" in types: cnt["prep"] += 1

for d in DAYS:
    for t in ["breakfast","lunch","dinner"]:
        cell = week.get("plan",{}).get(d,{}).get(t,{})
        if isinstance(cell, str): bump(cell)
        elif isinstance(cell, dict):
            for c in COLS:
                n = cell.get(c)
                if n and n != "-": bump(n)

# --- 目標カード ---
st.subheader("今週の目標と進捗")
c1,c2,c3 = st.columns(3)
with c1:
    st.markdown(f"**🐟 魚料理**  \n<small>{cnt['fish']} / {goals.get('fish',0)}</small>", unsafe_allow_html=True)
    st.progress(min(1.0, cnt["fish"]/max(1,goals.get("fish",1))))
with c2:
    st.markdown(f"**🥣 汁物**  \n<small>{cnt['soup']} / {goals.get('soup',0)}</small>", unsafe_allow_html=True)
    st.progress(min(1.0, cnt["soup"]/max(1,goals.get("soup",1))))
with c3:
    st.markdown(f"**🧺 作り置き**  \n<small>{cnt['prep']} / {goals.get('prep',0)}</small>", unsafe_allow_html=True)
    st.progress(min(1.0, cnt["prep"]/max(1,goals.get("prep",1))))

st.caption("✓：確定、~~打消し~~：今日の完成チェック反映")

# --- 週テーブル ---
for t in ["breakfast","lunch","dinner"]:
    rows=[]
    for d in DAYS:
        slot = week.get("plan",{}).get(d,{})
        cell = slot.get(t, {})
        if isinstance(cell, str):
            cell = {"main":cell, "side":"-","soup":"-","dessert":"-"}
        row = {"曜日": jpD[d]}
        for c in COLS:
            name = cell.get(c,"-")
            key  = f"{d}.{t}.{c}"
            mark = "✓ " if locks.get(key, False) else ""
            today_flag = (d == DAYS[date.today().weekday()])
            if today_flag and done.get(name, False):
                name = f"~~{name}~~"
            row[c] = f"{mark}{name}"
        rows.append(row)
    st.markdown(f"### {JP_T[t]}")
    st.table(pd.DataFrame(rows, columns=["曜日"]+COLS))
