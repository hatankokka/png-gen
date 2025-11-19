import streamlit as st
import traceback

st.write("起動テスト：ここまで動いています")

try:
    # 故意にあなたの app.py 本体を読み込む
    import app_main
except Exception as e:
    st.error("内部エラーを検出しました👇")
    st.code(traceback.format_exc())
