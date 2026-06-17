import streamlit as st
import pandas as pd
import requests

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# データ連携処理
@st.cache_data(ttl=0)
def load_data():
    r = requests.get(GAS_URL)
    data = r.json()
    return pd.DataFrame(data[1:], columns=data[0])

def save_to_sheet(df):
    requests.post(GAS_URL, json={'values': [df.columns.tolist()] + df.values.tolist()})

# メイン処理
st.title("📦 eBay 仕入れ管理システム")
df = load_data()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

# 1. 在庫管理（ここでのみ data_editor を使う）
with tab1:
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="main_editor")
    if st.button("💾 スプレッドシートに保存"):
        save_to_sheet(edited)
        st.success("保存しました")
        st.rerun()

# 2. 利益計算
with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    
    # 為替レートの取得
    def get_rate():
        try:
            return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
        except:
            return 155.0

    current_rate = get_rate()
    
    html_calc_template = """
    """
    
    # "__CURRENT_RATE__" を現在のレートに置き換えて表示
    html_calc = html_calc_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}")
    st.html(html_calc)

# 3. 新規登録
with tab3:
    with st.form("new_entry"):
        name = st.text_input("商品名")
        cost = st.number_input("仕入れ値")
        if st.form_submit_button("登録"):
            st.write("登録機能を追加中...")

# 5. 監視機能
with tab5:
    st.info("ここに以前の監視ロジックを移植します")
