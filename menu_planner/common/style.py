from pathlib import Path
import streamlit as st

def inject_css():
    css = """
    :root{
      --bg:#fffdfa;
      --panel:#fff4e9;
      --ink:#2a2a2a;
      --mute:#667085;
      --brand:#ff7a59;
      --brand-2:#ffd7c9;
      --ok:#22c55e;
      --warn:#f59e0b;
      --card-shadow: 0 8px 18px rgba(0,0,0,0.06);
      --radius-xl: 18px;
      --radius-xxl: 28px;
    }
    .block-container{padding-top:2rem; padding-bottom:6rem;}
    .stApp{background:var(--bg);}
    h1,h2,h3{letter-spacing:.2px}
    h1{font-weight:800}
    h2{font-weight:700}
    /* カード */
    .card{
      background:#fff; border-radius: var(--radius-xl);
      box-shadow: var(--card-shadow); padding: 18px 20px;
      border: 1px solid #f2e7de; margin: 8px 0;
    }
    .card.soft{background: var(--panel)}
    .badge{
      display:inline-flex; gap:.4rem; align-items:center;
      padding:.25rem .6rem; border-radius: 9999px; font-size:.78rem;
      background: var(--brand-2); color:#8a260e; border:1px solid #ffc2af;
    }
    /* CTAボタン */
    .stButton>button{
      border-radius: 12px !important;
      padding:.6rem 1rem !important;
      font-weight:700;
      border:1px solid #ffb7a3;
      background:var(--brand);
      color:white !important;
      box-shadow: 0 6px 14px rgba(255,122,89,.25);
    }
    .stButton>button:hover{filter:brightness(.96)}
    /* チェックボックス行を見やすく */
    label{font-weight:600}
    /* チップ */
    .chip{
      display:inline-flex;align-items:center;gap:.4rem;
      padding:.2rem .55rem;
      background:#fff;border:1px solid #f0e4db;
      border-radius:9999px;margin:.15rem .15rem 0 0;
    }
    /* 吹き出し */
    .bubble{
      background:#fff;
      border:1px solid #f0e4db;
      border-radius:16px;
      padding:12px 14px;
      max-width:720px;
      box-shadow:var(--card-shadow);
    }
    .bubble.luna{
      background:#fff;
      position:relative;
      border-left:4px solid var(--brand);
    }
    .bubble .meta{
      color:var(--mute);
      font-size:.82rem;
      margin-bottom:.25rem;
    }
    .hint{color:var(--mute); font-size:.9rem}
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def card(title:str=None, soft=False):
    cls = "card soft" if soft else "card"
    if title:
        st.markdown(f"<div class='{cls}'><h3 style='margin:.2rem 0 1rem'>{title}</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)


def endcard():
    st.markdown("</div>", unsafe_allow_html=True)


def bubble(text:str, who:str="luna", meta:str=""):
    st.markdown(
        f"""
        <div class="bubble {who}">
          <div class="meta">{meta}</div>
          {text}
        </div>
        """,
        unsafe_allow_html=True,
    )
