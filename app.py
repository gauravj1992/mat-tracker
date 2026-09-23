import datetime
import os
import sqlite3
import time
import pandas as pd
import streamlit as st

# --- PAGE CONFIGURATION & WARM WHITE THEME ---
st.set_page_config(
    page_title="MAT Case Management Portal - PCIT Maharashtra",
    page_icon="⚖️",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Global Warm White Background & Professional Font */
    .stApp {
        background-color: #FDFBF7;
        color: #2C3E50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sidebar Styling for Warm Aesthetic */
    [data-testid="stSidebar"] {
        background-color: #F5EFEB;
    }

    /* Full-Width Layout Expansion */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 100%;
    }

    /* Professional Header Styles */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1A252C;
    }
    
    p, label, span {
        color: #2C3E50;
    }

    /* Professional Orange Banner for Login Header */
    .orange-banner {
        background-color: #E65100;
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .orange-banner h1 {
        color: white !important;
        font-size: 26px !important;
        margin-bottom: 5px !important;
    }
    .orange-banner p {
        color: #FFE0B2 !important;
        font-size: 15px !important;
        margin: 0 !important;
    }

    /* Attractive Modern Search Text Box Styling (Soft Sky Blue & Royal Blue) */
    input[aria-label="🔍 Search Cases"] {
        background-color: #EBF5FB !important;
        color: #2C3E50 !important;
        border: 2px solid #2980B9 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(41, 128, 185, 0.2) !important;
    }

    /* Completely Disable Image Zoom / Fullscreen Toolbar Overlay on st.image */
    [data-testid="stImage"] img {
        pointer-events: none !important;
    }
    [data-testid="stImageToolbar"], 
    button[title*="View fullscreen"], 
    button[title*="Fullscreen"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("mat_cases.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT NOT NULL,
            year_of_filing TEXT,
            bench TEXT NOT NULL,
            other_bench_details TEXT,
            applicant_name TEXT,
            subject_prayer TEXT,
            category_prayer TEXT,
            case_brief TEXT,
            affidavit_details TEXT,
            main_application_details TEXT,
            case_status_date TEXT,
            next_hearing_date TEXT,
            pdf_file_path TEXT
        )
    """)
    
    columns_to_check = [
        ("year_of_filing", "TEXT"),
        ("other_bench_details", "TEXT"),
        ("next_hearing_date", "TEXT"),
        ("pdf_file_path", "TEXT")
    ]
    for col_name, col_type in columns_to_check:
        try:
            cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("clerk1", "clerk123", "Clerk / Data Entry"),
            ("officer1", "officer123", "Officer")
        ]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", default_users)

    conn.commit()
    conn.close()

init_db()

# --- 2. AUTHENTICATION & SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if "show_login_popup" not in st.session_state:
    st.session_state.show_login_popup = False

if "form_reset_counter" not in st.session_state:
    st.session_state.form_reset_counter = 0

if "success_notification" not in st.session_state:
    st.session_state.success_notification = None

# --- 3. LOGIN PAGE UI ---
if not st.session_state.logged_in:
    banner_container = st.container()
    with banner_container:
        st.markdown('<div class="orange-banner">', unsafe_allow_html=True)
        col_logo, col_text = st.columns([1, 8])
        with col_logo:
            if os.path.exists("logo.jpg"):
                import base64
                with open("logo.jpg", "rb") as img_file:
                    encoded_logo = base64.b64encode(img_file.read()).decode()
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{encoded_logo}" width="180" style="border-radius: 6px; pointer-events: none;">',
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<h1>⚖️</h1>", unsafe_allow_html=True)
        with col_text:
            st.markdown(
                '<h1 style="border-bottom: 5px solid #2E7D32; padding-bottom: 8px; display: inline-block;">MAT Case Management Portal - PCIT Maharashtra</h1>', 
                unsafe_allow_html=True
            )
            st.markdown("<p>Please sign in with your assigned credentials.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- 30% CENTERED LOGIN FORM CONTAINER ---
    _, form_col, _ = st.columns([3.5, 3, 3.5])
    
    with form_col:
        with st.form("login_form"):
            st.markdown("### 🔐 Secure Sign In")
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Sign In", use_container_width=True)
            
        if login_btn:
            conn = sqlite3.connect("mat_cases.db")
            cursor = conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username = ?", (username_input,))
            user_record = cursor.fetchone()
            conn.close()
            
            if user_record and user_record[0] == password_input:
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.session_state.role = user_record[1]
                st.session_state.show_login_popup = True
                st.session_state.popup_start_time = time.time()  # Start 10s countdown timer
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

    # --- COPYRIGHT FOOTER FOR LOGIN PAGE ---
    st.markdown(
        """
        <div style="text-align: center; margin-top: 60px; color: #555; font-size: 13px;">
            <hr style="border: 0; border-top: 1px solid #D3C5B4; margin-bottom: 15px; width: 50%; margin-left: auto; margin-right: auto;">
            © 2026 PCIT Maharashtra Police. All rights reserved.<br>
            <b>Designed and Developed by PCIT Maha Police</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# --- 4. EXCLUSIVE CENTERED POPUP WITH 10-SECOND COUNTDOWN TIMER ---
if st.session_state.logged_in and st.session_state.show_login_popup:
    if "popup_start_time" not in st.session_state:
        st.session_state.popup_start_time = time.time()

    elapsed = int(time.time() - st.session_state.popup_start_time)
    remaining = max(0, 10 - elapsed)

    if remaining == 0:
        st.session_state.show_login_popup = False
        if "popup_start_time" in st.session_state:
            del st.session_state.popup_start_time
        st.rerun()

    conn_pop = sqlite3.connect("mat_cases.db")
    query_pop = """
        SELECT case_number, year_of_filing, 
               CASE WHEN bench = 'Others' THEN other_bench_details ELSE bench END as bench_name,
               applicant_name, next_hearing_date 
        FROM cases WHERE next_hearing_date IS NOT NULL
    """
    df_pop = pd.read_sql_query(query_pop, conn_pop)
    conn_pop.close()

    upcoming_cases = []
    if not df_pop.empty:
        today = datetime.date.today()
        target_date = today + datetime.timedelta(days=7)
        for _, row in df_pop.iterrows():
            try:
                h_date = pd.to_datetime(row["next_hearing_date"]).date()
                if today <= h_date <= target_date:
                    upcoming_cases.append({
                        "Case": f"{row['case_number']}/{row['year_of_filing']}",
                        "Bench": row["bench_name"],
                        "Applicant": row["applicant_name"],
                        "Hearing Date": str(h_date)
                    })
            except:
                pass

    # Vertical & Horizontal Centering Spacers
    st.write("")
    st.write("")
    st.write("")
    
    _, pop_col, _ = st.columns([2, 6, 2])
    with pop_col:
        with st.container(border=True):
            st.subheader("🔔 URGENT: Upcoming Hearings in the Next 7 Days")
            
            if upcoming_cases:
                st.warning(f"⚠️ You have **{len(upcoming_cases)} case(s)** scheduled for hearing within the next week!")
                pop_display_df = pd.DataFrame(upcoming_cases)
                st.dataframe(pop_display_df, use_container_width=True, hide_index=True)
            else:
                st.info("✅ Good news! There are no hearings scheduled within the next 7 days.")

            btn_label = f"✔ OK, Proceed to Portal ({remaining}s)"
            if st.button(btn_label, type="primary", key="close_popup_btn", use_container_width=True):
                st.session_state.show_login_popup = False
                if "popup_start_time" in st.session_state:
                    del st.session_state.popup_start_time
                st.rerun()

    time.sleep(1)
    st.rerun()
    st.stop()

# --- 5. MAIN PORTAL HEADER & SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚖️ MAT Portal Navigation")
    st.markdown(f"👤 **User:** {st.session_state.username}")
    st.markdown(f"🛡️ **Role:** {st.session_state.role}")
    if st.button("Log Out", key="sidebar_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.show_login_popup = False
        if "popup_start_time" in st.session_state:
            del st.session_state.popup_start_time
        st.rerun()
    st.markdown("---")

st.title("MAT Case Management Portal - Maharashtra")
st.markdown(f"Dashboard & Repository (Access Level: **{st.session_state.role}**)")

if st.session_state.success_notification:
    st.success(st.session_state.success_notification)
    st.session_state.success_notification = None

category_options = [
    "1. Recruitment and Selection process", "2. Recruitment Rules", "3. Timely Bound Promotions",
    "4. Assured progression scheme", "5. Promotion request", "6. HRA start request",
    "7. Issuence of Pension", "8. Increment stoppage", "9. Supernumerary post",
    "10. FAke Certificate", "11. Demand for Old Pension", "13. Advanced Increment",
    "14. Objection on Promotion Order", "15. Objection on Transfer order", "16. Other Objection",
    "17. Deemed date Promotion and related benifits", "18. Service Removal",
    "19. Prilimanary enquery, Departmental enquery and Suspension", "20. Hindi Language Concession",
    "21. Concession due completion of 45 years of Age", "22. Criminal case registered against employee",
    "23. Compassinate appointment", "25. Other issues"
]

standard_benches = ["MAT Mumbai", "MAT Nagpur", "MAT Chhatrapati Sambhajinagar"]
year_options = ["Please select year"] + [str(y) for y in range(2026, 1949, -1)]

# Sidebar Filters
conn_filter = sqlite3.connect("mat_cases.db")
cursor_filter = conn_filter.cursor()
cursor_filter.execute("SELECT DISTINCT bench, other_bench_details, year_of_filing FROM cases")
db_benches = []
db_years = []
for row in cursor_filter.fetchall():
    b, ob, yr = row[0], row[1], row[2]
    if b == "Others" and ob:
        db_benches.append(ob)
    elif b and b not in standard_benches:
        db_benches.append(b)
    if yr:
        db_years.append(yr)
conn_filter.close()

all_filter_benches = ["All Benches"] + list(set(standard_benches + db_benches))
all_filter_years = ["All Years"] + sorted(list(set(db_years)), reverse=True)
hearing_filter_options = ["All Time", "Within 1 week", "Within 2 weeks", "Within 3 weeks", "Within 4 weeks"]

st.sidebar.header("Supervisor Filters")
selected_bench = st.sidebar.selectbox("Filter by Bench", all_filter_benches, key="filter_bench")
selected_year = st.sidebar.selectbox("Filter by Year of Filing", all_filter_years, key="filter_year")
selected_category = st.sidebar.selectbox("Filter by Category of Prayer", ["All Categories"] + category_options, key="filter_cat")
selected_hearing_filter = st.sidebar.selectbox("Filter by Next Hearing Date", hearing_filter_options, key="filter_hearing")

# --- 6. DATA ENTRY FORM (Clerk Only) ---
if st.session_state.role == "Clerk / Data Entry":
    with st.expander("➕ Open Data Entry Form", expanded=False):
        with st.form(f"operator_entry_form_{st.session_state.form_reset_counter}"):
            case_number = st.text_input("Case Number (e.g., OA 123)")
            year_of_filing = st.selectbox("Year of Filing", year_options)
            
            bench_choices = ["Please Select Court"] + standard_benches + ["Others"]
            bench_selection = st.selectbox("Name of Bench / Bench", bench_choices)
            custom_bench = st.text_input("Please specify Court Name (if Others)")

            applicant_name = st.text_input("Applicant Name")
            subject_prayer = st.text_input("Subject/Prayer")
            
            cat_choices = ["Please select appropriate category"] + category_options
            category_prayer = st.selectbox("Category of Prayer/Subject", cat_choices)
            
            case_brief = st.text_area("Case in Brief (Max ~150 words)")
            affidavit_details = st.text_area("Affidavit Filing Details")
            main_application_details = st.text_area("Details of Main Application")
            case_status_date = st.text_input("Case Status Date (e.g., 2026-06-15 or 'Pending')")
            
            next_hearing_date_obj = st.date_input("Next Hearing Date", value=datetime.date.today())
            uploaded_pdf = st.file_uploader("Upload Case Document (PDF)", type=["pdf"])

            submitted = st.form_submit_button("Submit Case Record")

        if submitted:
            next_hearing_date_str = next_hearing_date_obj.strftime("%Y-%m-%d")
            final_bench_val = "Others" if bench_selection == "Others" else bench_selection
            final_other_details = custom_bench.strip() if bench_selection == "Others" else None

            pdf_path = None
            if uploaded_pdf is not None:
                safe_case_no = case_number.replace("/", "_").replace(" ", "_")
                pdf_filename = f"{safe_case_no}_{year_of_filing}_{uploaded_pdf.name}"
                pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

            if year_of_filing == "Please select year":
                st.error("Please select a valid Year of Filing.")
            elif bench_selection == "Please Select Court":
                st.error("Please select a valid Court or Bench.")
            elif bench_selection == "Others" and not custom_bench.strip():
                st.error("Please specify the Court Name.")
            elif category_prayer == "Please select appropriate category":
                st.error("Please select an appropriate category of prayer/subject.")
            elif case_number and applicant_name:
                conn = sqlite3.connect("mat_cases.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cases (case_number, year_of_filing, bench, other_bench_details, applicant_name, subject_prayer, category_prayer, case_brief, affidavit_details, main_application_details, case_status_date, next_hearing_date, pdf_file_path) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (case_number, year_of_filing, final_bench_val, final_other_details, applicant_name, subject_prayer, category_prayer, case_brief, affidavit_details, main_application_details, case_status_date, next_hearing_date_str, pdf_path))
                conn.commit()
                conn.close()
                
                st.session_state.success_notification = f"✅ Success! Case {case_number}/{year_of_filing} has been successfully entered and saved."
                st.session_state.form_reset_counter += 1
                st.rerun()
            else:
                st.error("Please fill in at least the Case Number and Applicant Name.")

# --- 7. SUPERVISOR REPOSITORY & SEARCH ---
st.subheader("Live Case Repository")
st.markdown("💡 *Tip: Cases with upcoming hearings **within 1 week** are highlighted in light green.*")

conn = sqlite3.connect("mat_cases.db")
query = """
    SELECT id as 'ID', case_number as 'Case Number', year_of_filing as 'Filing Year', 
           CASE WHEN bench = 'Others' THEN other_bench_details ELSE bench END as 'Bench', 
           other_bench_details as 'Other Court Details',
           applicant_name as 'Applicant', subject_prayer as 'Subject/Prayer', 
           category_prayer as 'Category', case_brief as 'Brief', 
           affidavit_details as 'Affidavit Details', main_application_details as 'Main App Details', 
           case_status_date as 'Status Date', next_hearing_date as 'Next Hearing Date', pdf_file_path as 'PDF Path'
    FROM cases WHERE 1=1
"""
params = []

if selected_bench != "All Benches":
    query += " AND (bench = ? OR other_bench_details = ?)"
    params.extend([selected_bench, selected_bench])
if selected_year != "All Years":
    query += " AND year_of_filing = ?"
    params.append(selected_year)
if selected_category != "All Categories":
    query += " AND category_prayer = ?"
    params.append(selected_category)

df = pd.read_sql_query(query, conn, params=params)
conn.close()

if not df.empty:
    if selected_hearing_filter != "All Time":
        today = datetime.date.today()
        days_map = {"Within 1 week": 7, "Within 2 weeks": 14, "Within 3 weeks": 21, "Within 4 weeks": 28}
        target_days = days_map.get(selected_hearing_filter, 7)
        target_date = today + datetime.timedelta(days=target_days)
            
        df["temp_date"] = pd.to_datetime(df["Next Hearing Date"], errors="coerce").dt.date
        df = df[(df["temp_date"] >= today) & (df["temp_date"] <= target_date)]
        df = df.drop(columns=["temp_date"])

    display_df = df.drop(columns=["Other Court Details", "PDF Path"], errors="ignore")
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        search_query = st.text_input("🔍 Search Cases", placeholder="Type to search cases, applicants, subjects...", key="search_box")
        
    if search_query:
        mask = display_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
        display_df = display_df[mask]
        
    with col_t2:
        st.write("")
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name="mat_cases_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    def highlight_upcoming_hearing(row):
        try:
            h_date = pd.to_datetime(row['Next Hearing Date']).date()
            today = datetime.date.today()
            if today <= h_date <= today + datetime.timedelta(days=7):
                return ['background-color: #D8F3DC'] * len(row)
        except:
            pass
        return [''] * len(row)

    styled_df = display_df.style.apply(highlight_upcoming_hearing, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("No cases found matching the selected filters.")
