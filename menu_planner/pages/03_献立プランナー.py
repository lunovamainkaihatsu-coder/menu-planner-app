# --- bootstrap (import path fix) ---
import sys, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# -----------------------------------

import datetime as dt
import streamlit as st
from common.style import inject_css, card, endcard, bubble
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image

from copy import deepcopy


inject_css()

DATA = data_dir()
RECIPES_FILE   = DATA / "recipes.json"
SETTINGS_FILE  = DATA / "settings.json"
PLAN_FILE      = DATA / "weekly_plan.json"
SHOPPING_FILE  = DATA / "shopping_list.json"

# --------- 定数とユーティリティ ---------
MEALS = ["朝", "昼", "夜"]
CATEGORIES = ["メイン", "副菜", "汁物", "デザート"]
CATEGORY_TO_TYPES = {
    "メイン": ["主菜", "魚", "麺"],
    "副菜": ["副菜", "作り置き"],
    "汁物": ["汁物"],
    "デザート": ["主食", "副菜", "作り置き"],
}

def monday_of(date: dt.date) -> dt.date:
    return date - dt.timedelta(days=date.weekday())

def daterange(start: dt.date, days: int = 7):
    for i in range(days):
        yield start + dt.timedelta(days=i)

def today_tokyo():
    return dt.date.today()

def _ensure_plan_structure(plan: dict, week_start: dt.date) -> dict:
    s = week_start.isoformat()
    if "weeks" not in plan:
        plan["weeks"] = {}
    if s not in plan["weeks"]:
        plan["weeks"][s] = {}
    week = plan["weeks"][s]
    for d in daterange(week_start, 7):
        key = d.isoformat()
        if key not in week:
            week[key] = {}
        for meal in MEALS:
            if meal not in week[key]:
                week[key][meal] = {}
            for cat in CATEGORIES:
                if cat not in week[key][meal]:
                    week[key][meal][cat] = {"recipe_id": None, "confirmed": False}
    return plan

def _recipes_db():
    db = read_json(RECIPES_FILE, default={"recipes":[]})
    return db.get("recipes", [])

def _pick_recipe(recipes, types, avoid_ids=None):
    avoid_ids = set(avoid_ids or [])
    pool = [r for r in recipes if any(t in (r.get("type") or []) for t in types)]
    if not pool:
        return None
    pool_unused = [r for r in pool if r.get("recipe_id") not in avoid_ids]
    chosen_pool = pool_unused or pool
    return random.choice(chosen_pool)

def _collect_used_ids(week_block):
    used = []
    for day, meals in week_block.items():
        for meal, cats in meals.items():
            for cat, cell in cats.items():
                rid = cell.get("recipe_id")
                if rid:
                    used.append(rid)
    return used

def _recipe_by_id(recipes, rid):
    for r in recipes:
        if r.get("recipe_id") == rid:
            return r
    return None

def _weekday_label(d: dt.date):
    w = "月火水木金土日"[d.weekday()]
    return f"{d.month}/{d.day}（{w}）"

def _categorize_ingredient(name: str):
    n = name
    keys = {
        "野菜": ["ねぎ","玉ねぎ","キャベツ","にんじん","大根","なす","ピーマン","じゃがいも","トマト","ほうれん草","小松菜","白菜","もやし","きゅうり","ごぼう","れんこん","ブロッコリー"],
        "肉": ["豚","牛","鶏","ベーコン","ハム","ソーセージ"],
        "魚": ["鮭","サーモン","鯖","タラ","アジ","イワシ","マグロ","カツオ","白身魚","エビ","カニ"],
        "大豆/乳/卵": ["豆腐","油揚げ","納豆","牛乳","チーズ","卵","ヨーグルト"],
        "主食": ["米","ご飯","パン","うどん","そば","パスタ","麺","小麦粉"],
        "調味料": ["塩","砂糖","醤油","味噌","酒","みりん","酢","胡椒","コンソメ","だし","ごま油"],
        "その他": []
    }
    for cat, words in keys.items():
        if any(w in n for w in words):
            return cat
    return "その他"

def _add_to_shopping(bucket, name, qty, unit):
    cat = _categorize_ingredient(name or "")
    bucket.setdefault(cat, {})
    key = f"{name}".strip()
    if key in bucket[cat]:
        prev = bucket[cat][key]
        if prev["unit"] == unit and isinstance(prev["qty"], (int, float)) and isinstance(qty, (int, float)):
            prev["qty"] += qty
        else:
            prev["note"] = (prev.get("note","") + f" / +{qty}{unit}").strip(" /")
    else:
        try:
            q = float(qty)
        except Exception:
            q = qty
        bucket[cat][key] = {"qty": q, "unit": unit}

# --------- ページ UI ---------
st.title("週の献立プランナー 📅（一汁三菜）")

recipes = _recipes_db()
settings = read_json(SETTINGS_FILE, default={"budget_mode":"いつもどおり"})
budget = settings.get("budget_mode","いつもどおり")

