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
    div.stButton > button[kind="primary"], div.stButton > button {
        font-weight: 800 !important;
        font-size: 15px !important;
    }
    div.stButton > button[kind="primary"] p, div.stButton > button p,
    div.stButton > button[kind="primary"] span, div.stButton > button span {
        font-weight: 800 !important;
        font-size: 15px !important;
        color: #1A252C !important;
    }

    div.stFormSubmitButton > button {
        background-color: #9bff94 !important;
        border-color: #72e06b !important;
    }
    div.stFormSubmitButton > button p, div.stFormSubmitButton > button span {
        color: #1A252C !important;
    }

    [data-testid="stSidebar"] div.stButton > button {
        background-color: #73ceff !important;
        border-color: #4ab3e8 !important;
    }
    [data-testid="stSidebar"] div.stButton > button p, [data-testid="stSidebar"] div.stButton > button span {
        color: #1A252C !important;
    }

    div.stExpander div.stButton > button[kind="primary"] {
        background-color: #ff5b03 !important;
        border-color: #e04f02 !important;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #6b83fa !important;
        border-color: #4a66f8 !important;
    }
    div[data-testid="stButton"] button[kind="primary"] p, 
    div[data-testid="stButton"] button[kind="primary"] span {
        color: #1A252C !important;
    }

    .stApp {
        background-color: #FDFBF7;
        color: #2C3E50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #F5EFEB;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 100%;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1A252C;
    }
    
    p, label, span {
        color: #2C3E50;
    }

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

    input[aria-label="🔍 Search Cases"], input[aria-label="🔍 केस शोधा"] {
        background-color: #EBF5FB !important;
        color: #2C3E50 !important;
        border: 2px solid #2980B9 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(41, 128, 185, 0.2) !important;
    }

    [data-testid="stExpander"] {
        border-radius: 10px !important;
        background-color: #c7d0ff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    [data-testid="stExpander"] summary, 
    [data-testid="stExpander"] summary span, 
    [data-testid="stExpander"] summary p {
        font-weight: 900 !important;
        color: #1B2631 !important;
        font-size: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- BILINGUAL TRANSLATION DICTIONARY ---
TRANSLATIONS = {
    "English": {
        "portal_title": "MAT Case Management Portal - PCIT Maharashtra",
        "login_prompt": "Please sign in with your assigned credentials.",
        "secure_signin": "🔐 Secure Sign In",
        "username": "Username",
        "password": "Password",
        "signin_btn": "Sign In",
        "invalid_login": "Invalid username or password. Please try again.",
        "nav_header": "⚖️ MAT Portal Navigation",
        "user_label": "User",
        "role_label": "Role",
        "logout_btn": "Log Out",
        "dashboard_title": "Dashboard & Repository",
        "access_level": "Access Level",
        "supervisor_filters": "Supervisor Filters",
        "filter_bench": "Filter by Bench",
        "filter_year": "Filter by Year of Filing",
        "filter_cat": "Filter by Category of Prayer",
        "filter_hearing": "Filter by Next Hearing Date",
        "all_benches": "All Benches",
        "all_years": "All Years",
        "all_categories": "All Categories",
        "all_time": "All Time",
        "open_entry": "➕ Open Data Entry Form",
        "edit_record": "✏️ Edit Existing Case Record",
        "case_no": "Case Number (e.g., OA 123)",
        "year_filing": "Year of Filing",
        "select_year": "Please select year",
        "bench_name": "Name of Bench / Bench",
        "select_court": "Please Select Court",
        "others": "Others",
        "custom_bench": "Please specify Court Name (if Others)",
        "applicant": "Applicant Name",
        "subject": "Subject/Prayer",
        "category": "Category of Prayer/Subject",
        "select_cat": "Please select appropriate category",
        "brief": "Case in Brief (Max ~150 words)",
        "affidavit": "Affidavit Filing Details",
        "main_app": "Details of Main Application",
        "status_date": "Case Status Date (e.g., 2026-06-15 or 'Pending')",
        "has_hearing_chk": "Is next hearing date given?",
        "hearing_date": "Next Hearing Date",
        "upload_pdf": "Upload Case Document (PDF)",
        "submit_btn": "Submit Case Record",
        "update_btn": "Update Case Record",
        "select_edit_case": "Select Case to Edit",
        "live_repo": "Live Case Repository",
        "repo_tip": "💡 *Tip: Click the **View Details** button on any row to open full case records in a modal window. Cases with upcoming hearings **within 1 week** are highlighted in light green.*",
        "search_box": "🔍 Search Cases",
        "search_placeholder": "Type to search cases, applicants, subjects...",
        "export_csv": "📥 Export to CSV",
        "view_details": "View Details",
        "no_cases": "No cases found matching the selected filters.",
        "no_edit_cases": "No cases available in the database to edit.",
        "popup_title": "🔔 URGENT: Upcoming Hearings in the Next 7 Days",
        "popup_warning": "⚠️ You have **{count} case(s)** scheduled for hearing within the next week!",
        "popup_success": "✅ Good news! There are no hearings scheduled within the next 7 days.",
        "popup_btn": "✔ OK, Proceed to Portal ({remaining}s)",
        "footer": "© 2026 PCIT Maharashtra, All rights reserved.<br><b>Designed and Developed by PCIT Maha Police</b>"
    },
    "मराठी": {
        "portal_title": "एमएटी केस मॅनेजमेंट पोर्टल - पीसीआयटी महाराष्ट्र",
        "login_prompt": "कृपया आपल्या नियुक्त क्रेडेन्शियल्ससह साइन इन करा.",
        "secure_signin": "🔐 सुरक्षित साइन इन",
        "username": "वापरकर्ता नाव (Username)",
        "password": "पासवर्ड (Password)",
        "signin_btn": "साइन इन करा",
        "invalid_login": "अवैध वापरकर्ता नाव किंवा पासवर्ड. कृपया पुन्हा प्रयत्न करा.",
        "nav_header": "⚖️ एमएटी पोर्टल नेव्हिगेशन",
        "user_label": "वापरकर्ता",
        "role_label": "भूमिका",
        "logout_btn": "बाहेर पडा (Log Out)",
        "dashboard_title": "डॅशबोर्ड आणि रिपॉजिटरी",
        "access_level": "प्रवेश स्तर",
        "supervisor_filters": "सुपरवायझर फिल्टर",
        "filter_bench": "पीठाद्वारे फिल्टर करा",
        "filter_year": "दाखल वर्षानुसार फिल्टर करा",
        "filter_cat": "प्रार्थना श्रेणीनुसार फिल्टर करा",
        "filter_hearing": "पुढील सुनावणी तारखेनुसार फिल्टर करा",
        "all_benches": "सर्व पीठे",
        "all_years": "सर्व वर्षे",
        "all_categories": "सर्व श्रेणी",
        "all_time": "सर्व वेळ",
        "open_entry": "➕ डेटा एंट्री फॉर्म उघडा",
        "edit_record": "✏️ विद्यमान केस रेकॉर्ड संपादित करा",
        "case_no": "केस क्रमांक (उदा. OA 123)",
        "year_filing": "दाखल करण्याचे वर्ष",
        "select_year": "कृपया वर्ष निवडा",
        "bench_name": "न्यायालयाचे पीठ (Bench)",
        "select_court": "कृपया न्यायालय निवडा",
        "others": "इतर",
        "custom_bench": "कृपया न्यायालयाचे नाव निर्दिष्ट करा (इतर असल्यास)",
        "applicant": "अर्जदाराचे नाव",
        "subject": "विषय / प्रार्थना",
        "category": "प्रार्थना/विषयाचा वर्ग",
        "select_cat": "कृपया योग्य श्रेणी निवडा",
        "brief": "थोडक्यात केसची माहिती (कमाल ~१५० शब्द)",
        "affidavit": "प्रतिज्ञापत्र (Affidavit) तपशील",
        "main_app": "मुख्य अर्जाचा तपशील",
        "status_date": "केस स्थिती दिनांक (उदा. २०२६-०६-१५ किंवा 'Pending')",
        "has_hearing_chk": "पुढील सुनावणीची तारीख दिली आहे का?",
        "hearing_date": "पुढील सुनावणीची तारीख",
        "upload_pdf": "केस दस्तऐवज अपलोड करा (PDF)",
        "submit_btn": "केस रेकॉर्ड सबमिट करा",
        "update_btn": "केस रेकॉर्ड अपडेट करा",
        "select_edit_case": "संपादित करण्यासाठी केस निवडा",
        "live_repo": "लाइव्ह केस रिपॉजिटरी",
        "repo_tip": "💡 *टीप: संपूर्ण तपशील पॉपअप विंडोमध्ये पाहण्यासाठी प्रत्येक ओळीवरील **तपशील पहा** बटणावर क्लिक करा.*",
        "search_box": "🔍 केस शोधा",
        "search_placeholder": "केस, अर्जदार, विषय शोधण्यासाठी टाइप करा...",
        "export_csv": "📥 CSV मध्ये निर्यात करा",
        "view_details": "तपशील पहा",
        "no_cases": "निवडलेल्या फिल्टरशी जुळणाऱ्या कोणत्याही केसेस सापडल्या नाहीत.",
        "no_edit_cases": "संपादित करण्यासाठी डेटाबेसमध्ये कोणतीही केस उपलब्ध नाही.",
        "popup_title": "🔔 अत्यंत महत्त्वाचे: पुढील ७ दिवसांत सुनावणी असलेल्या केसेस",
        "popup_warning": "⚠️ पुढील आठवड्यात तुमच्या **{count} केसेस** सुनावणीसाठी शेड्यूल केल्या आहेत!",
        "popup_success": "✅ आनंदाची बातमी! पुढील ७ दिवसांत कोणतीही सुनावणी शेड्यूल केलेली नाही.",
        "popup_btn": "✔ ठीक आहे, पोर्टलवर पुढे जा ({remaining}s)",
        "footer": "© २०२६ पीसीआयटी महाराष्ट्र, सर्व हक्क सुरक्षित.<br><b>पीसीआयटी महा पोलीस द्वारे डिझाइन आणि विकसित</b>"
    }
}

def t(key):
    lang = st.session_state.get("lang", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)

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
            ("officer1", "officer123", "Officer"),
            ("admin1", "admin123", "Admin")
        ]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", default_users)
    else:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin1'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin1', 'admin123', 'Admin')")

    conn.commit()
    conn.close()

