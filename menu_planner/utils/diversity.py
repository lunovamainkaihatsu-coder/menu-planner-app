# --- bootstrap ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------

import re
from collections import Counter, defaultdict
from typing import List, Dict, Any

PROTEIN_KEYWORDS = {
    "鶏": ["鶏","鶏もも","鶏むね","ささみ","チキン"],
    "豚": ["豚","豚こま","豚バラ","豚ロース"],
    "牛": ["牛","牛こま","合い挽き","牛薄切り"],
    "魚": ["鮭","サーモン","鯖","サバ","タラ","アジ","イワシ","マグロ","カツオ","白身魚","さんま","ブリ"],
    "大豆": ["豆腐","大豆","納豆","おから","油揚げ"],
    "卵": ["卵","玉子"],
    "海老/甲殻": ["海老","エビ","むきえび","芝えび"],
}

CUISINE_KEYWORDS = {
    "和風": ["味噌","しょうゆ","だし","和風","昆布","鰹節","みりん","和風だし"],
    "中華": ["オイスター","豆板醤","甜麺醤","花椒","紹興酒","中華だし","ごま油"],
    "洋風": ["オリーブオイル","バター","コンソメ","トマト缶","パスタ","チーズ","ハーブ"],
    "韓国": ["コチュジャン","ごま油","キムチ","コムタンスープ"],
    "エスニック": ["ナンプラー","パクチー","ココナッツ","カレー粉","ターメリック","スパイス"],
}

COOKING_KEYWORDS = {
    "炒め": ["炒め","ソテー"," stir "],
    "煮": ["煮","煮物","煮込み"," braise "],
    "焼き": ["焼き","グリル","ロースト","オーブン"],
    "揚げ": ["揚げ","フライ","唐揚げ","天ぷら"],
    "和え": ["和え","マリネ","サラダ"],
    "蒸し": ["蒸し","スチーム"],
}

def _normalize(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^\wぁ-んァ-ン一-龥]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def _bag_of_words(rec: Dict[str,Any]) -> Counter:
    words = []
    words += _normalize(rec.get("name","")).split()
    for ing in rec.get("ingredients",[]):
        words += _normalize(ing.get("name","")).split()
    for s in rec.get("steps",[]):
        words += _normalize(s).split()
    return Counter(words)

def jaccard(a: Counter, b: Counter) -> float:
    sa = set(a.keys()); sb = set(b.keys())
    if not sa or not sb: return 0.0
    return len(sa & sb) / len(sa | sb)

def detect_tags(rec: Dict[str,Any]) -> Dict[str,str]:
    text = " ".join([
        rec.get("name",""),
        " ".join([i.get("name","") for i in rec.get("ingredients",[])]),
        " ".join(rec.get("steps",[]))
    ])
    tags = {}
    for k, arr in PROTEIN_KEYWORDS.items():
        if any(x in text for x in arr): tags["protein"] = k; break
    for k, arr in CUISINE_KEYWORDS.items():
        if any(x in text for x in arr): tags.setdefault("cuisine", k)
    for k, arr in COOKING_KEYWORDS.items():
        if any(x in text for x in arr): tags.setdefault("method", k)
    return tags

def select_diverse(recipes: List[Dict[str,Any]], k: int = 21,
                   jaccard_threshold: float = 0.28,
                   max_per_protein: int = 6,
                   need_types: List[str] = None) -> List[Dict[str,Any]]:
    """
    似すぎ料理の連発を抑えつつ k 件を選ぶ簡易貪欲法。
    - ingredients/steps/name の BoW でジャッカード類似度を計算して弾く
    - たんぱく質カテゴリの上限（max_per_protein）を設定
    - 一汁三菜など type バランス（主菜/副菜/汁物）も満たす
    """
    if need_types is None:
        need_types = []

    bows = [(_bag_of_words(r), r) for r in recipes]
    chosen = []
    protein_count = defaultdict(int)

    def ok_with_constraints(r):
        tags = detect_tags(r)
        prot = tags.get("protein","その他")
        if protein_count[prot] >= max_per_protein: 
            return False
        # 類似度
        rb = _bag_of_words(r)
        for cbow, cr in chosen:
            if jaccard(rbow := rb, cbow) >= jaccard_threshold:
                return False
        # typeバランス（必要タイプがあれば優先）
        if need_types:
            rt = r.get("type",[])
            if not any(t in rt for t in need_types):
                return False
        return True

    # 主→副→汁の順で拾っていく軽量アルゴ
    priority = ["主菜","副菜","汁物","魚","麺","作り置き","主食"]
    sorted_recipes = sorted(recipes, key=lambda r: (
        priority.index(r["type"][0]) if r.get("type") and r["type"][0] in priority else 99,
        r.get("time_min", 30),
        r.get("cost_level", 2)
    ))

    for r in sorted_recipes:
        if len(chosen) >= k: break
        if not ok_with_constraints(r): 
            continue
        chosen.append((_bag_of_words(r), r))
        prot = detect_tags(r).get("protein","その他")
        protein_count[prot] += 1

    return [r for _, r in chosen]
