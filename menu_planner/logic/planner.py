from typing import List, Dict
from collections import defaultdict
import random, itertools
from src.menu_planner.logic.scorer import (
    dislike_penalty, budget_weight, stock_bonus,
    contains_allergen, type_summary, preference_bonus
)
from src.menu_planner.logic.rules import weekly_penalty
from src.common.pathkit import data_dir
from src.common.fileio import read_json

DAYS  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
TIMES = ["breakfast","lunch","dinner"]

def _score_pool(recipes: List[Dict], settings: Dict, pantry: Dict):
    # ユーザー好み
    DATA = data_dir()
    PREF = read_json(DATA / "user_prefs.json", default={"likes":{}, "favorites":[]})

    allergies = settings.get("allergies",[])
    dislikes  = settings.get("dislikes",{})
    budget    = settings.get("budget_mode","いつもどおり")
    leftover  = settings.get("leftover_priority", True)
    pool = []
    for r in recipes:
        if contains_allergen(r.get("contains",[]), allergies):
            continue
        score = 1.0
        score *= budget_weight(budget, int(r.get("cost_level",2)))
        score += stock_bonus(r.get("ingredients",[]), pantry, leftover)
        score -= dislike_penalty(r.get("ingredients",[]), dislikes)
        if "汁物" in r.get("type",[]): score += 0.3
        # 好み加点
        score += preference_bonus(r.get("name",""), PREF)
        pool.append((score, r))
    pool.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in pool]

def _pick(pool, typename=None, last_name=None):
    it = (r for r in pool if typename in (r.get("type",[]) or [])) if typename else iter(pool)
    for r in it:
        if r["name"] != last_name:
            return r
    return pool[0] if pool else None

def plan_week(recipes: List[Dict], settings: Dict, pantry: Dict) -> Dict:
    pool = _score_pool(recipes, settings, pantry)
    week = {d: {t: {"main":"-","side":"-","soup":"-","dessert":"-"} for t in TIMES} for d in DAYS}
    if not pool: return week

    cycler = itertools.cycle(pool)
    last_b = last_l = None
    for d in DAYS:
        b = next(cycler); l = next(cycler)
        if b["name"] == last_b: b = next(cycler)
        if l["name"] == last_l: l = next(cycler)
        week[d]["breakfast"]["main"] = b["name"]; last_b = b["name"]
        week[d]["lunch"]["main"]     = l["name"]; last_l = l["name"]

    week_type_summary = defaultdict(int)
    last_main = last_side = last_soup = None
    for d in DAYS:
        main = _pick(pool, "主菜", last_main) or _pick(pool, "魚", last_main)
        side = _pick(pool, "副菜", last_side)
        soup = _pick(pool, "汁物", last_soup)
        week[d]["dinner"] = {
            "main": main["name"] if main else "-",
            "side": side["name"] if side else "-",
            "soup": soup["name"] if soup else "-",
            "dessert": "-"
        }
        last_main = week[d]["dinner"]["main"]
        last_side = week[d]["dinner"]["side"]
        last_soup = week[d]["dinner"]["soup"]
        for k,v in type_summary(["汁物"]).items(): week_type_summary[k]+=v

    rules = settings.get("rules",{})
    if weekly_penalty(week_type_summary, rules) >= 3 and len(pool)>1:
        d1,d2 = random.sample(DAYS,2)
        week[d1]["dinner"]["main"], week[d2]["dinner"]["main"] = week[d2]["dinner"]["main"], week[d1]["dinner"]["main"]
    return week