init_db()

# --- 2. AUTHENTICATION & SESSION STATE ---
if "lang" not in st.session_state:
    st.session_state.lang = "English"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    if "user" in st.query_params and "role" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.username = st.query_params["user"]
        st.session_state.role = st.query_params["role"]

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
        col_logo, col_text, col_lang = st.columns([1, 6, 2])
        with col_logo:
            if os.path.exists("logo.jpg"):
                import base64
                with open("logo.jpg", "rb") as img_file:
                    encoded_logo = base64.b64encode(img_file.read()).decode()
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{encoded_logo}" width="160" style="border-radius: 6px; pointer-events: none;">',
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<h1>⚖️</h1>", unsafe_allow_html=True)
        with col_text:
            st.markdown(
                f'<h1 style="border-bottom: 5px solid #2E7D32; padding-bottom: 8px; display: inline-block;">{t("portal_title")}</h1>', 
                unsafe_allow_html=True
            )
            st.markdown(f"<p>{t('login_prompt')}</p>", unsafe_allow_html=True)
        with col_lang:
            st.markdown("<p style='color: white !important; font-weight: bold; margin-bottom: 0;'>🌐 Language / भाषा</p>", unsafe_allow_html=True)
            st.session_state.lang = st.selectbox("Language", ["English", "मराठी"], index=0 if st.session_state.lang == "English" else 1, label_visibility="collapsed", key="login_lang_sel")
        st.markdown('</div>', unsafe_allow_html=True)
    
    _, form_col, _ = st.columns([3.5, 3, 3.5])
    
    with form_col:
        with st.form("login_form"):
            st.markdown(f"### {t('secure_signin')}")
            username_input = st.text_input(t("username"))
            password_input = st.text_input(t("password"), type="password")
            login_btn = st.form_submit_button(t("signin_btn"), use_container_width=True)
            
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
                st.session_state.popup_start_time = time.time()
                st.query_params["user"] = username_input
                st.query_params["role"] = user_record[1]
                st.rerun()
            else:
                st.error(t("invalid_login"))

    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 60px; color: #555; font-size: 13px;">
            <hr style="border: 0; border-top: 1px solid #D3C5B4; margin-bottom: 15px; width: 50%; margin-left: auto; margin-right: auto;">
            {t('footer')}
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
        FROM cases WHERE next_hearing_date IS NOT NULL AND next_hearing_date NOT LIKE '%Not available%' AND next_hearing_date != ''
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
                        "Hearing Date": h_date.strftime("%d-%m-%Y")
                    })
            except:
                pass

    st.write("")
    st.write("")
    st.write("")
    
    _, pop_col, _ = st.columns([2, 6, 2])
    with pop_col:
        with st.container(border=True):
            st.subheader(t("popup_title"))
            
            if upcoming_cases:
                warning_msg = t("popup_warning").format(count=len(upcoming_cases))
                st.warning(warning_msg)
                pop_display_df = pd.DataFrame(upcoming_cases)
                st.dataframe(pop_display_df, use_container_width=True, hide_index=True)
            else:
                st.info(t("popup_success"))

            btn_label = t("popup_btn").format(remaining=remaining)
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
    st.session_state.lang = st.selectbox("🌐 Language / भाषा", ["English", "मराठी"], index=0 if st.session_state.lang == "English" else 1, key="sidebar_lang_sel")
    st.markdown("---")
    
    st.markdown(f"### {t('nav_header')}")
    st.markdown(f"👤 **{t('user_label')}:** {st.session_state.username}")
    st.markdown(f"🛡️ **{t('role_label')}:** {st.session_state.role}")
    
    if st.button(t("logout_btn"), key="sidebar_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.show_login_popup = False
        if "popup_start_time" in st.session_state:
            del st.session_state.popup_start_time
        st.query_params.clear()
        
        st.markdown(
            """
            <script>
                setTimeout(function() {
                    window.location.reload(true);
                }, 100);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.rerun()
        
    st.markdown("---")

st.title(t("portal_title"))
st.markdown(f"**{t('dashboard_title')} ({t('access_level')}: {st.session_state.role})**")

if st.session_state.success_notification:
    st.success(st.session_state.success_notification)
    st.session_state.success_notification = None

category_options = [
    "1. Recruitment and Selection process", "2. Recruitment Rules", "3. Timely Bound Promotions",
    "4. Assured progression scheme", "5. Promotion request", "6. HRA start request",
    "7. Issuence of Pension", "8. Increment stoppage", "9. Supernumerary post",
    "10. Fake Certificate or Document", "11. Demand for Old Pension", "13. Advanced Increment",
    "14. Objection on Promotion Order", "15. Objection on Transfer order", "16. Other Objection",
    "17. Deemed date Promotion and related benifits", "18. Service Removal",
    "19. Prilimanary enquery, Departmental enquery and Suspension", "20. Hindi Language Concession",
    "21. Concession due completion of 45 years of Age", "22. Criminal case registered against employee",
    "23. Compassinate appointment", "25. Other issues"
]

standard_benches = ["MAT Mumbai", "MAT Nagpur", "MAT Chhatrapati Sambhajinagar"]
year_options = [t("select_year")] + [str(y) for y in range(2026, 1949, -1)]

# Sidebar Filters
conn_filter = sqlite3.connect("mat_cases.db")
cursor_filter = conn_filter.cursor()
cursor_filter.execute("SELECT DISTINCT bench, other_bench_details, year_of_filing FROM cases")
db_benches = []
db_years = []
for row in cursor_filter.fetchall():
    b, ob, yr = row[0], row[1], row[2]
    if b == t("others") and ob:
        db_benches.append(ob)
    elif b and b not in standard_benches:
        db_benches.append(b)
    if yr:
        db_years.append(yr)
conn_filter.close()

all_filter_benches = [t("all_benches")] + list(set(standard_benches + db_benches))
all_filter_years = [t("all_years")] + sorted(list(set(db_years)), reverse=True)
hearing_filter_options = [t("all_time"), "Within 1 week", "Within 2 weeks", "Within 3 weeks", "Within 4 weeks"]

# New Status filter options (Bilingual support added)
status_filter_options = {
    "English": ["All Cases", "Pending", "Disposed"],
    "मराठी": ["सर्व केसेस", "प्रलंबित (Pending)", "निकाल लागलेल्या (Disposed)"]
}
current_lang_status_opts = status_filter_options.get(st.session_state.get("lang", "English"), status_filter_options["English"])

st.sidebar.header(t("supervisor_filters"))
selected_bench = st.sidebar.selectbox(t("filter_bench"), all_filter_benches, key="filter_bench")
selected_year = st.sidebar.selectbox(t("filter_year"), all_filter_years, key="filter_year")
selected_category = st.sidebar.selectbox(t("filter_cat"), [t("all_categories")] + category_options, key="filter_cat")
selected_hearing_filter = st.sidebar.selectbox(t("filter_hearing"), hearing_filter_options, key="filter_hearing")

# New Status Filter Dropdown
status_label = "Filter by Status" if st.session_state.get("lang", "English") == "English" else "स्थितीनुसार फिल्टर करा"
selected_status_filter = st.sidebar.selectbox(status_label, current_lang_status_opts, key="filter_status")

# --- 6. DATA ENTRY FORM & EDIT RECORD FORM (Clerk & Admin) ---
if st.session_state.role in ["Clerk / Data Entry", "Admin"]:
    with st.expander(t("open_entry"), expanded=False):
        rc = st.session_state.form_reset_counter
        
        case_number = st.text_input(t("case_no"), key=f"de_case_no_{rc}")
        year_of_filing = st.selectbox(t("year_filing"), year_options, key=f"de_year_{rc}")
        
        bench_choices = [t("select_court")] + standard_benches + [t("others")]
        bench_selection = st.selectbox(t("bench_name"), bench_choices, key=f"de_bench_{rc}")
        custom_bench = st.text_input(t("custom_bench"), key=f"de_custom_bench_{rc}")

        applicant_name = st.text_input(t("applicant"), key=f"de_applicant_{rc}")
        subject_prayer = st.text_input(t("subject"), key=f"de_subject_{rc}")
        
        cat_choices = [t("select_cat")] + category_options
        category_prayer = st.selectbox(t("category"), cat_choices, key=f"de_cat_{rc}")
        
        case_brief = st.text_area(t("brief"), key=f"de_brief_{rc}")
        affidavit_details = st.text_area(t("affidavit"), key=f"de_affidavit_{rc}")
        main_application_details = st.text_area(t("main_app"), key=f"de_main_app_{rc}")
        case_status_date = st.text_input(t("status_date"), key=f"de_status_{rc}")
        
        has_hearing = st.checkbox(t("has_hearing_chk"), value=True, key=f"de_has_hearing_{rc}")
        next_hearing_date_obj = st.date_input(t("hearing_date"), value=datetime.date.today(), disabled=not has_hearing, key=f"de_hearing_date_{rc}")
        
        uploaded_pdf = st.file_uploader(t("upload_pdf"), type=["pdf"], key=f"de_pdf_{rc}")

        submitted = st.button(t("submit_btn"), key=f"de_submit_btn_{rc}", type="primary")

        if submitted:
            if has_hearing:
                next_hearing_date_str = next_hearing_date_obj.strftime("%Y-%m-%d")
            else:
                next_hearing_date_str = "Date Not available"

            final_bench_val = t("others") if bench_selection == t("others") else bench_selection
            final_other_details = custom_bench.strip() if bench_selection == t("others") else None

            pdf_path = None
            if uploaded_pdf is not None:
                safe_case_no = case_number.replace("/", "_").replace(" ", "_")
                pdf_filename = f"{safe_case_no}_{year_of_filing}_{uploaded_pdf.name}"
                pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

            if year_of_filing == t("select_year"):
                st.error("Please select a valid Year of Filing.")
            elif bench_selection == t("select_court"):
                st.error("Please select a valid Court or Bench.")
            elif bench_selection == t("others") and not custom_bench.strip():
                st.error("Please specify the Court Name.")
            elif category_prayer == t("select_cat"):
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

    # --- B. EDIT EXISTING CASE RECORD FORM ---
    with st.expander(t("edit_record"), expanded=False):
        conn_edit = sqlite3.connect("mat_cases.db")
        cursor_edit = conn_edit.cursor()
        cursor_edit.execute("SELECT id, case_number, year_of_filing, applicant_name FROM cases")
        cases_list = cursor_edit.fetchall()
        conn_edit.close()
        
        if cases_list:
            case_options_map = {f"ID: {row[0]} | {row[1]}/{row[2]} - {row[3]}": row[0] for row in cases_list}
            selected_case_label = st.selectbox(t("select_edit_case"), list(case_options_map.keys()), key="edit_case_select")
            selected_case_id = case_options_map[selected_case_label]
            
            conn_full = sqlite3.connect("mat_cases.db")
            cursor_full = conn_full.cursor()
            cursor_full.execute("SELECT case_number, year_of_filing, bench, other_bench_details, applicant_name, subject_prayer, category_prayer, case_brief, affidavit_details, main_application_details, case_status_date, next_hearing_date FROM cases WHERE id = ?", (selected_case_id,))
            c_data = cursor_full.fetchone()
            conn_full.close()
            
            if c_data:
                e_case_no = st.text_input(t("case_no"), value=c_data[0], key=f"edit_case_no_{selected_case_id}")
                e_year = st.selectbox(t("year_filing"), year_options, index=year_options.index(c_data[1]) if c_data[1] in year_options else 0, key=f"edit_year_{selected_case_id}")
                
                bench_choices = [t("select_court")] + standard_benches + [t("others")]
                b_idx = bench_choices.index(c_data[2]) if c_data[2] in bench_choices else (bench_choices.index(t("others")) if c_data[2] else 0)
                e_bench = st.selectbox(t("bench_name"), bench_choices, index=b_idx, key=f"edit_bench_{selected_case_id}")
                e_custom_bench = st.text_input(t("custom_bench"), value=c_data[3] if c_data[3] else "", key=f"edit_custom_bench_{selected_case_id}")
                
                e_applicant = st.text_input(t("applicant"), value=c_data[4] if c_data[4] else "", key=f"edit_applicant_{selected_case_id}")
                e_subject = st.text_input(t("subject"), value=c_data[5] if c_data[5] else "", key=f"edit_subject_{selected_case_id}")
                
                cat_choices = [t("select_cat")] + category_options
                c_idx = cat_choices.index(c_data[6]) if c_data[6] in cat_choices else 0
                e_cat = st.selectbox(t("category"), cat_choices, index=c_idx, key=f"edit_cat_{selected_case_id}")
                
                e_brief = st.text_area(t("brief"), value=c_data[7] if c_data[7] else "", key=f"edit_brief_{selected_case_id}")
                e_affidavit = st.text_area(t("affidavit"), value=c_data[8] if c_data[8] else "", key=f"edit_affidavit_{selected_case_id}")
                e_main_app = st.text_area(t("main_app"), value=c_data[9] if c_data[9] else "", key=f"edit_main_app_{selected_case_id}")
                e_status = st.text_input(t("status_date"), value=c_data[10] if c_data[10] else "", key=f"edit_status_{selected_case_id}")
                
                curr_hearing = c_data[11]
                has_h_val = True
                h_date_val = datetime.date.today()
                if not curr_hearing or str(curr_hearing).strip() in ["Date Not available", "None", ""]:
                    has_h_val = False
                else:
                    try:
                        h_date_val = datetime.datetime.strptime(curr_hearing, "%Y-%m-%d").date()
                    except:
                        try:
                            h_date_val = datetime.datetime.strptime(curr_hearing, "%d-%m-%Y").date()
                        except:
                            pass
                            
                e_has_hearing = st.checkbox(t("has_hearing_chk"), value=has_h_val, key=f"edit_has_hearing_{selected_case_id}")
                e_hearing_date = st.date_input(t("hearing_date"), value=h_date_val, disabled=not e_has_hearing, key=f"edit_hearing_date_{selected_case_id}")
                
                update_submitted = st.button(t("update_btn"), key=f"edit_submit_{selected_case_id}", type="primary")
                
                if update_submitted:
                    final_h_str = e_hearing_date.strftime("%Y-%m-%d") if e_has_hearing else "Date Not available"
                    final_b_val = t("others") if e_bench == t("others") else e_bench
                    final_ob_details = e_custom_bench.strip() if e_bench == t("others") else None
                    
                    conn_up = sqlite3.connect("mat_cases.db")
                    cur_up = conn_up.cursor()
                    cur_up.execute("""
                        UPDATE cases 
                        SET case_number = ?, year_of_filing = ?, bench = ?, other_bench_details = ?, 
                            applicant_name = ?, subject_prayer = ?, category_prayer = ?, 
                            case_brief = ?, affidavit_details = ?, main_application_details = ?, 
                            case_status_date = ?, next_hearing_date = ?
                        WHERE id = ?
                    """, (e_case_no, e_year, final_b_val, final_ob_details, e_applicant, e_subject, e_cat, e_brief, e_affidavit, e_main_app, e_status, final_h_str, selected_case_id))
                    conn_up.commit()
                    conn_up.close()
                    
                    st.session_state.success_notification = f"✅ Success! Case {e_case_no}/{e_year} has been successfully updated."
                    st.rerun()
        else:
            st.info(t("no_edit_cases"))

# --- 7. SUPERVISOR REPOSITORY, FILTERS & CUSTOM ROW GRID ---
st.subheader(t("live_repo"))
st.markdown(t("repo_tip"))

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

if selected_bench != t("all_benches"):
    query += " AND (bench = ? OR other_bench_details = ?)"
    params.extend([selected_bench, selected_bench])
if selected_year != t("all_years"):
    query += " AND year_of_filing = ?"
    params.append(selected_year)
if selected_category != t("all_categories"):
    query += " AND category_prayer = ?"
    params.append(selected_category)

# Apply Status Filter logic (Pending, Disposed, All Cases)
lang_key = st.session_state.get("lang", "English")
if lang_key == "English":
    if selected_status_filter == "Pending":
        query += " AND (LOWER(case_status_date) LIKE '%pending%' OR case_status_date IS NULL OR case_status_date = '')"
    elif selected_status_filter == "Disposed":
        query += " AND LOWER(case_status_date) LIKE '%disposed%'"
else: # Marathi
    if "प्रलंबित" in selected_status_filter:
        query += " AND (LOWER(case_status_date) LIKE '%pending%' OR case_status_date IS NULL OR case_status_date = '')"
    elif "निकाल" in selected_status_filter:
        query += " AND LOWER(case_status_date) LIKE '%disposed%'"

df = pd.read_sql_query(query, conn, params=params)
conn.close()

if not df.empty:
    def format_date_display(val):
        if not val or str(val).strip() in ["None", "nan", "", "NaT", "Date Not available", "Not Available"]:
            return "Date Not available"
        try:
            parsed_date = pd.to_datetime(val)
            if pd.isna(parsed_date):
                return "Date Not available"
            return parsed_date.strftime("%d-%m-%Y")
        except:
            return "Date Not available"

    df["Next Hearing Date"] = df["Next Hearing Date"].apply(format_date_display)

    if selected_hearing_filter != t("all_time"):
        today = datetime.date.today()
        days_map = {"Within 1 week": 7, "Within 2 weeks": 14, "Within 3 weeks": 21, "Within 4 weeks": 28}
        target_days = days_map.get(selected_hearing_filter, 7)
        target_date = today + datetime.timedelta(days=target_days)
            
        def is_within_range(val_str):
            if val_str == "Date Not available":
                return False
            try:
                dt = datetime.datetime.strptime(val_str, "%d-%m-%Y").date()
                return today <= dt <= target_date
            except:
                return False

        df = df[df["Next Hearing Date"].apply(is_within_range)]

    # Search bar & Export
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        search_query = st.text_input(t("search_box"), placeholder=t("search_placeholder"), key="search_box")
        
    if search_query:
        mask = df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
        df = df[mask]
        
    with col_t2:
        st.write("")
        export_df = df.drop(columns=["Other Court Details", "PDF Path"], errors="ignore")
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=t("export_csv"),
            data=csv_data,
            file_name="mat_cases_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --- NATIVE DIALOG MODAL POPUP WINDOW ---
    @st.dialog("📄 Case Full Details View", width="large")
    def show_case_modal(case_id):
        conn_pop = sqlite3.connect("mat_cases.db")
        cur_pop = conn_pop.cursor()
        cur_pop.execute("""
            SELECT case_number, year_of_filing, bench, other_bench_details, applicant_name, 
                   subject_prayer, category_prayer, case_brief, affidavit_details, 
                   main_application_details, case_status_date, next_hearing_date, pdf_file_path 
            FROM cases WHERE id = ?
        """, (case_id,))
        case_row = cur_pop.fetchone()
        conn_pop.close()

        if case_row:
            st.markdown(f"### Case Number: **{case_row[0]} / {case_row[1]}**")
            st.markdown("---")
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                bench_display = case_row[3] if case_row[2] == "Others" and case_row[3] else case_row[2]
                st.markdown(f"**🏛️ Bench / Court:** {bench_display}")
                st.markdown(f"**👤 Applicant Name:** {case_row[4]}")
                st.markdown(f"**📌 Subject / Prayer:** {case_row[5] if case_row[5] else 'N/A'}")
                st.markdown(f"**🏷️ Category:** {case_row[6] if case_row[6] else 'N/A'}")
                st.markdown(f"**📅 Status Date:** {case_row[10] if case_row[10] else 'N/A'}")

            with p_col2:
                st.markdown(f"**⏰ Next Hearing Date:** {case_row[11] if case_row[11] else 'Date Not available'}")
                st.markdown(f"**📝 Case Brief:** {case_row[7] if case_row[7] else 'N/A'}")
                st.markdown(f"**⚖️ Affidavit Details:** {case_row[8] if case_row[8] else 'N/A'}")
                st.markdown(f"**📂 Main App Details:** {case_row[9] if case_row[9] else 'N/A'}")

            if case_row[12] and os.path.exists(case_row[12]):
                st.markdown("---")
                with open(case_row[12], "rb") as pdf_f:
                    st.download_button(
                        label="📥 Download Attached Case Document (PDF)",
                        data=pdf_f.read(),
                        file_name=os.path.basename(case_row[12]),
                        mime="application/pdf",
                        key=f"download_pdf_{case_id}"
                    )
            else:
                st.markdown("---")
                st.info("ℹ️ No PDF document attached to this case record.")

            st.markdown("---")
            if st.button("❌ Close Window", use_container_width=True, type="primary"):
                st.rerun()

    # --- CUSTOM OUTLINED TABLE GRID WITH PER-ROW 'VIEW DETAILS' BUTTON ---
    # Header Row
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7 = st.columns([0.6, 1.8, 1.0, 2.5, 3.2, 1.8, 1.5])
    h_col1.markdown("**Sr.**")
    h_col2.markdown("**Case No.**")
    h_col3.markdown("**Year**")
    h_col4.markdown("**Applicant**")
    h_col5.markdown("**Category**")
    h_col6.markdown("**Next Hearing**")
    h_col7.markdown("**Action**")
    st.markdown("---")

    # Data Rows
    for idx, row in df.iterrows():
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6, r_col7 = st.columns([0.6, 1.8, 1.0, 2.5, 3.2, 1.8, 1.5])
        
        # Check hearing date for 1-week highlight
        bg_style = ""
        try:
            h_dt = datetime.datetime.strptime(row["Next Hearing Date"], "%d-%m-%Y").date()
            if datetime.date.today() <= h_dt <= datetime.date.today() + datetime.timedelta(days=7):
                bg_style = "background-color: #D8F3DC; padding: 6px; border-radius: 4px;"
        except:
            pass

        r_col1.markdown(f"<div style='{bg_style}'>{idx + 1}</div>", unsafe_allow_html=True)
        r_col2.markdown(f"<div style='{bg_style}'><b>{row['Case Number']}</b></div>", unsafe_allow_html=True)
        r_col3.markdown(f"<div style='{bg_style}'>{row['Filing Year']}</div>", unsafe_allow_html=True)
        r_col4.markdown(f"<div style='{bg_style}'>{row['Applicant']}</div>", unsafe_allow_html=True)
        r_col5.markdown(f"<div style='{bg_style}'>{row['Category']}</div>", unsafe_allow_html=True)
        r_col6.markdown(f"<div style='{bg_style}'>{row['Next Hearing Date']}</div>", unsafe_allow_html=True)
        
        case_id = int(row["ID"])
        with r_col7:
            if st.button(t("view_details"), key=f"btn_view_{case_id}", type="secondary"):
                show_case_modal(case_id)
else:
    st.info(t("no_cases"))
