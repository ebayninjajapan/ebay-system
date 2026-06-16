import streamlit as st
from supabase import create_client

# あなたのURLとキー（ここに正しいキーを貼ってください）
SUPABASE_URL = "https://fgfxhoolclbsampisebt.supabase.co"
SUPABASE_KEY = "ここにeyJから始まるキーを貼り付け"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ここから下に、元のアプリのコードを貼り付けてください
# 例えば、元々あった在庫を表示する機能など
st.title("在庫管理システム")
st.write("準備中です")
