import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")

DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"

# ─────────────────────────────────────────
# データ取得・ロード
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # 必須列の存在チェックと型変換
        for col in ["ID", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "確定レート"]:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        if "メモ" not in df.columns:
            df["メモ"] = ""
        # IDを整数型に
        df["ID"] = df["ID"].astype(int)
        return df
    return pd.DataFrame(columns=[
        "ID", "日付", "担当者", "商品名", "仕入(円)",
        "eBay相場(ドル)", "売値(ドル)", "ステータス",
        "発送サイズ", "確定レート", "メモ"
    ])

def load_watch_list():
    if os.path.exists(WATCH_FILE):
        w = pd.read_csv(WATCH_FILE)
        for col in ["前回最安値", "狙う仕入れ価格"]:
            if col not in w.columns:
                w[col] = 0
        if "状態" not in w.columns:
            w["状態"] = "🆕 未チェック"
        return w
    return pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "状態"])

# ─────────────────────────────────────────
# 定数
# ─────────────────────────────────────────
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS   = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS   = ["自分", "悠太郎", "その他"]

# ─────────────────────────────────────────
# ヘッダー
# ─────────────────────────────────────────
current_rate = get_rate()

st.markdown("""
<style>
    .main-header {font-size:1.6rem; font-weight:800; color:#1A5C3A;}
    .rate-badge {
        display:inline-block; background:#f0f9f3; border:1px solid #b0d8bc;
        color:#1A5C3A; font-weight:700; border-radius:8px; padding:4px 14px; font-size:0.95rem;
    }
    [data-testid="stMetricValue"] {font-size:1.5rem !important; font-weight:800;}
</style>
""", unsafe_allow_html=True)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="main-header">📦 eBay 仕入れ・利益管理システム</p>', unsafe_allow_html=True)
with col_h2:
    st.markdown(f'<p style="text-align:right;padding-top:12px"><span class="rate-badge">💱 1 USD = {current_rate:.2f} JPY</span></p>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# データ前処理と計算
# ─────────────────────────────────────────
df = load_data()
df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
df["使用レート"] = df["確定レート"].replace(0, current_rate)

# 計算列を作成
df["純利益(円)"] = (
    df["eBay相場(ドル)"] * 0.85 * df["使用レート"]
    - df["仕入(円)"]
    - df["発送サイズ"].map(SIZE_COSTS).fillna(2000)
).astype(int)
df["売上換算(円)"] = (df["売値(ドル)"] * df["使用レート"]).astype(int)

now_month = datetime.now().month
this_month = df[df["日付"].dt.month == now_month]
sold = this_month[this_month["ステータス"].isin(["販売済み", "発送済"])]

# ─────────────────────────────────────────
# ダッシュボード
# ─────────────────────────────────────────
st.subheader("📈 今月の実績")
m1, m2, m3, m4 = st.columns(4)
m1.metric("今月 仕入れ合計", f"¥{this_month['仕入(円)'].sum():,.0f}")
m2.metric("今月 売上合計", f"¥{sold['売値(ドル)'].sum() * current_rate:,.0f}")
m3.metric("今月 確定利益", f"¥{sold['純利益(円)'].sum():,.0f}")
m4.metric("在庫件数（掲載中）", len(df[df["ステータス"] == "掲載中"]))

with st.expander("📊 担当者別・商品別 内訳を見る"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("仕入れ (担当者別)")
        if not this_month.empty:
            st.dataframe(this_month.groupby("担当者")["仕入(円)"].sum(), use_container_width=True)
    with c2:
        st.caption("売上 (担当者別・円換算)")
        if not sold.empty:
            st.dataframe((sold.groupby("担当者")["売値(ドル)"].sum() * current_rate).rename("売上(円)"), use_container_width=True)
    with c3:
        st.caption("利益 (商品別)")
        if not sold.empty:
            st.dataframe(sold[["商品名", "純利益(円)"]].set_index("商品名"), use_container_width=True)

st.divider()

# ─────────────────────────────────────────
# タブ
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 在庫管理表",
    "🔍 利益計算ツール",
    "📥 新規仕入れ登録",
    "⚡ CSV一括更新",
    "🔥 お気に入り監視"
])

