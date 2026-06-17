import streamlit as st
import pandas as pd
import requests

# 1. 設定
st.set_page_config(page_title="eBay管理", page_icon="📦")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# 2. データを取ってくる命令
@st.cache_data(ttl=0)
def load_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        return response.json()
    except Exception as e:
        return f"エラーが発生しました: {e}"

# 3. 画面に表示する
st.title("📦 eBay 仕入れ管理")
data = load_data()

st.write("取得したデータの内容:")
st.write(data)
