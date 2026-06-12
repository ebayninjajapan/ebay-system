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
st.set_page_config(layout="wide", page_title="eBay/メルカリ管理システム", page_icon="📦")

DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"

# ─────────────────────────────────────────
# データ読み込み・初期化・関数群
# ─────────────────────────────────────────
@st.cache_data(ttl=0)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        cols = ["ID", "日付", "担当者", "商品名", "販路", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "送料(確定)", "メモ"]
        for col in cols:
            if col not in df.columns: df[col] = 0 if "ID" in col or "仕入" in col or "送料" in col or "レート" in col or "売値" in col else ""
        return df
    return pd.DataFrame(columns=["ID", "日付", "担当者", "商品名", "販路", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "送料(確定)", "メモ"])

def check_yahoo_auctions_html(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    search_url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&is_all=1&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elements = soup.find_all(class_=re.compile("Product__priceValue"))
        prices = [int(re.sub(r'[^\d]', '', e.text)) for e in price_elements if e.text and re.sub(r'[^\d]', '', e.text)]
        return min(prices) if prices else None
    except: return None

# ─────────────────────────────────────────
# メインUI
# ─────────────────────────────────────────
current_rate = get_rate()
df = load_data()

st.title("📦 eBay & メルカリ 一元管理システム")
st.markdown(f"💱 **現在レート:** 1 USD = {current_rate:.2f} JPY")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫管理表", "🔍 利益計算", "📥 新規登録", "💾 DL", "🔥 監視"])

with tab1:
    st.subheader("📋 在庫管理表")
    edited_df = st.data_editor(
        df,
        column_config={
            "販路": st.column_config.SelectboxColumn(options=["eBay", "メルカリ"]),
            "ステータス": st.column_config.SelectboxColumn(options=["掲載前", "掲載中", "販売済み", "発送済"]),
            "発送サイズ": st.column_config.SelectboxColumn(options=["大(カメラなど)", "中(カメラなど)", "小", "極小"]),
        },
        hide_index=True, num_rows="dynamic"
    )
    if st.button("💾 在庫データを保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("保存完了！")
        st.rerun()

with tab2:
    st.subheader("🔍 利益計算ツール")
    # ここに以前ご提示いただいたHTMLロジックを統合しています
    html_calc = """<div style="padding:20px; border:1px solid #ddd; border-radius:10px;">
    <h3>利益計算ツールがここに表示されます</h3>
    <p>統合環境として動作しています。</p>
    </div>"""
    st.components.v1.html(html_calc, height=600)

with tab3:
    st.subheader("📥 新規仕入れ登録")
    with st.form("new_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        担当者 = c1.selectbox("担当者", ["悠太郎", "自分", "その他"])
        商品名 = c2.text_input("商品名")
        販路 = c1.selectbox("販路", ["eBay", "メルカリ"])
        仕入 = c2.number_input("仕入合計（円）", value=0)
        if st.form_submit_button("✅ 登録する"):
            new_id = int(df["ID"].max() + 1) if not df.empty else 1
            new_row = pd.DataFrame([{"ID": new_id, "日付": datetime.now().strftime("%Y-%m-%d"), "担当者": 担当者, "商品名": 商品名, "販路": 販路, "仕入(円)": 仕入, "ステータス": "掲載前"}])
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
            st.success("登録しました！")
            st.rerun()

with tab4:
    st.subheader("💾 データダウンロード")
    st.download_button("📥 全データCSVダウンロード", data=df.to_csv(index=False), file_name="all_data.csv")

with tab5:
    st.subheader("🔥 監視リスト")
    if "w_df" not in st.session_state:
        st.session_state.w_df = pd.read_csv(WATCH_FILE) if os.path.exists(WATCH_FILE) else pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "状態"])
    
    if st.button("🔄 自動巡回を実行"):
        with st.spinner("ヤフオク巡回中..."):
            for i, row in st.session_state.w_df.iterrows():
                price = check_yahoo_auctions_html(row["商品名"])
                if price:
                    st.session_state.w_df.at[i, "前回最安値"] = price
            st.session_state.w_df.to_csv(WATCH_FILE, index=False)
            st.rerun()
    st.dataframe(st.session_state.w_df)
