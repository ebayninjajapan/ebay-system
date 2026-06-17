import streamlit as st
import pandas as pd
import requests

# 1. 設定
st.set_page_config(page_title="eBay管理", page_icon="📦")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# 2. データ読み込み（表に変換）
@st.cache_data(ttl=0)
def load_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame()

# 3. データをスプレッドシートに書き戻す関数
def save_to_sheet(df):
    payload = [df.columns.tolist()] + df.values.tolist()
    requests.post(GAS_URL, json={'values': payload})

# 4. 画面表示と編集機能
st.title("📦 eBay 仕入れ管理")
df = load_data()

# 編集可能な表を表示
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 保存ボタン
if st.button("💾 スプレッドシートに保存"):
    save_to_sheet(edited_df)
    st.success("保存完了！")
    st.rerun()
