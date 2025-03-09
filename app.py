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

# --- 🛠 กำหนดค่าการตัด ---
st.sidebar.header("⚙️ ตั้งค่าการตัด")
sheet_width = st.sidebar.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=10.0, value=91.4, step=0.1)

# ✅ เพิ่มช่องใส่ราคาต่อหน่วย
price_per_meter = st.sidebar.number_input("💰 ราคาต่อหน่วย (บาท/เมตร)", min_value=0.1, value=100.0, step=0.1)

# ✅ แปลงราคา/เมตร → ราคา/เมตร²
price_per_m2 = price_per_meter / (sheet_width / 100)  # (บาท/เมตร) ÷ (เมตร)
sort_strategy = st.sidebar.radio("เลือกกลยุทธ์การเรียงลำดับ", ["area", "max_side"])

# --- 📥 รับออเดอร์ ---
st.header("📥 เพิ่มออเดอร์")
input_method = st.radio("เลือกวิธีกรอกข้อมูลออเดอร์", ["กรอกข้อมูลเอง", "อัปโหลดไฟล์ CSV"])
orders = []
alert_flag = False  # ตัวแปรเช็คว่ามีข้อผิดพลาดหรือไม่

if input_method == "กรอกข้อมูลเอง":
    num_orders = st.number_input("จำนวนออเดอร์", min_value=1, step=1)
    for i in range(num_orders):
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input(f"🔹 ความกว้าง (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'w{i}')
        with col2:
            length = st.number_input(f"🔹 ความยาว (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'l{i}')
        
        # ✅ เช็คเงื่อนไข: ถ้าทั้งสองด้าน (width & length) > sheet_width → Error
        if width > sheet_width and length > sheet_width:
            alert_flag = True  # ถ้ามีค่าเกินให้ตั้ง flag เป็น True
        
        orders.append((width, length))

elif input_method == "อัปโหลดไฟล์ CSV":
    uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ CSV (ต้องมีคอลัมน์ 'Width' และ 'Length')", type="csv")
    if uploaded_file:
        df_orders = pd.read_csv(uploaded_file)
        if "Width" in df_orders.columns and "Length" in df_orders.columns:
            orders = list(zip(df_orders["Width"], df_orders["Length"]))
            
            # ✅ เช็คว่ามีออเดอร์ไหนที่ทั้งกว้างและยาวมากกว่าความกว้างของเมทัลชีทไหม
            if any(w > sheet_width and l > sheet_width for w, l in orders):
                alert_flag = True

            st.dataframe(df_orders)
        else:
            st.error("⚠️ ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

# ✅ ถ้าผู้ใช้กรอกค่าผิด (ทั้งกว้างและยาวเกิน) ให้ขึ้น Alert และไม่ให้คำนวณ
if alert_flag:
    st.error("🚨 ไม่สามารถคำนวณได้: ขนาดของออเดอร์บางรายการมีทั้งกว้างและยาวใหญ่กว่าความกว้างของแผ่นเมทัลชีท")

if orders and not alert_flag and st.button("🚀 คำนวณ"):
    results = {}
    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    kpi_rows = []
    total_used_area = sum(w * l for w, l in orders)  # คำนวณพื้นที่ที่ใช้งานจริงทั้งหมด
    waste_values = {}

    for name, algo in algorithms.items():
        start_time = time.time()
        bins = algo(sheet_width, orders, sort_by=sort_strategy)
        proc_time = time.time() - start_time

        # คำนวณ Total Length Used (cm)
        total_length_used = sum(max(h for _, h in bin) for bin in bins)

        # คำนวณ Total Waste (cm²)
        total_sheet_area = sheet_width * total_length_used
        total_waste = max(0, total_sheet_area - total_used_area)

        waste_values[name] = total_waste  # เก็บค่า Waste ของแต่ละ Alg

        kpi_rows.append({
            "Algorithm": name,
            "Total Length Used (cm)": round(total_length_used, 2),
            "Total Waste (cm²)": round(total_waste, 2),
            "Processing Time (s)": round(proc_time, 6),
        })

        results[name] = bins

    # ✅ คำนวณต้นทุนที่เสียไป
    min_waste = min(waste_values.values())  # หาค่า Waste ที่ต่ำที่สุด
    cost_lost_values = {}
    
    for name, waste in waste_values.items():
        if all(w == min_waste for w in waste_values.values()):  # ถ้า Waste เท่ากันหมด
            cost_lost = waste * price_per_m2 / 10_000  # แปลง cm² → m²
        else:
            cost_lost = (waste - min_waste) * price_per_m2 / 10_000  # คำนวณเฉพาะ Alg ที่ Waste มากกว่า

        cost_lost_values[name] = cost_lost

    # ✅ เพิ่มค่า "Cost Lost" ใน KPI Table
    for row in kpi_rows:
        row["Cost Lost (Baht)"] = f"{round(cost_lost_values[row['Algorithm']], 2):,}"

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
