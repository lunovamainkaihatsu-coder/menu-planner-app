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

DATA   = data_dir()
ASSETS = assets_dir()
RECIPES= DATA / "recipes.json"
SET    = DATA / "settings.json"
PAN    = DATA / "pantry.json"

st.title("AIレシピ生成（条件に合った献立を量産）")

# 現在の設定・在庫
settings = read_json(SET, default={
    "budget_mode":"いつもどおり","leftover_priority":True,"allergies":[], "dislikes":{}, "rules": {}
})
pantry   = read_json(PAN, default={"items":[]})

# 入力UI
st.subheader("生成条件")
col1,col2,col3 = st.columns(3)
with col1:
    count = st.number_input("作成件数", 1, 20, 6)
    max_time = st.number_input("調理時間の上限（分）", 5, 120, 25)
with col2:
    course = st.multiselect("種類（複数可）", ["主菜","副菜","汁物","魚","麺","作り置き","主食"], default=["主菜","副菜","汁物"])
    region = st.selectbox("テイスト", ["和風","中華","洋風","韓国","エスニック","なんでも"], index=0)
with col3:
    use_pantry = st.toggle("在庫を優先して使う", value=True)
    gen_images = st.toggle("AIでイメージ画像も作成", value=False)

avoid_allergens = settings.get("allergies",[])
dislikes = settings.get("dislikes",{})
budget = settings.get("budget_mode","いつもどおり")

# 在庫ヒント
stock_list = []
if use_pantry:
    for it in pantry.get("items",[]):
        if it.get("name"): stock_list.append(it["name"])

st.caption(
    "アレルギー回避: " + (", ".join(avoid_allergens) or "なし")
    + " / 苦手(Lv2+)回避: " + (", ".join([k for k,v in dislikes.items() if v>=2]) or "なし")
)

def validate_recipe(r:dict)->bool:
    try:
        return all([
            isinstance(r.get("name"), str) and len(r["name"])>0,
            isinstance(r.get("ingredients"), list) and len(r["ingredients"])>=2,
            isinstance(r.get("steps"), list) and len(r["steps"])>=2,
            int(r.get("time_min", 0))>0
        ])
    except Exception:
        return False

if st.button("AIでレシピ候補を作る", type="primary"):
    schema = """{
      "recipes":[
        {
          "name":"短い料理名",
          "type":["主菜/副菜/汁物/魚/麺/作り置き/主食 のいずれか"],
          "time_min":15,
          "cost_level": 1,
          "servings": 3,
          "contains": ["小麦","卵","乳","大豆","魚","甲殻","ナッツ など該当すれば"],
          "ingredients":[{"name":"食材名","qty":100,"unit":"g"}],
          "steps":["手順1","手順2","…"]
        }
      ]
    }"""

    prompt = f"""
日本の家庭向けに、以下条件で**JSONのみ**を返してください。文章は禁止。

- 件数: {count}
- 調理時間: {max_time}分以内
- 種類: {', '.join(course)}
- テイスト: {region if region!='なんでも' else '自由'}
- 予算モード: {budget}（1=節約, 2=ふつう, 3=少しリッチ で cost_level を概ね合わせる）
- アレルギー回避: {', '.join(avoid_allergens) or 'なし'} は**絶対に含めない**
- 苦手(Lv2+)は**なるべく避ける**: {', '.join([k for k,v in dislikes.items() if v>=2]) or 'なし'}
- { '在庫を優先して使う: ' + ', '.join(stock_list) if stock_list else '在庫指定なし' }

制約:
- 料理名は被らない
- ingredients は最小2品以上、数量は単位付きで具体的に
- steps は3〜6個、簡潔な文
- JSONルートは {{\"recipes\":[...]}} だけ
"""

    with st.spinner("AIがレシピを考えています…"):
        data, err = ai_json(prompt, schema_hint=schema, model_json="gpt-4o")

    if err:
        st.error(f"生成エラー: {err}")
        st.stop()   # ← return の代わりに停止

    # 解析結果が dict でも raw の場合があるので分岐
    raw = None
    if isinstance(data, dict) and "raw" in data:
        raw = data["raw"]
    recipes = (data or {}).get("recipes", []) if isinstance(data, dict) else []

    if raw and not recipes:
        with st.expander("AIからの生テキスト（デバッグ用）", expanded=False):
            st.code(raw, language="json")

    if not recipes:
        st.warning("JSONの recipes が空でした。条件を少し変えて再試行してください。")
        st.info("コツ：件数を減らす / 調理時間を広げる / 種類を1〜2種に絞る / 在庫優先をOFFにする")
        st.stop()

    # フィルタ＆バリデーション
    valid = []
    skipped = []
    for r in recipes:
        if any(a in (r.get("contains",[]) or []) for a in avoid_allergens):
            r["_skip_reason"] = "アレルギー該当"
            skipped.append(r); continue
        if not validate_recipe(r):
            r["_skip_reason"] = "項目不足（材料/手順/時間）"
            skipped.append(r); continue
        valid.append(r)

    st.success(f"{len(valid)} 件が有効でした（除外 {len(skipped)} 件）")

    # 既存DB
    db = read_json(RECIPES, default={"recipes":[]})
    existing = {r["name"] for r in db.get("recipes", [])}

    accept_flags = {}
    for i, r in enumerate(valid, 1):
        with st.expander(f"{i}. {r.get('name')}", expanded=False):
            st.write(f"種類: {', '.join(r.get('type',[]))} / 時間: {r.get('time_min','-')}分 / コスト: {r.get('cost_level','-')} / サーブ: {r.get('servings','-')}")
            st.write(f"アレルゲン候補: {', '.join(r.get('contains',[])) or '-'}")
            st.markdown("**材料**")
            for ing in r.get("ingredients", []):
                st.write(f"- {ing['name']}：{ing['qty']}{ing['unit']}")
            st.markdown("**手順**")
            for j, step in enumerate(r.get("steps",[]), 1):
                st.write(f"{j}. {step}")
            if r.get("name") in existing:
                st.warning("※ 同名のレシピが既に存在します（上書きはしません）")
                accept_flags[i] = False
            else:
                accept_flags[i] = st.checkbox("このレシピを取り込む", key=f"accept_{i}", value=True)

    if skipped:
        with st.expander("除外された候補（理由付き）", expanded=False):
            for r in skipped:
                st.write(f"- {r.get('name','(名称未定)')} … {r.get('_skip_reason')}")

    if st.button("選択したレシピを保存", type="primary"):
        saved = 0
        for i, r in enumerate(valid, 1):
            if not accept_flags.get(i): 
                continue
            rec = {
                "recipe_id": f"ai_{r.get('name')}",
                "name": r.get("name"),
                "time_min": int(r.get("time_min", 20)),
                "cost_level": int(r.get("cost_level", 2)),
                "servings": int(r.get("servings", 3)),
                "type": r.get("type", []),
                "contains": r.get("contains", []),
                "ingredients": r.get("ingredients", []),
                "steps": r.get("steps", [])
            }
            # 重複回避
            if any(x["name"] == rec["name"] for x in db["recipes"]):
                continue
            db["recipes"].append(rec)
            saved += 1

            if gen_images:
                try:
                    ai_image(
                        f"『{rec['name']}』の家庭料理の完成写真。自然光、温かい色味、食卓で。",
                        out_dir=ASSETS / "meals"
                    )
                except Exception:
                    pass

        write_json(RECIPES, db)
        st.success(f"{saved} 件を保存しました ✅")
        if gen_images:
            st.caption("※ 画像生成は1件ずつ時間/コストがかかります。必要なときだけ有効にしてね。")
