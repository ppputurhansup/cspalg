import streamlit as st
import pandas as pd
import time
from algorithms import (
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf_matplotlib
)

st.title("📦 Cutting Stock Problem Optimizer")

# 🔹 กำหนดค่าเริ่มต้นให้ session_state
if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "kpi_df" not in st.session_state:
    st.session_state.kpi_df = pd.DataFrame()

# --- 🛠 กำหนดค่าพารามิเตอร์ ---
st.sidebar.header("⚙️ ตั้งค่าการตัด")
sheet_width = st.sidebar.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=10.0, value=91.4, step=0.1)
sort_strategy = st.sidebar.radio("เลือกกลยุทธ์การเรียงลำดับ", ["area", "max_side"])

# --- 📥 รับออเดอร์ ---
st.header("📥 เพิ่มออเดอร์")
input_method = st.radio("เลือกวิธีกรอกข้อมูลออเดอร์", ["กรอกข้อมูลเอง", "อัปโหลดไฟล์ CSV"])
orders = []

if input_method == "กรอกข้อมูลเอง":
    num_orders = st.number_input("จำนวนออเดอร์", min_value=1, step=1)
    for i in range(num_orders):
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input(f"🔹 ความกว้าง (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'w{i}')
        with col2:
            length = st.number_input(f"🔹 ความยาว (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'l{i}')
        orders.append((width, length))

elif input_method == "อัปโหลดไฟล์ CSV":
    uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ CSV (ต้องมีคอลัมน์ 'Width' และ 'Length')", type="csv")
    if uploaded_file:
        df_orders = pd.read_csv(uploaded_file)
        if "Width" in df_orders.columns and "Length" in df_orders.columns:
            orders = list(zip(df_orders["Width"], df_orders["Length"]))
            st.dataframe(df_orders)
        else:
            st.error("⚠️ ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

if orders and st.button("🚀 คำนวณ"):
    results = {}
    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    kpi_rows = []
    total_used_area = sum(w * l for w, l in orders)  # คำนวณพื้นที่ที่ใช้งานจริงทั้งหมด

    for name, algo in algorithms.items():
        start_time = time.time()
        bins = algo(sheet_width, orders, sort_by=sort_strategy)
        proc_time = time.time() - start_time

        # คำนวณ Total Length Used (cm)
        total_length_used = sum(max(h for _, h in bin) for bin in bins)

        # คำนวณ Total Waste (cm²)
        total_sheet_area = sheet_width * total_length_used
        total_waste = max(0, total_sheet_area - total_used_area)

        kpi_rows.append({
            "Algorithm": name,
            "Total Length Used (cm)": round(total_length_used, 2),
            "Total Waste (cm²)": round(total_waste, 2),
            "Processing Time (s)": round(proc_time, 6),
        })

        results[name] = bins

    st.session_state.kpi_df = pd.DataFrame(kpi_rows)
    st.session_state.results = results
    st.session_state.calculated = True

# --- 📊 แสดง KPI Summary ---
if st.session_state.calculated:
    st.subheader("📊 KPI Summary")
    st.dataframe(st.session_state.kpi_df)

    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization", list(st.session_state.results.keys()))
    fig = plot_placements_shelf_matplotlib(st.session_state.results[selected_algo], sheet_width, selected_algo)
    st.pyplot(fig)
