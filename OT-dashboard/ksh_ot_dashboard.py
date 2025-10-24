import streamlit as st
import pandas as pd
import plotly.express as px
import io
from fpdf import FPDF
import os
from datetime import datetime
import requests

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="KSH OT Dashboard", page_icon="📊", layout="wide")

st.title("KSH Overtime (OT) Dashboard")
st.markdown("Built by **Jaykumar Kale** — Internship Dashboard Demo for KSH Logistics")

# -----------------------------------------------------------
# HELPER FUNCTION: Ensure DejaVuSans.ttf
# -----------------------------------------------------------
def ensure_font(font_path="DejaVuSans.ttf"):
    if not os.path.isfile(font_path):
        st.info(f"{font_path} not found. Downloading...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(r.content)
        st.success(f"{font_path} downloaded successfully.")
    return font_path

# -----------------------------------------------------------
# FILE UPLOAD
# -----------------------------------------------------------
uploaded_file = st.file_uploader("📂 Upload the Excel file", type=["xlsx"])

if uploaded_file:
    # --- Data Loading & Cleaning ---
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    expected_cols = ["Warehouse", "Customer", "Contractor Name", "Duration of work", "Total amt."]
    for col in expected_cols:
        if col not in df.columns:
            st.warning(f"⚠️ Column `{col}` not found in uploaded file.")
            df[col] = None

    df["Duration of work"] = pd.to_numeric(df["Duration of work"], errors="coerce")
    df["Total amt."] = pd.to_numeric(df["Total amt."], errors="coerce")
    df.dropna(subset=["Duration of work", "Total amt."], how="all", inplace=True)

    # -----------------------------------------------------------
    # DATA OVERVIEW
    # -----------------------------------------------------------
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    total_hours = df["Duration of work"].sum()
    total_amount = df["Total amt."].sum()
    total_records = len(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("⏱️ Total OT Hours", f"{total_hours:.1f} hrs")
    col2.metric("💰 Total OT Amount", f"₹{total_amount:,.0f}")
    col3.metric("📄 Records", f"{total_records}")

    # -----------------------------------------------------------
    # FILTERS
    # -----------------------------------------------------------
    st.sidebar.header("🎛️ Filters")
    warehouse_filter = st.sidebar.multiselect("Select Warehouse", df["Warehouse"].dropna().unique())
    customer_filter = st.sidebar.multiselect("Select Customer", df["Customer"].dropna().unique())
    contractor_filter = st.sidebar.multiselect("Select Contractor", df["Contractor Name"].dropna().unique())

    filtered_df = df.copy()
    if warehouse_filter:
        filtered_df = filtered_df[filtered_df["Warehouse"].isin(warehouse_filter)]
    if customer_filter:
        filtered_df = filtered_df[filtered_df["Customer"].isin(customer_filter)]
    if contractor_filter:
        filtered_df = filtered_df[filtered_df["Contractor Name"].isin(contractor_filter)]

    st.markdown("---")

    # -----------------------------------------------------------
    # WAREHOUSE SUMMARY
    # -----------------------------------------------------------
    st.subheader("🏭 Warehouse-wise Summary")
    warehouse_summary = (
        filtered_df.groupby("Warehouse")
        .agg({"Duration of work": "sum", "Total amt.": "sum"})
        .reset_index()
    )

    cols = st.columns(len(warehouse_summary) if len(warehouse_summary) > 0 else 1)
    for i, row in warehouse_summary.iterrows():
        with cols[i]:
            st.metric(
                f"{row['Warehouse']}",
                f"{row['Duration of work']:.1f} hrs",
                f"₹{row['Total amt.']:,.0f}"
            )

    st.markdown("---")

    # -----------------------------------------------------------
    # VISUAL INSIGHTS
    # -----------------------------------------------------------
    st.subheader("📈 Visual Insights")

    top_n = 3
    high_amount_threshold = 5000
    high_hours_threshold = 12

    # Top OT amounts for color mapping
    top_values = filtered_df["Total amt."].nlargest(top_n).values

    # Color assignment function
    def assign_color(amount):
        if amount in top_values:
            return "darkred"
        elif amount >= high_amount_threshold:
            return "red"
        else:
            return "lightblue"

    filtered_df["color_amount"] = filtered_df["Total amt."].apply(assign_color)

    # Chart: OT Amounts by Employee
    if "Name of the Employee" in filtered_df.columns:
        fig_amount = px.bar(
            filtered_df,
            x="Name of the Employee",
            y="Total amt.",
            color="color_amount",
            color_discrete_map={"darkred": "darkred", "red": "red", "lightblue": "lightblue"},
            text="Total amt.",
            title="OT Amount by Employee (Highlighted)",
        )
        fig_amount.update_layout(xaxis_title=None, yaxis_title="Amount (₹)", showlegend=False)
        st.plotly_chart(fig_amount, use_container_width=True)

    # Chart: OT Hours by Employee
    if "Name of the Employee" in filtered_df.columns:
        fig_hours = px.bar(
            filtered_df,
            x="Name of the Employee",
            y="Duration of work",
            color="Warehouse",
            text="Duration of work",
            title="OT Hours by Employee",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_hours.update_layout(xaxis_title=None, yaxis_title="Hours")
        st.plotly_chart(fig_hours, use_container_width=True)

    # Chart: Total Amount by Warehouse
    fig2 = px.bar(
        filtered_df,
        x="Warehouse",
        y="Total amt.",
        color="Customer",
        title="Total OT Amount by Warehouse",
        text_auto=True,
        color_discrete_sequence=px.colors.sequential.Greys
    )
    fig2.update_layout(xaxis_title=None, yaxis_title="Amount (₹)", showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

    # OT Reasons Pie Chart
    if "Remarks/Reasons" in filtered_df.columns:
        reason_count = filtered_df["Remarks/Reasons"].value_counts().reset_index()
        reason_count.columns = ["Reason", "Count"]
        fig3 = px.pie(
            reason_count,
            names="Reason",
            values="Count",
            title="OT Reasons Distribution",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # -----------------------------------------------------------
    # DOWNLOAD OPTIONS
    # -----------------------------------------------------------
    st.subheader("📤 Export Data")
    excel_buffer = io.BytesIO()
    filtered_df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        label="📥 Download Filtered Data (Excel)",
        data=excel_buffer,
        file_name="Filtered_OT_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF Export
    def create_pdf_report(filtered_df, report_period="October 2025"):
        pdf = FPDF()
        pdf.add_page()

        font_path = ensure_font()
        pdf.add_font("DejaVu", "", font_path, uni=True)

        def add_header():
            pdf.set_font("DejaVu", "B", 16)
            pdf.cell(0, 10, "KSH Logistics OT Report", ln=True, align="C")
            pdf.ln(2)
            pdf.set_font("DejaVu", "", 12)
            pdf.cell(0, 8, f"Report Period: {report_period}", ln=True, align="C")
            pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True, align="C")
            pdf.ln(6)

        def add_footer():
            pdf.set_y(-15)
            pdf.set_font("DejaVu", "I", 10)
            pdf.cell(0, 10, "Report generated automatically by KSH OT Dashboard", align="C")

        add_header()

        # Summary
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(0, 8, f"Total Records: {len(filtered_df)}", ln=True)
        pdf.cell(0, 8, f"Total OT Hours: {filtered_df['Duration of work'].sum():.1f} hrs", ln=True)
        pdf.cell(0, 8, f"Total OT Amount: ₹{filtered_df['Total amt.'].sum():,.2f}", ln=True)
        pdf.ln(4)

        col_width = pdf.w / (len(filtered_df.columns) + 1)
        line_height = 8

        def add_table_header():
            pdf.set_font("DejaVu", "B", 12)
            for col_name in filtered_df.columns:
                pdf.cell(col_width, line_height, str(col_name), border=1, align="C")
            pdf.ln(line_height)

        add_table_header()
        pdf.set_font("DejaVu", "", 11)

        top_n = 3
        top_values = filtered_df["Total amt."].nlargest(top_n).values

        for _, row in filtered_df.iterrows():
            if pdf.get_y() > pdf.h - 25:
                add_footer()
                pdf.add_page()
                add_header()
                add_table_header()
            for col_name in filtered_df.columns:
                value = str(row[col_name])
                if col_name == "Total amt.":
                    if row[col_name] in top_values:
                        pdf.set_text_color(139, 0, 0)  # Dark red
                    elif row[col_name] >= 5000:
                        pdf.set_text_color(255, 0, 0)  # Red
                    else:
                        pdf.set_text_color(0, 0, 0)
                    pdf.set_font("DejaVu", "B", 11)
                elif col_name == "Duration of work" and row[col_name] >= 12:
                    pdf.set_text_color(0, 0, 255)  # Blue
                    pdf.set_font("DejaVu", "B", 11)
                else:
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("DejaVu", "", 11)
                pdf.cell(col_width, line_height, value[:25], border=1, align="C")
            pdf.ln(line_height)

        pdf.set_text_color(0, 0, 0)
        add_footer()

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer

    pdf_buffer = create_pdf_report(filtered_df, report_period="01-10-2025 to 24-10-2025")

    st.download_button(
        label="🧾 Download Manager Report (PDF)",
        data=pdf_buffer,
        file_name="KSH_OT_Manager_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("👆 Upload the extracted Excel file (`OT_Data_Extracted.xlsx`) to view the dashboard.")
