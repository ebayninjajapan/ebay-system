import streamlit as st
import pandas as pd
import requests

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")
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

# 為替レート取得関数
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

# 画面表示
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
    
    # ここにHTMLを配置
    html_calc_template = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<style>
:root{--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);padding:10px 12px 280px;}
.sec{background:var(--card);margin:8px 0;border-radius:var(--r);padding:14px;border:1px solid var(--border);}
.lbl{display:block;font-size:11px;font-weight:600;color:var(--sub);margin-bottom:4px;}
input{width:100%;padding:10px 11px;border:1px solid var(--iborder);border-radius:var(--rs);font-size:15px;background:var(--ibg);}
.mb{margin-bottom:11px;}.trans-box{display:flex;gap:6px;align-items:stretch;}.trans{flex:1;background:rgba(26,92,58,.06);padding:10px;border-radius:var(--rs);font-size:13px;color:#1A5C3A;font-weight:700;}
.btn-gtrans{padding:0 12px;background:#4285F4;color:#fff;border-radius:var(--rs);font-size:11px;text-decoration:none;display:flex;align-items:center;}
.btn-search{flex:1;text-align:center;padding:11px 5px;border-radius:var(--rs);text-decoration:none;font-size:12px;font-weight:800;color:#fff;display:block;}
.off{opacity:.3;pointer-events:none;background:#ccc !important;}
.panel{position:fixed;bottom:0;left:0;right:0;background:#fafbf9;border-top:1px solid var(--border);padding:11px 14px;z-index:99;}
.pcol .val{font-size:22px;font-weight:900;}.pos{color:var(--pp);}.neg{color:var(--pn);}
</style></head>
<body>
<div style="display:flex;gap:12px;">
 <div class="sec" style="flex:1;"><div class="mb"><label class="lbl">🇯🇵 商品名</label><input id="jaInput" type="text"></div><div class="trans" id="jaToEnResult">英語に翻訳されます</div></div>
 <div class="sec" style="flex:1;"><div class="mb"><label class="lbl">🇺🇸 英語名</label><input id="enInput" type="text"></div><div class="trans" id="enToJaResult">日本語に翻訳されます</div></div>
</div>
<div class="sec">
 <div class="mb"><label class="lbl">為替レート</label><input id="exchangeRate" type="text" value="__CURRENT_RATE__"></div>
 <div class="mb"><label class="lbl">仕入れ価格(円)</label><input id="costPrice" type="text" value="0"></div>
 <div class="mb"><label class="lbl">売値(ドル)</label><input id="itemPrice" type="text" value="0"></div>
</div>
<div class="panel">
 <div class="pcol"><div class="lbl">最終利益</div><div class="val pos" id="pProfit">0円</div></div>
</div>
<script>
(function(){
 const $=id=>document.getElementById(id); const num=id=>parseFloat(($(id).value||'').replace(/,/g,''))||0;
 function calc(){
  const rate=num('exchangeRate'), cost=num('costPrice'), item=num('itemPrice');
  const rev=item*rate; const expense=cost+(rev*0.15); const profit=rev-expense;
  $('pProfit').textContent=Math.round(profit).toLocaleString()+'円';
  $('pProfit').className='val '+(profit>=0?'pos':'neg');
 }
 ['exchangeRate','costPrice','itemPrice'].forEach(id=>$(id).addEventListener('input',calc));
})();
</script>
</body></html>"""
    
    html_calc = html_calc_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}")
    st.html(html_calc)

with tab5:
    st.info("監視機能：準備中")
