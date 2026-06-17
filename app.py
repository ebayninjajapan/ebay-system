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
import streamlit as st
import pandas as pd
import requests

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# 読み込み・保存の関数（これでスプシと同期されます）
@st.cache_data(ttl=0)
def load_data():
    return pd.DataFrame(requests.get(GAS_URL).json()[1:], columns=requests.get(GAS_URL).json()[0])

def save_to_sheet(df):
    requests.post(GAS_URL, json={'values': [df.columns.tolist()] + df.values.tolist()})

# タブ作成
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    df = load_data()
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 保存"):
        save_to_sheet(edited)
        st.success("保存完了")
        st.rerun()

with tab2:
    st.write("ここに以前の計算ツールHTMLを貼り付けてください")

with tab5:
    st.write("ここに以前の監視ロジックを貼り付けてください")
