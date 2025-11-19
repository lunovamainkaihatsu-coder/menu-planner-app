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

from collections import defaultdict
from datetime import date

DATA = data_dir()
WEEK    = DATA / "week_plan.json"
RECIPES = DATA / "recipes.json"
PANTRY  = DATA / "pantry.json"
STATE   = DATA / "shopping_state.json"  # {"unnecessary":[], "purchased":[]}

st.title("買い物リスト")

week    = read_json(WEEK, default={"week_of":str(date.today()), "plan":{}})
recipes = {r["name"]: r for r in read_json(RECIPES, default={"recipes":[]}).get("recipes",[])}
pantry  = read_json(PANTRY, default={"items":[]})
state   = read_json(STATE, default={"unnecessary":[], "purchased":[]})

def meal_names(slot_value):
    if isinstance(slot_value, str): return [slot_value]
    if isinstance(slot_value, dict):
        out=[]; 
        for k in ["main","side","soup","dessert","side1","side2","staple"]:
            v = slot_value.get(k)
            if isinstance(v,str) and v.strip(): out.append(v.strip())
        return out
    return []

def categorize(name:str) -> str:
    n = name.lower()
    if any(x in n for x in ["ねぎ","にんじん","大根","玉ねぎ","じゃが","ほうれん草","キャベツ","ごぼう","もやし","ピーマン","トマト","きゅうり","白菜","なす","きのこ"]): return "野菜"
    if any(x in n for x in ["鶏","豚","牛","ひき肉","ベーコン","ハム"]): return "肉"
    if any(x in n for x in ["さば","鮭","サーモン","しらす","いわし","魚"]): return "魚介"
    if any(x in n for x in ["豆腐","納豆","油揚げ","厚揚げ"]): return "大豆製品"
    if any(x in n for x in ["牛乳","ヨーグルト","チーズ","バター"]): return "乳製品"
    if any(x in n for x in ["醤油","みりん","酒","砂糖","塩","味噌","ソース","酢","ごま油","油","塩麹"]): return "調味料"
    if any(x in n for x in ["米","ご飯","パン","うどん","そば","パスタ","スパゲッティ","麺"]): return "主食・麺"
    if any(x in n for x in ["海苔","ひじき","わかめ","昆布"]): return "乾物"
    return "その他"

def collect_need(plan_dict):
    need = defaultdict(float)  # key=(name,unit) -> qty
    for d, slots in plan_dict.items():
        for t, val in slots.items():
            for rname in meal_names(val):
                r = recipes.get(rname)
                if not r: 
                    continue
                for ing in r.get("ingredients", []):
                    key = (ing["name"], ing["unit"])
                    need[key] += float(ing["qty"])
    stock = {i["name"]: i for i in pantry.get("items",[])}
    for (n,u) in list(need.keys()):
        have = float(stock.get(n, {}).get("qty", 0))
        need[(n,u)] = max(need[(n,u)] - have, 0.0)
        if need[(n,u)] == 0: need.pop((n,u))
    return need

need_all = collect_need(week.get("plan",{}))

def render_list(title, need_dict, key_prefix):
    st.subheader(title)
    if not need_dict:
        st.success("不足はありません 🎉"); return
    buckets = defaultdict(list)
    for (n,u), q in need_dict.items():
        buckets[categorize(n)].append(((n,u), q))
    removed = set(state.get("unnecessary", []))
    purchased = set(state.get("purchased", []))

    for cat in sorted(buckets.keys()):
        with st.expander(cat, expanded=True):
            for (n,u), q in sorted(buckets[cat], key=lambda x: x[0][0]):
                item_id = f"{key_prefix}:{n}:{u}"
                if item_id in removed:
                    continue
                cols = st.columns([6,2,2,2])
                with cols[0]:
                    st.write(f"{n} … {q}{u}")
                with cols[1]:
                    rm = st.checkbox("不要", key=f"rm_{item_id}", value=(item_id in removed))
                    if rm: removed.add(item_id)
                    else:  removed.discard(item_id)
                with cols[2]:
                    buy = st.checkbox("購入", key=f"buy_{item_id}", value=(item_id in purchased))
                    if buy: purchased.add(item_id)
                    else:   purchased.discard(item_id)
                with cols[3]:
                    st.caption(f"#{categorize(n)}")
    state["unnecessary"] = list(removed)
    state["purchased"]   = list(purchased)
    write_json(STATE, state)

render_list("週まとめの買い物リスト", need_all, "WEEK")

if st.button("購入完了（購入チェックの項目を消去）", type="primary"):
    state["purchased"] = []
    write_json(STATE, state)
    st.success("購入済み項目をクリアしました")

st.divider()

jp = {"Mon":"月","Tue":"火","Wed":"水","Thu":"木","Fri":"金","Sat":"土","Sun":"日"}
for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]:
    subplan = {d: week.get("plan",{}).get(d, {})}
    need_day = collect_need(subplan)
    render_list(f"{jp[d]}曜日の買い物リスト", need_day, f"DAY-{d}")
