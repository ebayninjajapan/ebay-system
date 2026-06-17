import streamlit as st
import pandas as pd
import requests

st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")
GAS_URL = "ここにあなたのGASのURLを貼り付けてください"

@st.cache_data(ttl=0)
def load_data():
    try:
        response = requests.get(GAS_URL, timeout=10)
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame(columns=["商品名", "仕入(円)"])

def save_to_sheet(df):
    payload = [df.columns.tolist()] + df.values.tolist()
    requests.post(GAS_URL, json={'values': payload})

st.title("📦 eBay 仕入れ管理システム")
df = load_data()

# ★ここでタブを作ります
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫管理表", "🔍 利益計算ツール", "📥 新規仕入れ登録", "💾 データDL", "🔥 お気に入り監視"])

with tab1:
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 変更をスプレッドシートに保存"):
        save_to_sheet(edited_df)
        st.success("保存しました！")
        st.rerun()

with tab2:
    st.write("ここに利益計算ツールが入ります。")

with tab3:
    st.write("ここに新規登録機能が入ります。")

with tab4:
    st.write("ここにダウンロードボタンが入ります。")

with tab5:
    st.write("ここに監視機能が入ります。")
