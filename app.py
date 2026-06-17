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
    # keyを固定することで重複エラーを防ぎます
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="stock_editor")
    if st.button("💾 スプレッドシートに保存"):
        save_to_sheet(edited)
        st.success("保存完了")
        st.rerun()

with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    current_rate = get_rate()
    
    # CSSやJSの {} を {{ }} と二重にすることで、Pythonの変数誤認を回避しています
    html_template = f"""
<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<style>
:root{{--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;}}
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);padding:10px;}}
.sec{{background:var(--card);margin:8px 0;border-radius:var(--r);padding:14px;border:1px solid var(--border);}}
.lbl{{display:block;font-size:11px;font-weight:600;color:var(--sub);margin-bottom:4px;}}
input{{width:100%;padding:10px;border:1px solid var(--iborder);border-radius:var(--rs);background:var(--ibg);margin-bottom:10px;}}
.trans{{background:rgba(26,92,58,.06);padding:10px;border-radius:var(--rs);font-size:13px;color:#1A5C3A;font-weight:700;margin-bottom:10px;}}
.btn{{display:block;width:100%;padding:10px;margin-bottom:5px;border-radius:8px;text-align:center;text-decoration:none;color:#fff;font-weight:bold;}}
.off{{opacity:0.3;pointer-events:none;}}
.panel{{position:sticky;bottom:0;background:#fafbf9;padding:15px;border-top:1px solid var(--border);}}
</style></head>
<body>
<div class="sec">
    <label class="lbl">日本語名</label><input id="jaInput" type="text">
    <div class="trans" id="jaToEnResult">英語に翻訳されます</div>
    <label class="lbl">英語名</label><input id="enInput" type="text">
    <div class="trans" id="enToJaResult">日本語に翻訳されます</div>
</div>
<div class="sec">
    <a id="lMercari" class="btn off" style="background:#e32b2b;">メルカリ検索</a>
    <a id="lYahoo" class="btn off" style="background:#ffaa00;color:#000;">ヤフオク検索</a>
    <a id="lEbay" class="btn off" style="background:#0064d2;">eBay検索</a>
    <a id="lEbaySold" class="btn off" style="background:#2d7a4f;">eBay(Sold)検索</a>
</div>
<div class="sec">
    <label class="lbl">為替レート</label><input id="exRate" type="text" value="{current_rate:.2f}">
    <label class="lbl">仕入れ価格(円)</label><input id="cost" type="text" value="0">
    <label class="lbl">売値(ドル)</label><input id="price" type="text" value="0">
</div>
<div class="panel">
    <div class="lbl">最終利益</div>
    <div id="profit" style="font-size:22px;font-weight:900;">0円</div>
</div>
<script>
(function(){{
    const $=id=>document.getElementById(id);
    const trans=async(q,pair,resId)=>{{
        const r=await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(q)+'&langpair='+pair);
        const d=await r.json();
        if(d.responseData) $(resId).textContent=d.responseData.translatedText;
    }};
    $('jaInput').addEventListener('input',e=>{{
        trans(e.target.value,'ja|en','jaToEnResult');
        $('lMercari').href='https://jp.mercari.com/search?keyword='+encodeURIComponent(e.target.value); $('lMercari').classList.remove('off');
        $('lYahoo').href='https://auctions.yahoo.co.jp/search/search?p='+encodeURIComponent(e.target.value); $('lYahoo').classList.remove('off');
    }});
    $('enInput').addEventListener('input',e=>{{
        trans(e.target.value,'en|ja','enToJaResult');
        $('lEbay').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(e.target.value); $('lEbay').classList.remove('off');
        $('lEbaySold').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(e.target.value)+'&LH_Sold=1&LH_Complete=1'; $('lEbaySold').classList.remove('off');
    }});
    const calc=()=>{{
        let r=parseFloat($('exRate').value)||0, c=parseFloat($('cost').value)||0, p=parseFloat($('price').value)||0;
        $('profit').textContent=Math.round((p*r)-(c+(p*r*0.15))).toLocaleString()+'円';
    }};
    ['exRate','cost','price'].forEach(id=>$(id).addEventListener('input',calc));
}})();
</script>
</body></html>
"""
    st.html(html_template)

with tab5:
    st.info("監視機能：準備中")
