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


inject_css()

DATA = data_dir()
ASSETS = assets_dir()
RECIPES = DATA / "recipes.json"
PHOTOS  = ASSETS / "meals"

st.title("レシピ詳細")

db = read_json(RECIPES, default={"recipes":[]})
recipes = {r["name"]: r for r in db.get("recipes", [])}

name = st.selectbox("レシピを選ぶ", ["(選択)"] + list(recipes.keys()))
if name != "(選択)":
    r = recipes[name]
    st.markdown(f"#### {name}  <span class='badge'>所要 {r.get('time_min','-')}分</span>", unsafe_allow_html=True)
    st.caption(f"コスト目安: {r.get('cost_level','-')} / サービング: {r.get('servings','-')}")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**材料**")
        for ing in r.get("ingredients", []):
            st.write(f"- {ing['name']}：{ing['qty']}{ing['unit']}")
    with colB:
        st.markdown("**手順**")
        steps = r.get("steps") or ["手順未登録"]
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")

    st.divider()
    st.markdown("### 見た目（写真を保存 or AIで生成）")

    up = st.file_uploader("完成写真をアップロード（任意）", type=["png","jpg","jpeg"])
    if up and st.button("保存"):
        PHOTOS.mkdir(parents=True, exist_ok=True)
        savep = PHOTOS / f"{name}.jpg"
        savep.write_bytes(up.getvalue())
        st.success("写真を保存しました")
        st.image(str(savep), caption="アップロードした写真", use_column_width=True)

    with st.expander("AIで完成イメージを生成する", expanded=False):
        prompt = st.text_area("生成プロンプト", f"料理の完成写真風。器は家庭的、やさしい照明。料理名:{name}")
        if st.button("AI画像を作る", type="primary"):
            out, err = ai_image(prompt, out_dir=PHOTOS)
            if err: st.error(f"画像生成に失敗: {err}")
            else:   st.image(str(out), caption="AI生成イメージ", use_column_width=True)

    st.divider()
    st.markdown("### AIアドバイス")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("時短テクを聞く"):
            txt, _ = ai_text(f"{name}を15分で作るための時短テクを箇条書きで3つ。")
            st.write(txt)
    with col2:
        avoid = st.text_input("避けたい材料（カンマ区切り）", "卵, 牛乳")
        if st.button("代替食材を提案"):
            txt, _ = ai_text(f"{name}で[{avoid}]を使わない代替案を、日本の家庭向けに分量と理由つきで3個。")
            st.write(txt)
