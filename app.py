import streamlit as st
import pandas as pd
import requests

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理")
GAS_URL = "https://script.google.com/macros/s/AKfycbxrIQJy2O2T2CeLXddfbO2GQfW1fLG7uIBfTOzAXEdWRlf6YqaskLsMlasEF5EaIQ1o/exec"

# データ取得
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

# 画面構築
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
    # 以前のHTML/JSをそのまま再現した完全版
    html_full = f"""
    <!DOCTYPE html>
    <html lang="ja"><head><meta charset="UTF-8">
    <style>
      :root{{--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;}}
      body{{font-family:sans-serif;background:#fff;padding:10px;}}
      .sec{{background:#fff;border-radius:14px;padding:14px;border:1px solid #eee;margin-bottom:10px;}}
      .lbl{{font-size:11px;font-weight:600;color:#5a6b5e;margin-bottom:4px;}}
      input{{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;margin-bottom:10px;background:#f5f7f5;}}
      .panel{{position:sticky;bottom:0;background:#fafbf9;border-top:1px solid #eee;padding:15px;}}
      .val{{font-size:22px;font-weight:900;}}.pos{{color:#1A7A42;}}.neg{{color:#C62828;}}
    </style></head>
    <body>
      <div class="sec">
        <label class="lbl">為替レート</label><input id="exRate" type="text" value="{current_rate:.2f}">
        <label class="lbl">仕入れ価格(円)</label><input id="cost" type="text" value="0">
        <label class="lbl">eBay 販売価格(ドル)</label><input id="price" type="text" value="0">
      </div>
      <div class="panel">
        <div class="lbl">最終利益</div>
        <div class="val pos" id="profit">0円</div>
        <div id="rate">利益率 0%</div>
        <div style="font-size:12px;margin-top:5px;">売上: <strong id="rev">0円</strong> | 経費(仕入+15%): <strong id="exp">0円</strong></div>
      </div>
      <script>
        const $=id=>document.getElementById(id);
        function calc(){{
          let r=parseFloat($('exRate').value)||0, c=parseFloat($('cost').value)||0, p=parseFloat($('price').value)||0;
          let rev=p*r; let exp=c+(rev*0.15); let pro=rev-exp;
          $('profit').textContent=Math.round(pro).toLocaleString()+'円';
          $('profit').className='val '+(pro>=0?'pos':'neg');
          $('rate').textContent='利益率 '+(rev>0?(pro/rev*100).toFixed(1):0)+'%';
          $('rev').textContent=Math.round(rev).toLocaleString()+'円';
          $('exp').textContent=Math.round(exp).toLocaleString()+'円';
        }}
        ['exRate','cost','price'].forEach(id=>$(id).addEventListener('input',calc));
      </script>
    </body></html>
    """
    st.html(html_full)

with tab5:
    st.info("監視機能：移植準備中")
