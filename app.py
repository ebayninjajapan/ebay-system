import streamlit as st
from supabase import create_client

# 【重要】ここを自分の情報に書き換えてください
SUPABASE_URL = "https://fgfxhoolclbsampisebt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnZnhob29sY2xic2FtcGlzZWJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MDg0OTYsImV4cCI6MjA5NzA4NDQ5Nn0.9gQZOiWP7ljPLyIfTim9WDw2M17Tn0UuSWgZgR422yI"

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
