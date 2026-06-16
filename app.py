import streamlit as st
from supabase import create_client

# 【重要】ここを自分の情報に書き換えてください
SUPABASE_URL = "https://fgfxhoolclbsampisebt.supabase.co"
SUPABASE_KEY = "ここにanon publicキーを貼り付け"

# 接続作成
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("接続テスト")

try:
    # 接続確認
    st.write("接続中...")
    supabase.table("inventory").select("*").limit(1).execute()
    st.success("データベース接続成功！")
except Exception as e:
    st.error(f"接続失敗: {e}")
