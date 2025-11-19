import random, datetime
from pathlib import Path
from .fileio import read_json, write_json
from .pathkit import data_dir, assets_dir

PREF_PATH = data_dir() / "ui_prefs.json"
ASSETS    = assets_dir()

DEFAULT_PREFS = {
  "pop_mode": True,
  "mascot_name": "ルナ",
  "show_random_food": True,
  "encourage_level": "ふつう"  # ひかえめ / ふつう / がっつり
}

MESSAGES = {
  "ひかえめ": [
    "今日もゆるっといこう〜🍳", "あと一歩！水分とってね🫧", "困ったら味噌汁が味方だよ🥣"
  ],
  "ふつう": [
    "ナイス一歩！今ある食材で“おいしい”作ろう✨",
    "レンチンでも愛情は伝わるよ〜📣", "味つけ迷ったら“甘み1・塩分1・酸味0.5”で整う！"
  ],
  "がっつり": [
    "偉い！ここまで来たら勝ち確だよ🔥", "今日は“手を抜く勇気”も100点！", "作ったあなたが一番えらい！👑"
  ]
}

def prefs():
    p = read_json(PREF_PATH, default=DEFAULT_PREFS.copy())
    # 初期ファイル生成
    if not PREF_PATH.exists(): write_json(PREF_PATH, p)
    return p

def pick_message():
    p = prefs()
    level = p.get("encourage_level","ふつう")
    msg = random.choice(MESSAGES.get(level, MESSAGES["ふつう"]))
    name = p.get("mascot_name","ルナ")
    return f"{name}「{msg}」"

def pick_random_food_image():
    """assets/menu_planner/stock_foods の中からランダム画像Pathを返す。無ければNone"""
    folder = ASSETS / "stock_foods"
    if not folder.exists(): return None
    cands = [p for p in folder.iterdir() if p.suffix.lower() in [".jpg",".jpeg",".png",".webp"]]
    if not cands: return None
    return random.choice(cands)
