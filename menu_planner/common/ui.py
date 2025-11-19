import streamlit as st

def section(title: str, icon: str=""):
    st.markdown(f"### {icon} {title}" if icon else f"### {title}")

def badge(text: str):
    st.markdown(
        f"<span style='padding:2px 8px;border-radius:999px;background:#eef;display:inline-block'>{text}</span>",
        unsafe_allow_html=True
    )
