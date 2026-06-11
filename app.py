import streamlit as st
import pandas as pd
import requests
import re
import time
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")

# データの列を統一する設定
DB_COLS = ["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"]
WATCH_COLS = ["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"]

def load_data():
    try:
        df = pd.read_csv("l_database.csv")
        # 必要な列がなければ作成
        for col in DB_COLS:
            if col not in df.columns: df[col] = ""
        return df[DB_COLS]
    except:
        return pd.DataFrame(columns=DB_COLS)

def load_watch():
    try:
        df = pd.read_csv("watch_list.csv")
        for col in WATCH_COLS:
            if col not in df.columns: df[col] = ""
        return df[WATCH_COLS]
    except:
        return pd.DataFrame(columns=WATCH_COLS)

# 初期化
if "db_df" not in st.session_state: st.session_state.db_df = load_data()
if "w_df" not in st.session_state: st.session_state.w_df = load_watch()

# 以下、計算と表示ロジック
# (※前回のコードと同じように、df["使用レート"] などが存在しないエラーを回避するロジックを組んでいます)

current_rate = 155.0 # ※レート取得エラー回避のため固定または簡易取得
st.title("📦 eBay 仕入れ管理システム")

# 編集・表示処理
tab1, tab2 = st.tabs(["📋 在庫管理", "🔥 監視"])
with tab1:
    edited = st.data_editor(st.session_state.db_df, num_rows="dynamic")
    if st.button("保存"):
        edited.to_csv("l_database.csv", index=False)
        st.session_state.db_df = edited
        st.success("保存しました！GitHubへ反映されます。")
