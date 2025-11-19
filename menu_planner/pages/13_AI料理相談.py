import streamlit as st
from common.style import inject_css, card, endcard, bubble
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image


inject_css()

st.title("AI料理相談 🍳")

st.markdown("どんな料理を作りたい？食材・時間・気分を入力してみよう！")

query = st.text_area("相談内容を入力", placeholder="例：冷蔵庫にキャベツと豚肉があるけど、何作ろう？")

if "last_proposal" not in st.session_state:
    st.session_state.last_proposal = ""

if st.button("ルナに相談する 🧡"):
    if query.strip():
        st.session_state.last_proposal = f"それなら、『豚バラ塩キャベツ炒め』がおすすめ！10分で作れるし、キャベツの甘みが引き立つよ！"
    else:
        st.session_state.last_proposal = "どんな材料があるか教えてくれる？それに合わせて考えるね🍀"

if st.session_state.last_proposal:
    st.subheader("ルナの提案")
    bubble(st.session_state.last_proposal.replace("\n","<br>"), meta="Lunaが考えたよ")
