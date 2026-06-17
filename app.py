import streamlit as st
import pandas as pd
import requests

# 1. 設定
st.set_page_config(page_title="eBay管理", page_icon="📦")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# 2. データ読み込み（表に変換するまでやる）
@st.cache_data(ttl=0)
def load_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        data = response.json()
        # 0番目がヘッダー、1番目以降がデータ
        if len(data) > 1:
            return pd.DataFrame(data[1:], columns=data[0])
        else:
            return pd.DataFrame(columns=data[0])
    except:
        return pd.DataFrame()

# 3. 画面に表示
st.title("📦 eBay 仕入れ管理")
df = load_data()

st.write("スプレッドシートのデータ:")
st.dataframe(df) # これで表になります
