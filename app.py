import streamlit as st
import pandas as pd
import requests
import os
import re
import time
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup

# ページ設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")

DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"

# 定数
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS   = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS   = ["自分", "悠太郎", "その他"]

# データの取得・ロード
@st.cache_data(ttl=0)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # 数値列の強制変換
        for col in ["ID", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "確定レート"]:
            if col not in df.columns: df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        if "メモ" not in df.columns: df["メモ"] = ""
        df["ID"] = df["ID"].astype(int)
        return df
    return pd.DataFrame(columns=["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"])

def load_watch_list():
    if os.path.exists(WATCH_FILE):
        try:
            w = pd.read_csv(WATCH_FILE)
            w = w.loc[:, ~w.columns.duplicated()]
            for col in ["狙う仕入れ価格", "前回最安値", "eBay相場(ドル)"]:
                if col not in w.columns: w[col] = 0.0
                w[col] = pd.to_numeric(w[col], errors="coerce").fillna(0.0)
            if "状態" not in w.columns: w["状態"] = "🆕 未チェック"
            return w[["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"]]
        except: pass
    return pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"])

def check_yahoo_auctions_html(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    search_url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&is_all=1&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            prices = [int(re.sub(r'[^\d]', '', e.text)) for e in soup.find_all(class_=re.compile("Product__priceValue")) if re.sub(r'[^\d]', '', e.text)]
            return min(prices) if prices else None
    except: pass
    return None

# メイン処理
current_rate = get_rate()
df = load_data()
if "w_df" not in st.session_state: st.session_state.w_df = load_watch_list()

# レイアウト・スタイル
st.markdown("<style>.main-header {font-size:1.6rem; font-weight:800; color:#1A5C3A;}</style>", unsafe_allow_html=True)
col_h1, col_h2 = st.columns([3, 1])
col_h1.markdown('<p class="main-header">📦 eBay 仕入れ・利益管理システム</p>', unsafe_allow_html=True)
col_h2.metric("💱 現在レート", f"¥{current_rate:.2f}")

# タブ定義
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫管理表", "🔍 利益計算ツール", "📥 新規登録", "💾 データDL", "🔥 監視"])

with tab1:
    st.subheader("📋 在庫管理表")
    edited_df = st.data_editor(df, column_config={
        "ID": st.column_config.NumberColumn(disabled=True),
        "ステータス": st.column_config.SelectboxColumn(options=STATUS_OPTIONS),
        "発送サイズ": st.column_config.SelectboxColumn(options=SIZE_OPTIONS),
        "担当者": st.column_config.SelectboxColumn(options=USER_OPTIONS),
    }, hide_index=True, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 変更を保存", type="primary"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("保存しました")
        st.rerun()

with tab2:
    st.subheader("🔍 利益計算ツール")
    # シンプルに動作するJS埋め込み計算機
    calc_html = f"""
    <div id="calc" style="padding:20px; border:1px solid #ddd; border-radius:10px;">
        <label>為替レート:</label><input type="number" id="r" value="{current_rate:.2f}" step="0.1"><br>
        <label>仕入れ(円):</label><input type="number" id="c" value="0"><br>
        <label>販売額($):</label><input type="number" id="p" value="0"><br>
        <h2 id="res">利益: 0円</h2>
    </div>
    <script>
        const update = () => {{
            const r = parseFloat(document.getElementById('r').value);
            const c = parseFloat(document.getElementById('c').value);
            const p = parseFloat(document.getElementById('p').value);
            const prof = (p * r * 0.85) - c - 2000;
            document.getElementById('res').innerText = '利益: ' + Math.round(prof).toLocaleString() + '円';
        }};
        ['r','c','p'].forEach(id => document.getElementById(id).addEventListener('input', update));
    </script>
    """
    st.html(calc_html)

with tab3:
    with st.form("new_entry", clear_on_submit=True):
        name = st.text_input("商品名")
        user = st.selectbox("担当者", USER_OPTIONS)
        cost = st.number_input("仕入(円)", value=0)
        if st.form_submit_button("✅ 登録"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{"ID": new_id, "日付": datetime.now().strftime("%Y-%m-%d"), "担当者": user, "商品名": name, "仕入(円)": cost, "ステータス": "掲載前"}])
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
            st.rerun()

with tab4:
    st.download_button("📥 全データダウンロード", data=df.to_csv(index=False), file_name="db.csv")

with tab5:
    st.subheader("🔥 監視リスト")
    if st.button("🔄 巡回開始"):
        for i, row in st.session_state.w_df.iterrows():
            val = check_yahoo_auctions_html(row["商品名"])
            if val: st.session_state.w_df.at[i, "前回最安値"] = val
        st.session_state.w_df.to_csv(WATCH_FILE, index=False)
        st.rerun()
    st.data_editor(st.session_state.w_df, num_rows="dynamic", use_container_width=True)
