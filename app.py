import streamlit as st
import pandas as pd
import requests
import os
import re
import time
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup

# ─────────────────────────────────────────
# 設定・定数
# ─────────────────────────────────────────
st.set_page_config(layout="wide", page_title="eBay/メルカリ管理システム", page_icon="📦")
DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]

# ─────────────────────────────────────────
# 補助関数（ヤフオク巡回・レート取得）
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_rate():
    try: return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except: return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # 必要な列の整合性を保つ
        cols = ["ID", "日付", "担当者", "商品名", "販路", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "送料(確定)", "メモ"]
        for col in cols:
            if col not in df.columns: df[col] = 0 if "ID" in col or "仕入" in col or "送料" in col or "レート" in col or "売値" in col else ""
        return df
    return pd.DataFrame(columns=["ID", "日付", "担当者", "商品名", "販路", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "送料(確定)", "メモ"])

def check_yahoo_auctions_html(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&is_all=1&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = [int(re.sub(r'[^\d]', '', e.text)) for e in soup.find_all(class_=re.compile("Product__priceValue")) if e.text]
        return min(prices) if prices else None
    except: return None

# ─────────────────────────────────────────
# メインUIロジック
# ─────────────────────────────────────────
current_rate = get_rate()
df = load_data()

st.title("📦 eBay & メルカリ 一元管理システム")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫管理表", "🔍 利益計算", "📥 新規登録", "💾 データDL", "🔥 監視"])

# TAB 1: 在庫管理表
with tab1:
    edited_df = st.data_editor(df, column_config={
        "販路": st.column_config.SelectboxColumn(options=["eBay", "メルカリ"]),
        "ステータス": st.column_config.SelectboxColumn(options=STATUS_OPTIONS),
        "発送サイズ": st.column_config.SelectboxColumn(options=SIZE_OPTIONS)
    }, hide_index=True, num_rows="dynamic")
    if st.button("💾 変更を保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("保存しました")
        st.rerun()

# TAB 2: 利益計算 (550行分のロジックをここに復元するためのHTMLフレーム)
with tab2:
    st.subheader("🔍 利益計算ツール")
    # ここに以前お使いの長い計算ロジック（HTML/JS）をそのまま配置してください
    st.info("※以前のHTML計算テンプレートをここに入力してください。")

# TAB 3: 新規登録
with tab3:
    with st.form("new_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        u, n = c1.selectbox("担当者", USER_OPTIONS), c2.text_input("商品名")
        v, c = c1.selectbox("販路", ["eBay", "メルカリ"]), c2.number_input("仕入(円)", value=0)
        if st.form_submit_button("✅ 登録"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{"ID": new_id, "日付": datetime.now().strftime("%Y-%m-%d"), "担当者": u, "商品名": n, "販路": v, "仕入(円)": c, "ステータス": "掲載前"}])
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
            st.rerun()

# TAB 4: DL
with tab4:
    st.download_button("📥 CSVダウンロード", data=df.to_csv(index=False), file_name="all_data.csv")

# TAB 5: 監視機能
with tab5:
    if "w_df" not in st.session_state:
        st.session_state.w_df = pd.read_csv(WATCH_FILE) if os.path.exists(WATCH_FILE) else pd.DataFrame(columns=["商品名", "狙う価格", "状態"])
    if st.button("🔄 巡回開始"):
        with st.spinner("巡回中..."):
            for i, row in st.session_state.w_df.iterrows():
                low = check_yahoo_auctions_html(row["商品名"])
                if low: st.session_state.w_df.at[i, "状態"] = f"最安:{low}円"
            st.session_state.w_df.to_csv(WATCH_FILE, index=False)
            st.rerun()
    st.data_editor(st.session_state.w_df, num_rows="dynamic")
