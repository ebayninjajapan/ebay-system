import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://fgfxhoolclbsampisebt.supabase.co"
SUPABASE_KEY = "ここに先ほどのeyJから始まるキー" # そのままでOK

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("在庫管理システム")

try:
    # 接続確認
    supabase.table("inventory").select("*").limit(1).execute()
    st.success("データベース接続成功！")
except Exception as e:
    st.error(f"接続失敗: {e}")
