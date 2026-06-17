import streamlit as st
import pandas as pd
import requests

# 1. 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# 2. データ読み込み関数
@st.cache_data(ttl=0)
def load_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame(columns=["商品名", "仕入(円)"])

# 3. 画面の表示
st.title("📦 eBay 仕入れ管理システム")

df = load_data()
st.write("スプレッドシートから読み込んだデータ:", df)

if st.button("データ再読み込み"):
    st.rerun()
    
