# KSH Interactive Dashboard  

**Internship / Real-World Warehouse Solution**  
*Developed by **Jaykumar Kale**  

---

## **Overview**

During my internship at **KSH Logistics, Chakan, Pune**, I visited the warehouse and discussed operations with the warehouse manager. The warehouse uses Excel dashboards for tracking operations and overtime (OT), but they are **manual, non-scalable, and lack interactivity**.  

This project focuses on developing an **interactive, web-based dashboard** that enables secure, warehouse-specific data entry and visualization, with automated reporting.

---

## **Problem Statement**

- **Current Excel dashboards are not scalable.**  
- Each warehouse requires **independent access**, ensuring one warehouse’s data does not interfere with another.  
- Managers need **interactive insights**, complaint tracking, and automated report generation.  

---

## **Solution**

- **Web-Based Interactive Dashboard** built using:
  - **Streamlit** for the web interface.
  - **Pandas** for data cleaning and manipulation.
  - **Plotly** for interactive visualizations.
  - **FPDF** for auto-generated PDF reports.
- Future scalability options: React + Node + PostgreSQL or Power BI integration for enterprise deployment.
- **Login-based access per warehouse** can be implemented to ensure data security.

---

## **Features**

- **Complaint Tracking:** Manage and view warehouse complaints and resolutions.  
- **OT Cost Analysis:** Calculate overtime per employee or warehouse and track costs.  
- **Approval Workflows:** Track approval status of operations and OT entries.  
- **Customer-Wise Trends:** Visualize trends by customer, employee, or warehouse.  
- **Auto-Generated Reports:** Export PDF reports for managerial review.  
- **Interactive Charts & Filters:** Drill-down into data for deeper insights.  

---

## **Data Requirements**

The dashboard works with Excel files containing the following columns:

- `Operation Date`  
- `Warehouse`  
- `Customer`  
- `Employee Name`  
- `Designation`  
- `Contractor Name`  
- `Start Time`  
- `End Time`  
- `Duration` (calculated automatically)  
- `Remarks / Reasons`  
- `Rate` (optional)  
- `Total Amount`  
- `Approved By`  
- `Approval Date`  

> Duration is calculated automatically from `Start Time` and `End Time`.

---

## **Installation and Usage**

1. Clone this repository:
```bash
git clone https://github.com/Jaykumar-Kale/KSH-projects.git
cd Dashboard

2. Install dependencies:
pip install -r requirements.txt

3. Run the dashboard locally:
streamlit run ksh_ot_dashboard.py