col0, col1, col2, col3 = st.columns([1,1,1,2])
with col0:
    base_date = st.date_input("週の開始日（任意の月曜推奨）", value=monday_of(today_tokyo()))
with col1:
    use_stock = st.toggle("在庫優先", value=True)
with col2:
    intensity = st.selectbox("予算", ["節約","いつもどおり","ちょっと豪勢"], index=["節約","いつもどおり","ちょっと豪勢"].index(budget) if budget in ["節約","いつもどおり","ちょっと豪勢"] else 1)
with col3:
    regen_mode = st.selectbox("再生成", ["未確定のみ","すべて"])

week_start = monday_of(base_date)
plan = read_json(PLAN_FILE, default={})
plan = _ensure_plan_structure(plan, week_start)
week_block = plan["weeks"][week_start.isoformat()]

card("候補の生成 / 入れ替え")
if st.button("この週の献立を提案する（AIなし・DBから多様に）", type="primary"):
    used = set(_collect_used_ids(week_block))
    for d in daterange(week_start, 7):
        dkey = d.isoformat()
        for meal in MEALS:
            for cat in CATEGORIES:
                cell = week_block[dkey][meal][cat]
                if regen_mode == "未確定のみ" and cell.get("confirmed"):
                    continue
                r = _pick_recipe(recipes, CATEGORY_TO_TYPES[cat], avoid_ids=used)
                if r:
                    rid = r.get("recipe_id")
                    used.add(rid)
                    week_block[dkey][meal][cat] = {"recipe_id": rid, "confirmed": False}
    write_json(PLAN_FILE, plan)
    st.success("候補を更新しました！")
endcard()

if "open_recipe_obj" not in st.session_state:
    st.session_state.open_recipe_obj = None

for the_day in daterange(week_start, 7):
    dkey = the_day.isoformat()
    pretty = _weekday_label(the_day)

    card(f"{pretty} の献立")
    for meal in MEALS:
        st.markdown(f"### {meal}")
        cols = st.columns(4)
        for idx, cat in enumerate(CATEGORIES):
            cell = week_block[dkey][meal][cat]
            rid = cell.get("recipe_id")
            recipe = _recipe_by_id(recipes, rid) if rid else None

            with cols[idx]:
                st.markdown(f"**{cat}**")
                if recipe:
                    tags_html = "".join([f"<span class='chip'>{t}</span>" for t in (recipe.get("type") or [])])
                    st.markdown(
                        f"{recipe.get('name','（名称未定）')}  \n"
                        f"<span class='chip'>{recipe.get('time_min','?')}分</span> {tags_html}",
                        unsafe_allow_html=True
                    )
                else:
                    st.caption("候補なし（再生成で提案）")

                confirmed_key = f"chk_{dkey}_{meal}_{cat}"
                new_conf = st.checkbox("作れた！", value=bool(cell.get("confirmed")), key=confirmed_key)
                week_block[dkey][meal][cat]["confirmed"] = new_conf

                colA, colB = st.columns(2)
                with colA:
                    if st.button("🔁 候補を変える", key=f"swap_{dkey}_{meal}_{cat}"):
                        used_now = set(_collect_used_ids(week_block))
                        r = _pick_recipe(recipes, CATEGORY_TO_TYPES[cat], avoid_ids=used_now - {rid})
                        if r:
                            week_block[dkey][meal][cat] = {"recipe_id": r.get("recipe_id"), "confirmed": False}
                            write_json(PLAN_FILE, plan)
                            st.experimental_rerun()
                        else:
                            st.warning("該当タイプのレシピが不足しています。")
                with colB:
                    if recipe and st.button("📄 レシピ", key=f"show_{dkey}_{meal}_{cat}"):
                        st.session_state.open_recipe_obj = deepcopy(recipe)

    endcard()

card("保存とリスト更新")
c1, c2 = st.columns([1,1])
with c1:
    if st.button("確定だけカレンダーに保存", type="primary"):
        write_json(PLAN_FILE, plan)
        st.success("保存しました！")
with c2:
    if st.button("買い物リストを更新 🛒", type="primary"):
        bucket = {}
        for d in daterange(week_start, 7):
            dkey = d.isoformat()
            for meal in MEALS:
                for cat in CATEGORIES:
                    cell = week_block[dkey][meal][cat]
                    if not cell.get("confirmed"):
                        continue
                    rid = cell.get("recipe_id")
                    r = _recipe_by_id(recipes, rid) if rid else None
                    if not r:
                        continue
                    for ing in (r.get("ingredients") or []):
                        _add_to_shopping(bucket, ing.get("name",""), ing.get("qty",0), ing.get("unit",""))
        write_json(SHOPPING_FILE, {"updated_at": dt.datetime.now().isoformat(), "items": bucket})
        st.success("買い物リストを更新しました！")
endcard()

if st.session_state.open_recipe_obj:
    recipe_drawer(st.session_state.open_recipe_obj)
