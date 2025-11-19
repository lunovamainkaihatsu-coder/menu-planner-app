from typing import Dict, List
from src.menu_planner.logic.inventory import near_expiry_score

def dislike_penalty(ingredients: List[Dict], dislikes: Dict[str,int]) -> float:
    return sum(dislikes.get(ing["name"], 0) * 0.5 for ing in ingredients)

def budget_weight(mode: str, cost_level: int) -> float:
    if mode == "節約":
        return {1:1.5,2:1.0,3:0.2}.get(cost_level,1.0)
    if mode == "ちょっと豪勢":
        return {1:0.5,2:1.0,3:1.5}.get(cost_level,1.0)
    return {1:1.0,2:1.2,3:1.0}.get(cost_level,1.0)

def stock_bonus(ingredients: List[Dict], pantry: dict, leftover_priority: bool) -> float:
    if not leftover_priority: return 0.0
    bonus = 0.0
    index = {i["name"]: i for i in pantry.get("items",[])}
    for ing in ingredients:
        if ing["name"] in index:
            bonus += 0.2 + near_expiry_score(index[ing["name"]].get("expires"))*0.2
    return bonus

def contains_allergen(contains: List[str], allergies: List[str]) -> bool:
    return any(a in (contains or []) for a in allergies)

def type_summary(typelist: List[str]) -> dict:
    sm = {"麺":0,"汁物":0,"魚":0,"揚げ物":0}
    for t in typelist:
        if t in sm: sm[t]+=1
    return sm

def preference_bonus(recipe_name: str, prefs: Dict) -> float:
    """
    ユーザー好みの加点。
    - お気に入り: +1.2
    - いいね(回数): 1回あたり +0.1（上限+0.8）
    """
    if not prefs: return 0.0
    bonus = 0.0
    favs = set(prefs.get("favorites", []))
    likes = prefs.get("likes", {})
    if recipe_name in favs:
        bonus += 1.2
    if recipe_name in likes:
        bonus += min(0.8, 0.1 * float(likes.get(recipe_name, 0)))
    return bonus