# ══════════════════════════════════════════
# TAB 1 : 在庫管理表
# ══════════════════════════════════════════
with tab1:
    st.subheader("📋 在庫管理表")

    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        filter_status = st.selectbox("ステータスで絞り込み", ["すべて"] + STATUS_OPTIONS, key="filter_status")
    with col_f2:
        filter_user = st.selectbox("担当者で絞り込み", ["すべて"] + USER_OPTIONS, key="filter_user")
    with col_f3:
        search_word = st.text_input("商品名で検索", key="search_word")

    df_show = df.copy()
    if filter_status != "すべて":
        df_show = df_show[df_show["ステータス"] == filter_status]
    if filter_user != "すべて":
        df_show = df_show[df_show["担当者"] == filter_user]
    if search_word:
        df_show = df_show[df_show["商品名"].str.contains(search_word, na=False)]

    if not df_show.empty and "日付" in df_show.columns:
        df_show["日付"] = df_show["日付"].dt.strftime("%Y-%m-%d")

    df_show.insert(0, "削除", False)
    base_columns = ["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"]

    edited_df = st.data_editor(
        df_show,
        column_config={
            "削除":       st.column_config.CheckboxColumn("削除", width="small"),
            "ID":         st.column_config.NumberColumn("ID", disabled=True, format="%d"),
            "日付":       st.column_config.TextColumn("日付"),
            "ステータス": st.column_config.SelectboxColumn(options=STATUS_OPTIONS, required=True),
            "発送サイズ": st.column_config.SelectboxColumn(options=SIZE_OPTIONS),
            "担当者":     st.column_config.SelectboxColumn(options=USER_OPTIONS),
            "確定レート": st.column_config.NumberColumn(format="%.2f"),
            "仕入(円)":   st.column_config.NumberColumn(format="%d"),
            "eBay相場(ドル)": st.column_config.NumberColumn(format="%.2f"),
            "売値(ドル)": st.column_config.NumberColumn(format="%.2f"),
            "純利益(円)": st.column_config.NumberColumn(format="%d", disabled=True),
            "売上換算(円)": st.column_config.NumberColumn(format="%d", disabled=True),
            "使用レート": st.column_config.NumberColumn(format="%.2f", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="main_editor"
    )

    if st.button("💾 変更を保存", type="primary"):
        saved_edited = edited_df[edited_df["削除"] == False].copy()
        new_rows_list = []
        updated_ids = set()

        for _, row in saved_edited.iterrows():
            pid = row.get("ID", 0)
            if pd.isna(pid) or pid == 0 or int(pid) not in df["ID"].values:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                while next_id in updated_ids:
                    next_id += 1
                row["ID"] = next_id
                row["日付"] = datetime.now().strftime("%Y-%m-%d") if pd.isna(row.get("日付")) else row["日付"]
                new_dict = {col: row.get(col, "") for col in base_columns}
                if new_dict["ステータス"] in ["販売済み", "発送済"] and (pd.isna(new_dict["確定レート"]) or new_dict["確定レート"] == 0):
                    new_dict["確定レート"] = current_rate
                new_rows_list.append(new_dict)
                updated_ids.add(next_id)
            else:
                pid = int(pid)
                updated_ids.add(pid)
                if row["ステータス"] in ["販売済み", "発送済"] and row["確定レート"] == 0:
                    row["確定レート"] = current_rate
                for col in base_columns:
                    if col in row:
                        df.loc[df["ID"] == pid, col] = row[col]

        visible_ids = set(df_show["ID"].dropna().astype(int).values)
        deleted_ids = visible_ids - updated_ids
        if deleted_ids:
            df = df[~df["ID"].isin(deleted_ids)]

        if new_rows_list:
            df_new = pd.DataFrame(new_rows_list)
            df = pd.concat([df, df_new], ignore_index=True)

        df[base_columns].to_csv(DB_FILE, index=False)
        st.success("✅ 変更を安全に保存しました！")
        st.rerun()

    st.caption("📊 ステータス別件数")
    if not df.empty:
        summary = df.groupby("ステータス").size().reset_index(name="件数")
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# TAB 2 : 利益計算ツール
# ══════════════════════════════════════════
with tab2:
    st.subheader("🔍 eBay利益計算ツール")
    st.caption("メルカリ・ヤフオクのURLを入れると仕入れ価格を自動抽出。英語翻訳とeBayリサーチリンクも自動生成します。")

    # 105行目: f""" からただの """ に変更して閉じタグのエラーを完全に防止
    html_calc_template = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<style>
:root{
  --bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;
  --dim:#9ca89e;--accent:#B79740;--teal:#1A5C3A;--teal2:#2D7A4F;
  --pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);
  --r:14px;--rs:8px;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:var(--bg);color:var(--text);padding:10px 12px 280px;}
.sec{background:var(--card);margin:8px 0;border-radius:var(--r);padding:14px;
  border:1px solid var(--border);}
.sec.highlight{border:2px solid var(--accent);}
.lbl{display:block;font-size:11px;font-weight:600;color:var(--sub);margin-bottom:4px;letter-spacing:.3px;}
input,select{width:100%;padding:10px 11px;border:1px solid var(--iborder);border-radius:var(--rs);
  font-size:15px;background:var(--ibg);color:var(--text);}
input:focus,select:focus{outline:2px solid var(--teal);border-color:transparent;}
.mb{margin-bottom:11px;}
.btn{width:100%;padding:11px;background:linear-gradient(135deg,var(--teal),var(--teal2));
  color:#fff;border:none;border-radius:var(--rs);font-size:14px;font-weight:700;cursor:pointer;margin-top:6px;}
.btn:active{opacity:.85;}
.toggle{display:flex;border:1px solid var(--iborder);border-radius:var(--rs);overflow:hidden;background:var(--ibg);}
.toggle button{flex:1;padding:9px;border:none;background:transparent;color:var(--dim);
  font-size:13px;font-weight:700;cursor:pointer;transition:all .15s;}
.toggle button.on{background:linear-gradient(135deg,var(--teal),var(--teal2));color:#fff;}
.trans{background:rgba(26,92,58,.07);padding:10px;border-radius:var(--rs);
  font-size:13px;min-height:36px;display:flex;align-items:center;color:var(--sub);}
.links-row{display:flex;align-items:center;gap:8px;margin-top:7px;}
.tag{font-size:9px;font-weight:800;color:#fff;padding:2px 6px;border-radius:4px;white-space:nowrap;}
.tag.ja{background:#555;}.tag.en{background:var(--teal);}
.link-group{display:flex;gap:5px;flex-wrap:wrap;}
.link-group a{padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:700;
  color:var(--text);background:var(--ibg);border:1px solid var(--iborder);transition:.1s;}
.link-group a:hover{background:var(--teal);color:#fff;border-color:var(--teal);}
.link-group a.off{opacity:.25;pointer-events:none;}
.info-row{background:rgba(183,151,64,.1);padding:9px 12px;border-radius:var(--rs);
  font-size:13px;display:flex;justify-content:space-between;align-items:center;}
.panel{position:fixed;bottom:0;left:0;right:0;background:#fafbf9;
  border-top:1px solid var(--border);padding:11px 14px;box-shadow:0 -4px 12px rgba(0,0,0,.05);z-index:99;}
.profits{display:flex;gap:0;margin-bottom:7px;border-bottom:1px solid var(--border);padding-bottom:8px;}
.pcol{flex:1;text-align:center;}
.pcol+.pcol{border-left:1px solid var(--border);}
.pcol .lbl2{font-size:10px;color:var(--sub);margin-bottom:2px;}
.pcol .val{font-size:22px;font-weight:900;}
.pcol .sub{font-size:11px;}
.summary{display:flex;justify-content:space-around;font-size:11px;color:var(--sub);margin-bottom:5px;}
.toggle-detail{background:none;border:none;color:var(--accent);font-weight:700;cursor:pointer;
  font-size:11px;display:block;margin:0 auto;}
.breakdown{display:none;padding-top:8px;border-top:1px solid var(--border);margin-top:6px;}
.breakdown.open{display:block;}
.brow{display:flex;justify-content:space-between;font-size:11px;padding:3px 0;}
.pos{color:var(--pp);}.neg{color:var(--pn);}
.err{color:var(--pn);font-size:12px;margin-top:4px;display:none;}
</style></head>
<body>

<div class="sec highlight">
  <label class="lbl">🔗 仕入れ元URL（メルカリ・ヤフオク）</label>
  <div class="mb"><input id="importUrl" type="text" placeholder="https://jp.mercari.com/item/...  または ヤフオクURL"></div>
  <button class="btn" id="btnImport">URLから商品名・価格を自動抽出</button>
  <div class="err" id="importErr">⚠️ 抽出に失敗しました。手動で入力してください。</div>
</div>

<div class="sec">
  <div class="mb">
    <label class="lbl">商品名（日本語）</label>
    <input id="productName" type="text" placeholder="例: ポケモンカード リザードン SAR">
  </div>
  <div class="mb">
    <label class="lbl">英語翻訳（自動）</label>
    <div class="trans" id="translatedName">商品名を入力すると自動翻訳されます</div>
  </div>
  <div class="links-row">
    <span class="tag ja">JP</span>
    <div class="link-group">
      <a href="#" class="off" id="lMercari" target="_blank">メルカリ</a>
      <a href="#" class="off" id="lYahoo" target="_blank">ヤフオク</a>
    </div>
  </div>
  <div class="links-row">
    <span class="tag en">EN</span>
    <div class="link-group">
      <a href="#" class="off" id="lEbay" target="_blank">eBay 販売中</a>
      <a href="#" class="off" id="lEbaySold" target="_blank">eBay Sold</a>
    </div>
  </div>
</div>

<div class="sec">
  <label class="lbl">為替レート（USD → JPY）</label>
  <input id="exchangeRate" type="text" value="__CURRENT_RATE__">
</div>

<div class="sec">
  <div class="mb">
    <label class="lbl">仕入れ価格（円）</label>
    <input id="costPrice" type="text" placeholder="0">
  </div>
  <div class="mb">
    <label class="lbl">eBay 販売価格（商品のみ）</label>
    <div style="display:flex;gap:10px;">
      <div style="flex:2"><input id="itemPrice" type="text" placeholder="例: 80"></div>
      <div style="flex:1"><div class="toggle" id="curToggle">
        <button class="on" data-v="USD">USD</button>
        <button data-v="JPY">JPY</button>
      </div></div>
    </div>
  </div>
  <div class="mb">
    <label class="lbl">eBay 送料（バイヤー請求分）</label>
    <input id="buyerShipping" type="text" placeholder="0 (送料無料なら0)">
  </div>
</div>

<div class="sec">
  <label class="lbl">カテゴリ（eBay手数料率）</label>
  <select id="category">
    <option value="figures">フィギュア・玩具・トレカ（13.6%）</option>
    <option value="apparel">アパレル・衣類（13.6%）</option>
    <option value="watches">時計（15.0%）</option>
    <option value="cameras">カメラ（13.6%）</option>
    <option value="games">ゲーム（13.6%）</option>
    <option value="other">その他（13.6%）</option>
  </select>
</div>

<div class="sec">
  <div class="mb">
    <label class="lbl">燃油サーチャージ（%）</label>
    <input id="fuelSurcharge" type="text" value="46">
  </div>
  <div class="mb">
    <label class="lbl">国際送料 ベース（円）</label>
    <input id="baseShipping" type="text" value="2500">
  </div>
  <div class="info-row">
    <span>送料合計（サーチャージ込）</span>
    <strong id="shippingTotal">---円</strong>
  </div>
</div>

<div class="panel">
  <div class="profits">
    <div class="pcol">
      <div class="lbl2">最終利益</div>
      <div class="val pos" id="pProfit">---</div>
      <div class="sub" id="pRate">利益率 ---%</div>
    </div>
    <div class="pcol">
      <div class="lbl2">消費税還付込み利益</div>
      <div class="val pos" id="pRefund">---</div>
      <div class="sub" id="pRefundNote" style="color:var(--teal)">還付額 ---</div>
    </div>
  </div>
  <div class="summary">
    <span>売上: <strong id="pRevenue">---</strong></span>
    <span>経費合計: <strong id="pExpense">---</strong></span>
  </div>
  <button class="toggle-detail" id="btnDetail">内訳を見る ▼</button>
  <div class="breakdown" id="breakdown">
    <div class="brow"><span>eBay手数料 (FVF + 固定 + 国際)</span><span id="dFvf">---</span></div>
    <div class="brow"><span>eBay手数料の消費税 (10%)</span><span id="dFvfTax">---</span></div>
    <div class="brow"><span>国際送料</span><span id="dShip">---</span></div>
    <div class="brow"><span>仕入れ原価</span><span id="dCost">---</span></div>
    <div class="brow" style="color:var(--teal)"><span>消費税還付予測</span><span id="dRefund">---</span></div>
  </div>
</div>

<script>
(function(){
  const CAT = {
    figures:{fvf:13.6}, apparel:{fvf:13.6}, watches:{fvf:15.0},
    cameras:{fvf:13.6}, games:{fvf:13.6}, other:{fvf:13.6}
  };
  const $=id=>document.getElementById(id);
  const num=id=>parseFloat(($(id).value||'').replace(/,/g,''))||0;
  let cur='USD', eng='';

  $('btnImport').addEventListener('click', async()=>{
    const url=$('importUrl').value.trim();
    if(!url)return;
    $('btnImport').textContent='解析中...';
    $('importErr').style.display='none';
    try{
      const res=await fetch('https://api.allorigins.win/get?url='+encodeURIComponent(url));
      const {contents:html}=await res.json();
      let title='',price='';
      const tM=html.match(/<meta property="og:title" content="([^"]+)"/);
      if(tM) title=tM[1].replace(/ - メルカリ/,'').replace(/ - ヤフオク!/,'');
      const pM=html.match(/<meta property="product:price:amount" content="([^"]+)"/);
      if(pM) price=pM[1];
      if(price){
        $('costPrice').value=price;
        $('productName').value=title;
        $('productName').dispatchEvent(new Event('input'));
        $('btnImport').textContent='✅ 抽出完了！';
      }else{
        $('importErr').style.display='block';
        $('btnImport').textContent='URLから自動抽出';
      }
    }catch(e){
      $('importErr').style.display='block';
      $('btnImport').textContent='URLから自動抽出';
    }
    setTimeout(()=>$('btnImport').textContent='URLから商品名・価格を自動抽出',3000);
  });

  let tTimer;
  $('productName').addEventListener('input',function(){
    clearTimeout(tTimer);
    const txt=this.value.trim();
    if(!txt)return;
    $('lMercari').href='https://jp.mercari.com/search?keyword='+encodeURIComponent(txt);
    $('lMercari').classList.remove('off');
    $('lYahoo').href='https://auctions.yahoo.co.jp/search/search?p='+encodeURIComponent(txt);
    $('lYahoo').classList.remove('off');
    tTimer=setTimeout(async()=>{
      try{
        const r=await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(txt)+'&langpair=ja|en');
        const d=await r.json();
        if(d.responseData){
          eng=d.responseData.translatedText;
          $('translatedName').textContent=eng;
          $('lEbay').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(eng);
          $('lEbay').classList.remove('off');
          $('lEbaySold').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(eng)+'&LH_Sold=1&LH_Complete=1';
          $('lEbaySold').classList.remove('off');
          calc();
        }
      }catch(e){}
    },600);
  });

  function fmt(n){return Math.round(n).toLocaleString()+'円';}
  function calc(){
    const rate=num('exchangeRate'), cost=num('costPrice'),
          item=num('itemPrice'), bShip=num('buyerShipping'),
          fuel=num('fuelSurcharge'), base=num('baseShipping');
    const totalShip=Math.round(base*(1+fuel/100));
    $('shippingTotal').textContent=totalShip.toLocaleString()+'円';
    if(!rate||!item)return;
    const saleUSD=cur==='USD'?item+bShip:(item+bShip)/rate;
    const rev=saleUSD*rate;
    const fvfRate=CAT[$('category').value].fvf/100;
    const fvf=saleUSD*fvfRate*rate;
    const fixed=0.40*rate, intl=saleUSD*0.0135*rate;
    const totalFee=fvf+fixed+intl;
    const feeTax=totalFee*0.10;
    const expense=totalFee+feeTax+totalShip+cost;
    const profit=rev-expense;
    const refund=(cost*10/110)+feeTax;
    const profitR=profit+refund;
    $('pProfit').textContent=fmt(profit);
    $('pProfit').className='val '+(profit>=0?'pos':'neg');
    $('pRate').textContent='利益率 '+(rev>0?(profit/rev*100).toFixed(1):0)+'%';
    $('pRefund').textContent=fmt(profitR);
    $('pRefundNote').textContent='還付額 +'+fmt(refund);
    $('pRevenue').textContent=fmt(rev);
    $('pExpense').textContent=fmt(expense);
    $('dFvf').textContent=fmt(totalFee);
    $('dFvfTax').textContent=fmt(feeTax);
    $('dShip').textContent=fmt(totalShip);
    $('dCost').textContent=fmt(cost);
    $('dRefund').textContent='+'+fmt(refund);
  }

  ['exchangeRate','costPrice','itemPrice','buyerShipping','fuelSurcharge','baseShipping','category']
    .forEach(id=>$(id).addEventListener('input',calc));

  $('curToggle').addEventListener('click',e=>{
    const btn=e.target.closest('button');if(!btn)return;
    $('curToggle').querySelectorAll('button').forEach(b=>b.classList.remove('on'));
    btn.classList.add('on'); cur=btn.dataset.v; calc();
  });

  $('btnDetail').addEventListener('click',()=>{
    const bd=$('breakdown'); const open=bd.classList.toggle('open');
    $('btnDetail').textContent=open?'内訳を閉じる ▲':'内訳を見る ▼';
  });
})();
</script>
</body></html>"""
    
    # 180行目の閉じ忘れエラー対策の締めくくり：Python側で文字列置換
    html_calc = html_calc_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}")
    components.html(html_calc, height=820, scrolling=True)

# ══════════════════════════════════════════
# TAB 3 : 新規仕入れ登録
# ══════════════════════════════════════════
with tab3:
    st.subheader("📥 新規仕入れ登録")

    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name  = st.text_input("商品名 *", placeholder="例: ポケカ リザードン SAR")
            user  = st.selectbox("担当者 *", USER_OPTIONS)
            cost  = st.number_input("仕入合計（円）", min_value=0, step=100)
        with c2:
            size   = st.selectbox("発送サイズ", SIZE_OPTIONS)
            status = st.selectbox("初期ステータス", STATUS_OPTIONS)
            ebay_p = st.number_input("eBay相場（ドル）※任意", min_value=0.0, step=0.5)
            memo   = st.text_input("メモ（任意）")

        submitted = st.form_submit_button("✅ 登録する", type="primary", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("商品名を入力してください")
            else:
                next_id = int(df["ID"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "ID": next_id,
                    "日付": datetime.now().strftime("%Y-%m-%d"),
                    "担当者": user,
                    "商品名": name.strip(),
                    "仕入(円)": cost,
                    "eBay相場(ドル)": ebay_p,
                    "売値(ドル)": 0,
                    "発送サイズ": size,
                    "ステータス": status,
                    "確定レート": 0,
                    "メモ": memo
                }])
                
                save = pd.concat([df[base_columns], new_row], ignore_index=True)
                save.to_csv(DB_FILE, index=False)
                st.success(f"✅「{name}」を登録しました！")
                st.rerun()

    st.divider()
    st.caption("📋 最近登録した商品（直近10件）")
    if not df.empty:
        recent = df.sort_values("ID", ascending=False).head(10)
        st.dataframe(recent[["ID","日付","担当者","商品名","仕入(円 toggle)","ステータス"]].rename(columns={"仕入(円 toggle)": "仕入(円)"}), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# TAB 4 : CSV一括更新
# ══════════════════════════════════════════
with tab4:
    st.subheader("⚡ CSV一括アップデート（eBay相場の反映）")

    with st.expander("📄 CSVフォーマットについて"):
        st.markdown("""
CSVには以下の列が必要です（列名は柔軟に認識します）：

| 列 | 認識するキーワード |
|---|---|
| 商品名 | `商品名`, `Name`, `タイトル` |
| eBay相場 | `eBay`, `相場`, `Price`, `ドル` |

文字コードは **UTF-8** または **Shift-JIS** どちらでも対応。
""")

    up_file = st.file_uploader("CSVファイルをアップロード", type=["csv"])

    if up_file:
        try:
            try:
                rdf = pd.read_csv(up_file, encoding="utf-8")
            except:
                up_file.seek(0)
                rdf = pd.read_csv(up_file, encoding="shift-jis")

            st.caption(f"読み込み: {len(rdf)}行 / 列: {list(rdf.columns)}")
            st.dataframe(rdf.head(5), use_container_width=True)

            name_col = [c for c in rdf.columns if any(k in c for k in ["商品名","Name","タイトル"])]
            ebay_col = [c for c in rdf.columns if any(k in c for k in ["eBay","相場","Price","ドル"])]

            if not name_col or not ebay_col:
                st.error("❌ CSVに「商品名」または「eBay相場」の列が見つかりません。")
            else:
                st.info(f"商品名列: `{name_col[0]}` eBay相場列: `{ebay_col[0]}`")

                if st.button("⚡ eBay相場を反映する", type="primary"):
                    cnt = 0
                    for _, row in rdf.iterrows():
                        csv_name  = str(row[name_col[0]]).strip()
                        csv_price = pd.to_numeric(row[ebay_col[0]], errors="coerce")
                        mask = df["商品名"].str.strip() == csv_name
                        if mask.any() and not pd.isna(csv_price):
                            df.loc[mask, "eBay相場(ドル)"] = float(csv_price)
                            cnt += 1
                    
                    df[base_columns].to_csv(DB_FILE, index=False)
                    st.success(f"✅ {cnt}件 のeBay相場を更新しました！")
                    st.rerun()
        except Exception as e:
            st.error(f"読み込みエラー: {e}")

    st.divider()
    st.subheader("💾 現在のデータをCSVでダウンロード")
    if not df.empty:
        st.download_button(
            label="📥 管理データをCSVでダウンロード",
            data=df[base_columns].to_csv(index=False, encoding="utf-8-sig"),
            file_name=f"ebay_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ══════════════════════════════════════════
# TAB 5 : お気に入り監視
# ══════════════════════════════════════════
with tab5:
    st.subheader("🔥 お気に入り・新着監視リスト")
    w_df = load_watch_list()

    with st.expander("➕ 新しい商品を監視登録する"):
        with st.form("watch_form", clear_on_submit=True):
            wc1, wc2 = st.columns(2)
            with wc1:
                w_name  = st.text_input("監視キーワード", placeholder="例: ポケカ リザードン SAR")
            with wc2:
                w_price = st.number_input("狙う仕入れ価格（円以下）", min_value=0, step=500)
            if st.form_submit_button("📌 登録", type="primary"):
                if w_name.strip():
                    new_w = pd.DataFrame([{
                        "商品名": w_name.strip(),
                        "狙う仕入れ価格": w_price,
                        "前回最安値": 0,
                        "状態": "🆕 未チェック"
                    }])
                    pd.concat([w_df, new_w], ignore_index=True).to_csv(WATCH_FILE, index=False)
                    st.success(f"「{w_name}」を監視リストに登録しました！")
                    st.rerun()

    if not w_df.empty:
        st.markdown("### ⚡ ワンクリック新着リサーチ")
        st.caption("登録した全商品のメルカリ・ヤフオク新着ページをまとめてブラウザで開きます。")

        links_js = "".join([
            f"window.open('https://jp.mercari.com/search?keyword={requests.utils.quote(str(r[\"商品名\"]))}&sort=created_time&order=desc','_blank');"
            f"window.open('https://auctions.yahoo.co.jp/search/search?p={requests.utils.quote(str(r[\"商品名\"]))}&s1=new&o1=d','_blank');"
            for _, r in w_df.iterrows()
        ])
        open_html = f"<script>{links_js}</script>"

        if st.button("🚀 全商品の新着ページを一括で開く", use_container_width=True):
            components.html(open_html, height=0)
            st.info("ブラウザの別タブで開きました。ポップアップがブロックされている場合は許可してください。")

    st.divider()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 メルカリ新着チェック（自動更新）", use_container_width=True):
            with st.spinner("各商品の最新出品を確認中..."):
                import re
                for idx, row in w_df.iterrows():
                    try:
                        url = f"https://jp.mercari.com/search?keyword={requests.utils.quote(str(row['商品名']))}&sort=created_time&order=desc"
                        proxy = "https://api.allorigins.win/get?url=" + requests.utils.quote(url)
                        html = requests.get(proxy, timeout=6).json().get("contents","")
                        prices = [int(p) for p in re.findall(r'"price":\s*(\d+)', html)]
                        if prices:
                            latest = prices[0]
                            prev   = int(row["前回最安値"])
                            w_df.loc[idx, "状態"] = "🔥 新着あり！" if (prev > 0 and latest != prev) else "✅ 変化なし"
                            w_df.loc[idx, "前回最安値"] = latest
                        else:
                            w_df.loc[idx, "状態"] = "⚠️ 取得失敗"
                    except:
                        w_df.loc[idx, "状態"] = "⚠️ エラー"
                w_df.to_csv(WATCH_FILE, index=False)
                st.rerun()

    st.markdown("### 📋 監視リスト")
    if w_df.empty:
        st.info("まだ監視商品が登録されていません。")
    else:
        w_df.insert(0, "削除", False)
        edited_w = st.data_editor(
            w_df,
            column_config={
                "削除":             st.column_config.CheckboxColumn("削除", width="small"),
                "状態":             st.column_config.TextColumn("ステータス"),
                "前回最安値":       st.column_config.NumberColumn("前回価格(円)", format="%d"),
                "狙う仕入れ価格":   st.column_config.NumberColumn("目標価格(円)", format="%d"),
            },
            use_container_width=True, hide_index=True
        )
        if st.button("💾 監視リストを保存"):
            save_w = edited_w[edited_w["削除"] == False].drop(columns=["削除"], errors="ignore")
            save_w.to_csv(WATCH_FILE, index=False)
            st.success("✅ 保存しました")
            st.rerun()
