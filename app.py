import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import time
from algorithms import (
    first_fit_decreasing_2d,
    best_fit_decreasing_2d,
    guillotine_cutting_2d,
    plot_placements_2d_matplotlib
)

st.title("📦 Cutting Stock Problem Optimizer")

# Initialize session state
if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "kpi_df" not in st.session_state:
    st.session_state.kpi_df = pd.DataFrame()

# Sidebar settings
st.sidebar.header("⚙️ ตั้งค่าการตัด")
sheet_width = st.sidebar.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=10.0, value=91.4, step=0.1)
price_per_meter = st.sidebar.number_input("💰 ราคาต่อหน่วย (บาท/เมตร)", min_value=0.1, value=100.0, step=0.1)
price_per_m2 = price_per_meter / (sheet_width / 100)  # แปลงเป็นบาท/ตร.เมตร

# รับออเดอร์
st.header("📥 เพิ่มออเดอร์")
input_method = st.radio("เลือกวิธีกรอกข้อมูลออเดอร์", ["กรอกข้อมูลเอง", "อัปโหลดไฟล์ CSV"])
orders = []
alert_flag = False

if input_method == "กรอกข้อมูลเอง":
    num_orders = st.number_input("จำนวนออเดอร์", min_value=1, step=1)
    for i in range(num_orders):
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input(f"🔹 ความกว้าง (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'w{i}')
        with col2:
            length = st.number_input(f"🔹 ความยาว (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'l{i}')

        if width > sheet_width and length > sheet_width:
            alert_flag = True
        orders.append((width, length))

elif input_method == "อัปโหลดไฟล์ CSV":
    uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ CSV (ต้องมีคอลัมน์ 'Width' และ 'Length')", type="csv")
    if uploaded_file:
        df_orders = pd.read_csv(uploaded_file)
        if "Width" in df_orders.columns and "Length" in df_orders.columns:
            orders = list(zip(df_orders["Width"], df_orders["Length"]))
            if any(w > sheet_width and l > sheet_width for w, l in orders):
                alert_flag = True
            st.dataframe(df_orders)
        else:
            st.error("⚠️ ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

# ถ้ามีขนาดเกิน sheet_width ทั้งสองด้าน
if alert_flag:
    st.error("🚨 ไม่สามารถคำนวณได้: มีออเดอร์ที่กว้างและยาวเกินความกว้างของแผ่นเมทัลชีท")

# เริ่มคำนวณ
if orders and not alert_flag and st.button("🚀 คำนวณ"):
    algorithms = {
        "FFD 2D": first_fit_decreasing_2d,
        "BFD 2D": best_fit_decreasing_2d,
        "Guillotine 2D": guillotine_cutting_2d
    }

    results = {}
    kpi_rows = []
    total_used_area = sum(w * l for w, l in orders)
    waste_values = {}

    for name, algo in algorithms.items():
        start_time = time.time()
        placements = algo(orders, sheet_width)
        proc_time = time.time() - start_time

        total_length_used = max(p["y"] + p["height"] for p in placements)
        total_sheet_area = sheet_width * total_length_used
        total_waste = max(0, total_sheet_area - total_used_area)
        waste_values[name] = total_waste

        kpi_rows.append({
            "Algorithm": name,
            "Total Length Used (cm)": round(total_length_used, 2),
            "Total Waste (cm²)": round(total_waste, 2),
            "Processing Time (s)": round(proc_time, 6),
        })

        results[name] = placements

    # คำนวณ cost lost
    min_waste = min(waste_values.values())
    cost_lost_values = {}

    for name, waste in waste_values.items():
        if all(w == min_waste for w in waste_values.values()):
            cost_lost = waste * price_per_m2 / 10_000
        else:
            cost_lost = (waste - min_waste) * price_per_m2 / 10_000
        cost_lost_values[name] = cost_lost

    for row in kpi_rows:
        row["Cost Lost (Baht)"] = f"{round(cost_lost_values[row['Algorithm']], 2):,}"

    st.session_state.kpi_df = pd.DataFrame(kpi_rows)
    st.session_state.results = results
    st.session_state.calculated = True

if st.session_state.calculated:
    st.subheader("📊 KPI Summary")
    st.dataframe(st.session_state.kpi_df)

    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization", list(st.session_state.results.keys()))

    # ✅ เตรียม label ถ้ามีจากไฟล์ CSV
    labels = None
    if input_method == "อัปโหลดไฟล์ CSV" and uploaded_file and "Label" in df_orders.columns:
        labels = df_orders["Label"].tolist()
    elif input_method == "อัปโหลดไฟล์ CSV":
        labels = [f"Part {i+1}" for i in range(len(st.session_state.results[selected_algo]))]

    fig = plot_placements_2d_matplotlib(st.session_state.results[selected_algo], sheet_width, labels=labels, title=selected_algo)

    # ✅ ใช้ full height ไม่บีบภาพ
    st.pyplot(fig, use_container_width=False)
