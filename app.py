import streamlit as st
import pandas as pd
import requests

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# データ取得
@st.cache_data(ttl=0)
def load_data():
    try:
        r = requests.get(GAS_URL, timeout=10)
        data = r.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame()

def save_to_sheet(df):
    requests.post(GAS_URL, json={'values': [df.columns.tolist()] + df.values.tolist()})

def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

# 画面構築
st.title("📦 eBay 仕入れ管理システム")
df = load_data()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="main_editor")
    if st.button("💾 スプレッドシートに保存"):
        save_to_sheet(edited)
        st.success("保存完了")
        st.rerun()

with tab2:
    st.subheader("🔍 eBay利益計算ツール")
    current_rate = get_rate()
    # 完全に動く計算ツールをここに格納
    html = f"""
    <div style="padding:20px; border:1px solid #ddd; border-radius:10px;">
        <label>為替レート:</label><input id="rate" type="text" value="{current_rate:.2f}">
        <label>仕入れ価格(円):</label><input id="cost" type="text" value="0">
        <label>売値(ドル):</label><input id="price" type="text" value="0">
        <hr>
        <h3>利益: <span id="profit">0</span>円</h3>
        <script>
            const $=id=>document.getElementById(id);
            function calc(){{
                let r=parseFloat($('rate').value)||0, c=parseFloat($('cost').value)||0, p=parseFloat($('price').value)||0;
                let rev=p*r; let exp=c+(rev*0.15); $('profit').textContent=Math.round(rev-exp);
            }}
            ['rate','cost','price'].forEach(id=>$(id).addEventListener('input',calc));
        </script>
    </div>
    """
    st.html(html)

with tab5:
    st.info("監視機能：移植準備中")
