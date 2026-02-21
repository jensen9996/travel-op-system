import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 系統標題
st.set_page_config(page_title="雲端旅行社管理系統", layout="wide")
st.title("🌐 雲端 OP 帳務管理系統")

# 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取現有資料
try:
    df = conn.read(worksheet="Sheet1", ttl=0)
except Exception as e:
    st.error(f"無法讀取 Google Sheets 資料，請確認連線設定是否正確。錯誤：{e}")
    st.stop()

# 確保欄位存在
COLUMNS = ["訂單編號", "客戶姓名", "行程名稱", "出發日期", "金額", "付款狀態", "備註"]
for col in COLUMNS:
    if col not in df.columns:
        df[col] = ""

# --- 側邊欄：新增訂單表單 ---
st.sidebar.header("📋 新增訂單")

order_id = st.sidebar.text_input("訂單編號")
customer_name = st.sidebar.text_input("客戶姓名")
tour_name = st.sidebar.text_input("行程名稱")
departure_date = st.sidebar.date_input("出發日期")
amount = st.sidebar.number_input("金額（元）", min_value=0, step=1)
payment_status = st.sidebar.selectbox("付款狀態", ["未付款", "已付訂金", "已全額付清"])
notes = st.sidebar.text_area("備註")

if st.sidebar.button("儲存至雲端"):
    if not order_id.strip() or not customer_name.strip() or not tour_name.strip():
        st.sidebar.error("請填寫必填欄位：訂單編號、客戶姓名、行程名稱")
    else:
        new_row = {
            "訂單編號": order_id.strip(),
            "客戶姓名": customer_name.strip(),
            "行程名稱": tour_name.strip(),
            "出發日期": str(departure_date),
            "金額": amount,
            "付款狀態": payment_status,
            "備註": notes,
        }
        updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        try:
            conn.update(worksheet="Sheet1", data=updated_df)
            st.sidebar.success("雲端同步成功！")
        except Exception as e:
            st.sidebar.error(f"儲存失敗，請確認權限與連線是否正常。錯誤：{e}")

# --- 主畫面：顯示現有訂單 ---
st.subheader("📊 現有訂單列表")

if df.empty:
    st.info("目前尚無訂單資料。請從側邊欄新增訂單。")
else:
    # 付款狀態篩選
    status_filter = st.multiselect(
        "篩選付款狀態",
        options=df["付款狀態"].dropna().unique().tolist(),
        default=df["付款狀態"].dropna().unique().tolist(),
    )
    filtered_df = df[df["付款狀態"].isin(status_filter)] if status_filter else df.iloc[0:0]
    st.dataframe(filtered_df, use_container_width=True)

    # 統計摘要
    st.subheader("💰 帳務摘要")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("訂單總數", len(df))
    with col2:
        total_amount = pd.to_numeric(df["金額"], errors="coerce").sum()
        st.metric("總金額", f"NT$ {total_amount:,.0f}")
    with col3:
        paid_count = (df["付款狀態"] == "已全額付清").sum()
        st.metric("已全額付清", paid_count)
