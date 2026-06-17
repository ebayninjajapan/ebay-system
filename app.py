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
    # keyを指定して重複エラーを回避
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="main_table")
    if st.button("💾 スプレッドシートに保存"):
        save_to_sheet(edited)
        st.success("保存完了")
        st.rerun()

with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    current_rate = get_rate()
    
    # CSS/JSの波括弧を{{ }}に二重化してPythonの誤解を防いでいます
    html_calc = f"""
<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<style>
:root{{--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;--dim:#9ca89e;--accent:#B79740;--teal:#1A5C3A;--teal2:#2D7A4F;--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);padding:10px 12px 280px;}}
.sec{{background:var(--card);margin:8px 0;border-radius:var(--r);padding:14px;border:1px solid var(--border);}}
.lbl{{display:block;font-size:11px;font-weight:600;color:var(--sub);margin-bottom:4px;}}
input,select{{width:100%;padding:10px 11px;border:1px solid var(--iborder);border-radius:var(--rs);font-size:15px;background:var(--ibg);color:var(--text);}}
.mb{{margin-bottom:11px;}}
.trans-box{{display:flex;gap:6px;align-items:stretch;}}
.trans{{flex:1;background:rgba(26,92,58,.06);padding:10px;border-radius:var(--rs);font-size:13px;min-height:36px;display:flex;align-items:center;color:var(--teal);font-weight:700;word-break:break-all;}}
.btn-gtrans{{padding:0 12px;background:#4285F4;color:#fff;border:none;border-radius:var(--rs);font-size:11px;font-weight:bold;cursor:pointer;display:flex;align-items:center;text-decoration:none;}}
.links-title{{font-size:11px;font-weight:700;color:var(--sub);margin:14px 0 6px;}}
.links-row{{display:flex;gap:8px;margin-bottom:10px;}}
.btn-search{{flex:1;text-align:center;padding:11px 5px;border-radius:var(--rs);text-decoration:none;font-size:12px;font-weight:800;color:#fff;display:block;box-shadow:0 2px 4px rgba(0,0,0,.08);}}
.btn-search.mercari{{background:linear-gradient(135deg,#e32b2b,#b51212);}}
.btn-search.yahoo{{background:linear-gradient(135deg,#ffaa00,#cc8800);color:#1a1a1a;}}
.btn-search.ebay-live{{background:linear-gradient(135deg,#0064d2,#0050a5);}}
.btn-search.ebay-sold{{background:linear-gradient(135deg,#2d7a4f,#1a5c3a);}}
.btn-search.off{{opacity:.3;pointer-events:none;background:#ccc !important;color:#666;}}
.panel{{position:fixed;bottom:0;left:0;right:0;background:#fafbf9;border-top:1px solid var(--border);padding:11px 14px;box-shadow:0 -4px 12px rgba(0,0,0,.05);z-index:99;}}
.profits{{display:flex;margin-bottom:7px;border-bottom:1px solid var(--border);padding-bottom:8px;}}
.pcol{{flex:1;text-align:center;}}
.pcol .val{{font-size:22px;font-weight:900;}}
.pos{{color:var(--pp);}}.neg{{color:var(--pn);}}
.summary{{display:flex;justify-content:space-around;font-size:11px;color:var(--sub);}}
.split-grid{{display:flex;gap:12px;}}
.split-col{{flex:1;}}
</style></head>
<body>
<div class="split-grid">
  <div class="sec split-col" style="border-top:4px solid #e32b2b;">
    <div class="mb"><label class="lbl">🇯🇵 日本語の商品名を入力</label><input id="jaInput" type="text" placeholder="例：デジモン ぬいぐるみ"></div>
    <div class="mb"><label class="lbl">🇺🇸 自動英語訳</label><div class="trans-box"><div class="trans" id="jaToEnResult">英語に翻訳されます</div><a href="#" id="gTransJa" class="btn-gtrans" target="_blank">G翻訳↗</a></div></div>
  </div>
  <div class="sec split-col" style="border-top:4px solid #0064d2;">
    <div class="mb"><label class="lbl">🇺🇸 英語の商品名・型番を入力</label><input id="enInput" type="text" placeholder="例：Nikon F3 Camera"></div>
    <div class="mb"><label class="lbl">🇯🇵 自動日本語訳</label><div class="trans-box"><div class="trans" id="enToJaResult">日本語に翻訳されます</div><a href="#" id="gTransEn" class="btn-gtrans" target="_blank">G翻訳↗</a></div></div>
  </div>
</div>
<div class="sec" style="background:#f9fbf9;">
  <div class="links-title" style="margin-top:0;">🇯🇵 国内仕入れ元を検索（日本語ワード連動）</div>
  <div class="links-row">
    <a href="#" class="btn-search mercari off" id="lMercari" target="_blank">🔴 メルカリで検索</a>
    <a href="#" class="btn-search yahoo off" id="lYahoo" target="_blank">🟡 ヤフオクで検索</a>
  </div>
  <div class="links-title">🇺🇸 海外eBay相場を検索（英語ワード連動）</div>
  <div class="links-row">
    <a href="#" class="btn-search ebay-live off" id="lEbay" target="_blank">🔵 eBay (販売中)</a>
    <a href="#" class="btn-search ebay-sold off" id="lEbaySold" target="_blank">🟢 eBay (売れ済/Sold)</a>
  </div>
</div>
<div class="sec">
  <div class="mb"><label class="lbl">為替レート (1ドルあたり)</label><input id="exchangeRate" type="text" value="{current_rate:.2f}"></div>
  <div class="mb"><label class="lbl">仕入れ価格（円）</label><input id="costPrice" type="text" value="0"></div>
  <div class="mb"><label class="lbl">eBay 販売価格 (ドル入力)</label><input id="itemPrice" type="text" value="0"></div>
</div>
<div class="panel">
  <div class="profits">
    <div class="pcol"><div class="lbl">最終利益</div><div class="val pos" id="pProfit">0円</div><div id="pRate" style="font-size:11px;">利益率 0%</div></div>
  </div>
  <div class="summary"><span>売上: <strong id="pRevenue">0円</strong></span><span>経費: <strong id="pExpense">0円</strong></span></div>
</div>
<script>
(function(){{
  const $=id=>document.getElementById(id);
  const num=id=>parseFloat(($(id).value||'').replace(/,/g,''))||0;
  let currentJa = ''; let currentEn = '';
  function updateButtons() {{
    if(currentJa) {{ $('lMercari').href='https://jp.mercari.com/search?keyword='+encodeURIComponent(currentJa); $('lMercari').classList.remove('off'); $('lYahoo').href='https://auctions.yahoo.co.jp/search/search?p='+encodeURIComponent(currentJa); $('lYahoo').classList.remove('off'); }} else {{ $('lMercari').classList.add('off'); $('lYahoo').classList.add('off'); }}
    if(currentEn) {{ $('lEbay').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(currentEn); $('lEbay').classList.remove('off'); $('lEbaySold').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(currentEn)+'&LH_Sold=1&LH_Complete=1'; $('lEbaySold').classList.remove('off'); }} else {{ $('lEbay').classList.add('off'); $('lEbaySold').classList.add('off'); }}
  }}
  $('jaInput').addEventListener('input', function(){{
    const val = this.value.trim(); $('enInput').value = ''; if(!val) {{ $('jaToEnResult').textContent = '英語に翻訳されます'; $('gTransJa').href = '#'; currentJa = ''; currentEn = ''; updateButtons(); return; }}
    currentJa = val; $('gTransJa').href = 'https://translate.google.com/?sl=ja&tl=en&text=' + encodeURIComponent(val);
    setTimeout(async()=>{{
      if($('jaInput').value.trim() !== val) return;
      try {{ const r = await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(val)+'&langpair=ja|en'); const d = await r.json(); if(d.responseData && d.responseData.translatedText) {{ currentEn = d.responseData.translatedText; $('jaToEnResult').textContent = currentEn; updateButtons(); calc(); }} }} catch(e){{}}
    }}, 400);
  }});
  $('enInput').addEventListener('input', function(){{
    const val = this.value.trim(); $('jaInput').value = ''; if(!val) {{ $('enToJaResult').textContent = '日本語に翻訳されます'; $('gTransEn').href = '#'; currentJa = ''; currentEn = ''; updateButtons(); return; }}
    currentEn = val; $('gTransEn').href = 'https://translate.google.com/?sl=en&tl=ja&text=' + encodeURIComponent(val);
    setTimeout(async()=>{{
      if($('enInput').value.trim() !== val) return;
      try {{ const r = await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(val)+'&langpair=en|ja'); const d = await r.json(); if(d.responseData && d.responseData.translatedText) {{ let transText = d.responseData.translatedText; if (transText.toLowerCase() === val.toLowerCase()) {{ currentJa = val; $('enToJaResult').textContent = "⚠️直訳不可"; }} else {{ currentJa = transText; $('enToJaResult').textContent = currentJa; }} updateButtons(); calc(); }} }} catch(e){{}}
    }}, 400);
  }});
  function calc(){{
    const rate=num('exchangeRate'), cost=num('costPrice'), item=num('itemPrice'); if(!rate)return;
    const rev=item*rate; const expense=cost+(rev*0.15); const profit=rev-expense;
    $('pProfit').textContent=Math.round(profit).toLocaleString()+'円'; $('pProfit').className='val '+(profit>=0?'pos':'neg');
    $('pRate').textContent='利益率 '+(rev>0?(profit/rev*100).toFixed(1):0)+'%';
    $('pRevenue').textContent=Math.round(rev).toLocaleString()+'円'; $('pExpense').textContent=Math.round(expense).toLocaleString()+'円';
  }}
  ['exchangeRate','costPrice','itemPrice'].forEach(id=>$(id).addEventListener('input',calc));
}})();
</script>
</body></html>
"""
    st.html(html_calc)

with tab5:
    st.info("監視機能：移植準備中")
