import streamlit as st
from pathlib import Path

# ===== インポート修正 =====
from common.style import inject_css, card, endcard, bubble
from common.fileio import read_json, write_json
from common.pathkit import data_dir
from common.ai import ai_json

inject_css()

# -----------------------------
# データフォルダ
# -----------------------------
DATA = data_dir()
RECIPE_FILE = DATA / "goals.json"

if not RECIPE_FILE.exists():
    write_json(RECIPE_FILE, [])

recipes = read_json(RECIPE_FILE, default=[])

st.title("AIでレシピを大量生成")

st.write("AIにテーマを渡すと、レシピを一括で生成して保存できます。")

# -----------------------------
# 入力欄
# -----------------------------
theme = st.text_input("テーマ例：『節約料理』『和風の献立』『子ども用レシピ』など")

gen_count = st.slider("生成数", 3, 30, 10)

# -----------------------------
# AI生成
# -----------------------------
if st.button("AIで大量生成して保存する 🚀"):
    if not theme:
        st.error("テーマを入力してください。")
    else:
        prompt = f"""
あなたは家庭料理のプロ。
以下のテーマに合う料理を {gen_count} 個、JSONで返してください。

テーマ: {theme}

形式:
[
  {{
    "title": "料理名",
    "time": 調理時間（数字）,
    "type": ["主菜" または "副菜" など],
    "ingredients": ["材料1","材料2"],
    "steps": ["手順1","手順2"]
  }},
  ...
]
"""

        result = ai_json(prompt)
        if isinstance(result, list):
            recipes.extend(result)
            write_json(RECIPE_FILE, recipes)
            st.success("レシピを保存しました！")
            bubble("たくさん作ったよ、ご主人！キミの役に立ててうれしい♡")
        else:
            st.error("AIの返したデータが不正です。")

# -----------------------------
# 現在の数を表示
# -----------------------------
st.info(f"現在の登録レシピ数：{len(recipes)} 件")
