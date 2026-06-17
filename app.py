import streamlit as st
import pandas as pd
import requests

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

@st.cache_data(ttl=0)
def load_data():
    try:
        r = requests.get(GAS_URL, timeout=10)
        data = r.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame()

def save_to_sheet(df):
    requests.post(GAS_URL, json={'values': [df.columns.tolist()] + df.values.tolist()})

def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

st.title("📦 eBay 仕入れ管理システム")
df = load_data()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="main_editor")
    if st.button("💾 スプレッドシートに保存"):
        save_to_sheet(edited)
        st.success("保存完了")
        st.rerun()

with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    current_rate = get_rate()
    
    # HTML部分をPythonの変数として扱われないよう、f-stringを使わずそのままHTMLとして定義
    # JS内の{}はPython側で干渉しないよう、文字列の外に置くかエスケープしています
    html_code = f"""
    <div id="app-container"></div>
    <script>
    const rate = {current_rate};
    const html = `
    <style>
    :root{{--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;--dim:#9ca89e;--accent:#B79740;--teal:#1A5C3A;--teal2:#2D7A4F;--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;}}
    body{{font-family:sans-serif;padding:10px;}}
    .sec{{background:var(--card);margin:8px 0;border-radius:var(--r);padding:14px;border:1px solid var(--border);}}
    input{{width:100%;padding:10px;margin-bottom:10px;border:1px solid #ccc;border-radius:8px;}}
    .btn-search{{display:block;padding:10px;text-align:center;background:#0064d2;color:#fff;text-decoration:none;border-radius:8px;margin-bottom:5px;}}
    </style>
    <div class="sec">
        <input id="jaInput" type="text" placeholder="日本語の商品名">
        <input id="enInput" type="text" placeholder="英語の商品名">
        <a id="lMercari" class="btn-search">メルカリで検索</a>
        <a id="lEbay" class="btn-search">eBayで検索</a>
    </div>
    `;
    document.getElementById('app-container').innerHTML = html;
    
    document.getElementById('jaInput').addEventListener('input', (e) => {{
        const val = e.target.value;
        document.getElementById('lMercari').href = 'https://jp.mercari.com/search?keyword=' + encodeURIComponent(val);
    }});
    document.getElementById('enInput').addEventListener('input', (e) => {{
        const val = e.target.value;
        document.getElementById('lEbay').href = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(val);
    }});
    </script>
    """
    st.components.v1.html(html_code, height=400)

with tab5:
    st.info("監視機能：移植準備中")
