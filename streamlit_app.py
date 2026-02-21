import streamlit as st
import pandas as pd
import sqlite3
import os

# 系統初始化
DB_FILE = 'travel_op.db'
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
                    group_no TEXT PRIMARY KEY, departure_date TEXT, customer TEXT, 
                    pax INTEGER, price_per_pax REAL, total_revenue REAL, received_amount REAL, 
                    airline_name TEXT, ticket_cost REAL, ticket_paid REAL, 
                    land_operator TEXT, land_cost REAL, land_paid REAL, profit REAL)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="旅行社 OP 系統", layout="wide")
st.title("🚢 旅行社 OP 專業帳務管理系統")

# 這裡先簡化，確保你能跑起來
st.info("系統已成功部署！請在左側輸入資料。")

# --- 選單與基本輸入 ---
with st.sidebar.form("op_form"):
    g_no = st.text_input("團號")
    dep_date = st.date_input("出發日期")
    cust = st.text_input("客戶名稱")
    pax = st.number_input("人數", min_value=1)
    price = st.number_input("售價")
    submit = st.form_submit_button("儲存資料")

if submit and g_no:
    conn = get_connection()
    total_rev = pax * price
    conn.execute("INSERT OR REPLACE INTO groups (group_no, departure_date, customer, pax, price_per_pax, total_revenue, received_amount, ticket_cost, ticket_paid, land_cost, land_paid, profit) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (g_no, str(dep_date), cust, pax, price, total_rev, 0, 0, 0, 0, 0, 0))
    conn.commit()
    conn.close()
    st.success(f"團號 {g_no} 已存檔")

# 顯示資料
conn = get_connection()
df = pd.read_sql_query("SELECT * FROM groups", conn)
st.dataframe(df)
