import streamlit as st

def recipe_drawer(recipe, key=None):
    """
    レシピを下からスライド表示するドロワー風UI
    recipe: {name, type, time_min, ingredients, steps}
    """
    st.markdown(
        """
        <style>
        .drawer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            max-height: 70%;
            background: #fff7ef;
            border-top: 3px solid #ffcc99;
            border-radius: 20px 20px 0 0;
            box-shadow: 0 -4px 12px rgba(0,0,0,0.15);
            padding: 1.2rem 1.5rem;
            overflow-y: auto;
            animation: slideUp 0.35s ease-out;
            z-index: 9999;
        }
        @keyframes slideUp {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .recipe-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #222;
        }
        .recipe-tags {
            margin-top: 0.3rem;
            color: #666;
            font-size: 0.9rem;
        }
        .recipe-section {
            margin-top: 1rem;
            font-weight: bold;
            color: #444;
            border-bottom: 1px solid #ddd;
        }
        .recipe-body {
            margin-left: 0.5rem;
            color: #333;
            font-size: 0.95rem;
        }
        .recipe-btns {
            display: flex;
            justify-content: space-between;
            margin-top: 1.3rem;
        }
        .recipe-btns button {
            background: #ffb366;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    name = recipe.get("name", "レシピ名不明")
    time_min = recipe.get("time_min", "??")
    tags = "・".join(recipe.get("type", []))
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])

    with st.container():
        st.markdown(f"""
        <div class="drawer">
            <div class="recipe-title">{name}</div>
            <div class="recipe-tags">⏱ {time_min}分｜{tags}</div>

            <div class="recipe-section">材料</div>
            <div class="recipe-body">
                {"<br>".join([f"・{i['name']} {i.get('qty','')} {i.get('unit','')}" for i in ingredients])}
            </div>

            <div class="recipe-section">作り方</div>
            <div class="recipe-body">
                {"<br>".join([f"{idx+1}. {s}" for idx, s in enumerate(steps)])}
            </div>

            <div class="recipe-btns">
                <button onclick="window.speechSynthesis.speak(new SpeechSynthesisUtterance('{name}の作り方を読み上げます'));">🔊 読み上げ</button>
                <button>＋ 今週に入れる</button>
                <button>🛒 買い物に追加</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
