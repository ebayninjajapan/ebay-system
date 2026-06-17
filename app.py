import streamlit as st
import pandas as pd
import requests

# 1. 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")
GAS_URL = "ここにあなたのGASのURLを貼り付けてください"

# 2. データ読み込み関数
@st.cache_data(ttl=0)
def load_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame(columns=["商品名", "仕入(円)"])

# 3. データ保存関数（ここが重要）
def save_to_sheet(df):
    # ヘッダーとデータを含めてGASにPOSTする
    payload = [df.columns.tolist()] + df.values.tolist()
    requests.post(GAS_URL, json={'values': payload})

# 4. 画面表示
st.title("📦 eBay 仕入れ管理システム")

df = load_data()

# 編集可能な表を表示
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 保存ボタン
if st.button("💾 変更をスプレッドシートに保存"):
    save_to_sheet(edited_df)
    st.success("保存しました！")
    st.rerun()
