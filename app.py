import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import time
from algorithms import (
    first_fit_decreasing_2d,
    best_fit_decreasing_2d,
    guillotine_cutting_2d,
    plot_placements_2d_matplotlib,
    check_all_orders_placed,
    match_labels_to_placements 
)

st.title("📦 Cutting Stock Problem Optimizer")

# Session state
if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "kpi_df" not in st.session_state:
    st.session_state.kpi_df = pd.DataFrame()

# Sidebar config
st.sidebar.header("⚙️ ตั้งค่าการตัด")
sheet_width = st.sidebar.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=10.0, value=91.4, step=0.1)
price_per_meter = st.sidebar.number_input("💰 ราคาต่อหน่วย (บาท/เมตร)", min_value=0.1, value=100.0, step=0.1)
price_per_m2 = price_per_meter / (sheet_width / 100)

# รับออเดอร์
st.header("📥 เพิ่มออเดอร์")
input_method = st.radio("เลือกวิธีกรอกข้อมูลออเดอร์", ["กรอกข้อมูลเอง", "อัปโหลดไฟล์ CSV"])
orders = []
labels = []
alert_flag = False

if input_method == "กรอกข้อมูลเอง":
    num_orders = st.number_input("จำนวนออเดอร์", min_value=1, step=1)
    for i in range(num_orders):
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            width = st.number_input(f"🔹 ความกว้าง (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'w{i}')
        with col2:
            length = st.number_input(f"🔹 ความยาว (cm) ที่ {i+1}", min_value=1.0, step=0.1, key=f'l{i}')
        with col3:
            label = st.text_input(f"🏷️ Label ที่ {i+1}", value="", key=f'label{i}')
        if width > sheet_width and length > sheet_width:
            alert_flag = True
        orders.append((width, length))
        labels.append(label.strip() if label.strip() else f"{int(width)}x{int(length)}")

elif input_method == "อัปโหลดไฟล์ CSV":
    uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ CSV (ต้องมีคอลัมน์ 'Width' และ 'Length')", type="csv")
    if uploaded_file:
        df_orders = pd.read_csv(uploaded_file)
        if "Width" in df_orders.columns and "Length" in df_orders.columns:
            orders = list(zip(df_orders["Width"], df_orders["Length"]))
            if any(w > sheet_width and l > sheet_width for w, l in orders):
                alert_flag = True
            if "Label" in df_orders.columns:
                labels = df_orders["Label"].fillna("").tolist()
                labels = [
                    label.strip() if label.strip() else f"{int(w)}x{int(l)}"
                    for label, (w, l) in zip(labels, orders)
                ]
            else:
                labels = [f"{int(w)}x{int(l)}" for w, l in orders]
            st.dataframe(df_orders)
        else:
            st.error("⚠️ ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

if alert_flag:
    st.error("🚨 ไม่สามารถคำนวณได้: มีออเดอร์ที่กว้างและยาวเกินความกว้างของแผ่นเมทัลชีท")

# คำนวณ
if orders and not alert_flag and st.button("🚀 คำนวณ"):
    algorithms = {
        "FFD 2D": first_fit_decreasing_2d,
        "BFD 2D": best_fit_decreasing_2d,
        "Guillotine 2D": guillotine_cutting_2d
    }

    results = {}
    kpi_rows = []
    total_order_area = sum(w * l for w, l in orders)

    for name, algo in algorithms.items():
        start_time = time.time()
        placements = algo(orders, sheet_width)
        proc_time = time.time() - start_time

        total_length_used = max(p["y"] + p["height"] for p in placements)
        total_used_area = sheet_width * total_length_used
        total_waste = max(0, total_used_area - total_order_area)

        material_cost = total_used_area * price_per_m2 / 10_000
        waste_cost = total_waste * price_per_m2 / 10_000

        all_placed = check_all_orders_placed(placements, orders)

        kpi_rows.append({
            "Algorithm": name,
            "Total Length Used (cm)": round(total_length_used, 2),
            "Total Used Area (cm²)": round(total_used_area, 2),
            "Total Waste (cm²)": round(total_waste, 2),
            "Processing Time (s)": round(proc_time, 6),
            "Material Cost (Baht)": f"{material_cost:,.2f}",
            "Waste Cost (Baht)": f"{waste_cost:,.2f}",
            "All Orders Placed": "✅" if all_placed else "❌"
        })

        results[name] = placements

    st.session_state.kpi_df = pd.DataFrame(kpi_rows)
    st.session_state.results = results
    st.session_state.labels = labels
    st.session_state.calculated = True

# แสดงผลลัพธ์
if st.session_state.calculated:
    st.subheader("📊 Summary (Algorithm & Area)")
    st.dataframe(
        st.session_state.kpi_df[[
            "Algorithm", "Total Length Used (cm)",
            "Total Used Area (cm²)", "Total Waste (cm²)",
            "Processing Time (s)", "All Orders Placed"
        ]],
        use_container_width=True, hide_index=True
    )
    
    st.subheader("💸 Cost Summary")
    st.dataframe(st.session_state.kpi_df[[
        "Algorithm", "Material Cost (Baht)", "Waste Cost (Baht)"
    ]], use_container_width=True, hide_index=True)

    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization", list(st.session_state.results.keys()))
    labels_matched = match_labels_to_placements(
    st.session_state.results[selected_algo],
    orders,
    st.session_state.labels
    )

    fig = plot_placements_2d_matplotlib(
        st.session_state.results[selected_algo],
        sheet_width,
        labels=labels_matched,
        title=selected_algo
    )
    st.pyplot(fig, use_container_width=False)
