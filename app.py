import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import plotly.graph_objects as go
import requests
import xml.etree.ElementTree as ET
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

from database import init_db, get_session
from crud import (
    create_user,
    authenticate_user,
    DEFAULT_CATEGORIES,
    add_category,
    get_all_categories,
    add_transaction,
    get_all_transactions,
    delete_transaction
)


init_db()
session = get_session()
load_dotenv()


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_verification_email(to_email, code):
    msg = MIMEText(
        f"Your verification code is: {code}\n\nThis code is valid for 15 minutes."
    )
    msg["Subject"] = "Budget Tracker - Email Verification"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

@st.cache_data(ttl=3600)
def get_exchange_rates():
    url = "https://www.bnr.ro/nbrfxrates.xml"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    rates = {"RON": 1.0}

    for rate in root.findall(".//{http://www.bnr.ro/xsd}Rate"):
        currency = rate.attrib["currency"]
        multiplier = float(rate.attrib.get("multiplier", "1"))
        value = float(rate.text)

        rates[currency] = value / multiplier

    return rates
# seed_categories(session)

st.set_page_config(page_title="Budget Tracker", layout="wide")
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "verification_code" not in st.session_state:
    st.session_state.verification_code = None

if "verification_email" not in st.session_state:
    st.session_state.verification_email = None

if "verification_expiry" not in st.session_state:
    st.session_state.verification_expiry = None

if "pending_username" not in st.session_state:
    st.session_state.pending_username = None

if "pending_password" not in st.session_state:
    st.session_state.pending_password = None
st.markdown("<style>body {}</style>", unsafe_allow_html=True)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

:root {
    --bg: #0b1120;
    --surface: #111827;
    --field: #242936;
    --card: linear-gradient(180deg, rgba(30,41,59,0.92), rgba(15,23,42,0.96));
    --border: rgba(148,163,184,0.18);
    --text: #f8fafc;
    --muted: #94a3b8;
    --green: #34d399;
    --green-bg: rgba(16,185,129,0.16);
    --red: #fb7185;
    --red-bg: rgba(244,63,94,0.16);
    --accent1: #4f46e5;
    --accent2: #7c3aed;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

[data-testid="stSidebar"],
[data-testid="stHeader"] {
    display: none;
}

#MainMenu, footer {
    visibility: hidden;
}


/* NAVBAR */
.block-container {
    padding-top: 85px !important;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    max-width: 920px;
    margin: auto;
}

.fixed-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999999;
    height: 72px;
    padding: 0 26px;
    background: rgba(11,17,32,0.96);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.nav-brand {
    display: flex;
    flex-direction: column;
}

.nav-title {
    font-size: 21px;
    font-weight: 800;
    color: white;
}

.nav-subtitle {
    margin-top: 4px;
    font-size: 12px;
    color: #94a3b8;
}

.user-pill {
    position: fixed !important;
    top: 18px !important;
    right: 420px !important;
    height: 36px;
    min-width: 140px;
    padding: 0 12px 0 9px;
    border-radius: 999px;
    background: #111827;
    border: 1px solid rgba(148,163,184,0.28);
    display: flex;
    align-items: center;
    gap: 9px;
    color: #e5e7eb;
    font-size: 12px;
    font-weight: 650;
    z-index: 1000001;
}

.avatar {
    width: 23px;
    height: 23px;
    border-radius: 50%;
    background: #7c3aed;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 12px;
}

.st-key-top_nav_buttons {
    position: fixed;
    top: 18px;
    right: 24px;
    z-index: 1000000;
    width: 380px;
}

.st-key-top_nav_buttons .stButton > button {
    width: 120px;
    height: 36px !important;
    min-width: unset !important;
    padding: 0 10px !important;
    border-radius: 7px;
    background: #111827 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(148,163,184,0.28) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
}

.st-key-top_nav_buttons .stButton > button:hover {
    background: #1e293b !important;
    border-color: rgba(148,163,184,0.65) !important;
}
        
.st-key-top_nav_buttons div[data-testid="column"] {
    gap: 8px;
}

.st-key-top_nav_buttons .stButton > button:hover {
    background: #1e293b !important;
    border-color: rgba(148,163,184,0.5) !important;
    transform: translateY(-1px);
}
/* TITLURI */
h1 {
    font-size: 34px !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em;
    color: var(--text) !important;
}

h2, h3 {
    font-weight: 750 !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
}

label {
    font-size: 13px !important;
    color: var(--muted) !important;
    margin-bottom: 6px !important;
}

/* CARDURI */
.card {
    background: var(--card);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid var(--border);
    transition: all 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.28);
}

.metric-title {
    font-size: 13px;
    color: var(--muted);
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
}

.positive {
    color: var(--green);
}

.negative {
    color: var(--red);
}

.transaction-card {
    margin-bottom: 12px;
}

/* INPUTURI CLEAN */
.stTextInput input,
.stDateInput input {
    background: var(--field) !important;
    color: var(--text) !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    font-size: 15px !important;
}

.stTextInput div[data-baseweb="input"],
.stDateInput div[data-baseweb="input"] {
    background: var(--field) !important;
    border: 1px solid rgba(148,163,184,0.22) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

/* SELECTBOX FIX */
.stSelectbox div[data-baseweb="select"],
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--field) !important;
    border-color: rgba(148,163,184,0.22) !important;
    color: var(--text) !important;
    box-shadow: none !important;
}

.stSelectbox div[data-baseweb="select"] {
    border: 1px solid rgba(148,163,184,0.22) !important;
    border-radius: 10px !important;
}

/* cand dai click pe select */
.stSelectbox div[data-baseweb="select"]:focus-within {
    border-color: rgba(148,163,184,0.45) !important;
    box-shadow: none !important;
}

/* text select */
.stSelectbox span {
    color: #f8fafc !important;
}

/* sageata select */
.stSelectbox svg {
    color: #94a3b8 !important;
}

/* dropdown deschis */
div[data-baseweb="popover"] {
    background: #111827 !important;
}

ul[role="listbox"] {
    background: #111827 !important;
    border: 1px solid rgba(148,163,184,0.22) !important;
    border-radius: 10px !important;
    padding: 6px !important;
}

/* optiuni dropdown */
li[role="option"] {
    background: transparent !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
}

/* hover optiune */
li[role="option"]:hover {
    background: #1f2937 !important;
    color: #ffffff !important;
}
.icon-box {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: #0f172a;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.arrow-income::before {
    content: "↑";
    color: #34d399;
}

.arrow-expense::before {
    content: "↓";
    color: #fb7185;
}
            
h1 {
    font-size: 27px !important;
    margin-bottom: 18px !important;
}

h2 {
    font-size: 22px !important;
}

.stTextInput,
.stDateInput,
.stSelectbox {
    margin-bottom: 8px !important;
}

.stTextInput input,
.stDateInput input {
    height: 38px !important;
    font-size: 13px !important;
}

.stSelectbox div[data-baseweb="select"] {
    min-height: 38px !important;
}

.card {
    padding: 14px;
}

.metric-title {
    font-size: 12px;
}

.metric-value {
    font-size: 20px;
}

.stButton > button {
    height: 38px !important;
}
            
.badge {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.08);
}

.st-key-top_nav_buttons div[data-testid="column"] {
    display: flex;
    justify-content: center;
}

</style>
""", unsafe_allow_html=True)


# LOGIN / REGISTER
if st.session_state.user_id is None:
    st.title("Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        identifier = st.text_input("Username or Email", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            user = authenticate_user(session, identifier, password)

            if user:
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.page = "Dashboard"
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_email = st.text_input("Email", key="reg_email")
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Send Verification Code", key="send_code_btn"):
            if not new_email or not new_user or not new_pass:
                st.error("Please fill in all fields.")
            else:
                code = str(random.randint(100000, 999999))

                st.session_state.verification_code = code
                st.session_state.verification_email = new_email
                st.session_state.verification_expiry = datetime.now() + timedelta(minutes=15)

                st.session_state.pending_username = new_user
                st.session_state.pending_password = new_pass

                send_verification_email(new_email, code)

                st.success("Verification code sent. Check your email.")

        verification_input = st.text_input("Enter verification code", key="verification_input")

        if st.button("Verify & Create Account", key="verify_create_btn"):
            if not st.session_state.verification_code:
                st.error("Please request a verification code first.")

            elif datetime.now() > st.session_state.verification_expiry:
                st.error("Verification code expired. Please request a new one.")

            elif verification_input != st.session_state.verification_code:
                st.error("Invalid verification code.")

            else:
                user = create_user(
                    session,
                    st.session_state.pending_username,
                    st.session_state.verification_email,
                    st.session_state.pending_password
                )

                if user:
                    st.session_state.user_id = user.id
                    st.session_state.username = user.username
                    st.session_state.page = "Dashboard"

                    st.session_state.verification_code = None
                    st.session_state.verification_email = None
                    st.session_state.verification_expiry = None
                    st.session_state.pending_username = None
                    st.session_state.pending_password = None

                    st.success("Account created successfully!")
                    st.rerun()

                else:
                    st.error("Username or email already exists.")

    st.stop()


# PAGE STATE
page = st.session_state.page

username = st.session_state.get("username", "User")
initial = username[0].upper() if username else "U"

st.html(f"""
<div class="fixed-navbar">
    <div class="nav-brand">
        <div class="nav-title">Budget Tracker</div>
        <div class="nav-subtitle">Personal finance dashboard</div>
    </div>

    <div class="user-pill">
        <div class="avatar">{initial}</div>
        <span>{username}</span>
    </div>
</div>
""")

nav = st.container(key="top_nav_buttons")

with nav:
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Dashboard", key="btn_dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col2:
        if st.button("Transactions", key="btn_transactions", use_container_width=True):
            st.session_state.page = "Transactions"
            st.rerun()

    with col3:
        if st.button("Logout", key="btn_logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.page = "Dashboard"
            st.rerun()

page = st.session_state.page

rates = get_exchange_rates()

currency = st.selectbox(
    "Display currency",
    ["RON", "EUR", "USD", "GBP", "CHF"],
    index=0
)

def convert_from_ron(amount):
    return amount / rates[currency]

def money(amount):
    return f"{convert_from_ron(amount):.2f} {currency}"

# DASHBOARD
if page == "Dashboard":
    st.title("Dashboard")

    transactions = get_all_transactions(session, st.session_state.user_id)

    if not transactions:
        st.info("No transactions to display. Please add some transactions first.")
    else:
        total_income = sum(t.amount for t in transactions if t.category.type == "income")
        total_expense = sum(t.amount for t in transactions if t.category.type == "expense")
        balance = total_income - total_expense

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Balance</div>
                <div class="metric-value {'positive' if balance >= 0 else 'negative'}">
                    {money(balance)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Total Income</div>
                <div class="metric-value positive">{money(total_income)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Total Expense</div>
                <div class="metric-value negative">{money(total_expense)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        expense_data = [
            {"Category": t.category.name, "Amount": t.amount}
            for t in transactions
            if t.category.type == "expense"
        ]

        if expense_data:
            df_expenses = pd.DataFrame(expense_data)
            df_grouped = df_expenses.groupby("Category").sum().reset_index()

            labels = df_grouped["Category"].tolist()
            values = [convert_from_ron(v) for v in df_grouped["Amount"].tolist()]
            total_expenses_chart = sum(values)

            modern_colors = [
                "#6366f1",
                "#34d399",
                "#fb7185",
                "#fbbf24",
                "#38bdf8",
                "#a78bfa",
                "#f97316",
                "#2dd4bf",
            ]

            colors = [modern_colors[i % len(modern_colors)] for i in range(len(labels))]

            fig1 = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.62,
                        sort=False,
                        direction="clockwise",
                        textinfo="percent",
                        textposition="inside",
                        insidetextorientation="horizontal",
                        textfont=dict(size=13, color="white"),
                        marker=dict(
                            colors=colors,
                            line=dict(color="#0b1120", width=5)
                        ),
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Amount: %{value:.2f} {currency}<br>"
                            "Share: %{percent}<extra></extra>"
                        )
                    )
                ]
            )

            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(color="#f8fafc", size=13),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=0.82,
                    font=dict(size=12, color="#cbd5e1"),
                    itemclick="toggle",
                    itemdoubleclick="toggleothers"
                ),
                hoverlabel=dict(
                    bgcolor="#111827",
                    bordercolor="rgba(148,163,184,0.25)",
                    font_size=13,
                    font_family="Inter",
                    font_color="#f8fafc"
                ),
                annotations=[
                    dict(
                        text=f"<b>{total_expenses_chart:.0f}</b><br><span style='font-size:12px;color:#94a3b8'>{currency} spent</span>",
                        x=0.5,
                        y=0.5,
                        font=dict(size=18, color="#f8fafc"),
                        showarrow=False
                    )
                ]
            )

            st.markdown("""
            <div class="chart-card">
                <div class="chart-title">Expenses by Category</div>
                <div class="chart-subtitle">Interactive breakdown of your spending</div>
            """, unsafe_allow_html=True)

            st.plotly_chart(
                fig1,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                    "showTips": False
                },
                key="expenses_donut_chart"
            )
            st.markdown("""
            <style>
            .chart-hint {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #111827;
                color: #cbd5e1;
                padding: 10px 14px;
                border-radius: 10px;
                border: 1px solid rgba(148,163,184,0.2);
                font-size: 13px;
                z-index: 9999;
                opacity: 0.85;
            }
            .chart-hint:hover {
                opacity: 1;
            }
            </style>

            <div class="chart-hint">
                Double-click on legend to isolate a category
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        df_all = pd.DataFrame([
            {
                "Date": t.date,
                "Amount": t.amount if t.category.type == "income" else -t.amount,
            }
            for t in transactions
        ])

        df_all = df_all.sort_values("Date")
        df_all["Balance"] = df_all["Amount"].cumsum()
        df_all["Balance"] = df_all["Balance"].apply(convert_from_ron)

        fig2 = px.line(df_all, x="Date", y="Balance")

        fig2.update_traces(
            line=dict(width=3, color="#6366f1"),
            mode="lines+markers",
            marker=dict(size=7, color="#8b5cf6")
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=13),
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                gridcolor="rgba(148,163,184,0.12)",
                linecolor="rgba(148,163,184,0.18)"
            ),
            yaxis=dict(
                gridcolor="rgba(148,163,184,0.12)",
                linecolor="rgba(148,163,184,0.18)"
            )
        )

        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Balance Over Time</div>
            <div class="chart-subtitle">Track how your balance changes after every transaction</div>
        """, unsafe_allow_html=True)

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            },
            key="balance_over_time_chart"
        )

        st.markdown("</div>", unsafe_allow_html=True)


# TRANSACTIONS
elif page == "Transactions":
    st.title("Transactions")

    col1, col2 = st.columns([1, 1])

    with col1:
        amount_input = st.text_input("Amount", value="0.01")

    with col2:
        transaction_date = st.date_input("Date", value=date.today())

    description = st.text_input(
        "Description",
        placeholder="Example: Groceries, salary, rent..."
    )

    category_names = [name for name, t in DEFAULT_CATEGORIES] + ["Other"]
    selected_category = st.selectbox("Category", options=category_names)

    custom_category = ""
    custom_type = None

    if selected_category == "Other":
        custom_category = st.text_input("Custom category name")
        custom_type = st.selectbox("Type", ["expense", "income"])

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        submitted = st.button("Add Transaction", use_container_width=True)

    if submitted:
        try:
            amount_input_value = float(amount_input)

            amount = amount_input_value * rates[currency]
            if amount <= 0:
                st.error("Amount must be greater than 0.")
                st.stop()
        except ValueError:
            st.error("Please enter a valid amount.")
            st.stop()

        categories = get_all_categories(session, st.session_state.user_id)

        if selected_category == "Other":
            final_category_name = custom_category.strip()
            final_category_type = custom_type

            if final_category_name == "":
                st.error("Category name cannot be empty.")
                st.stop()
        else:
            final_category_name = selected_category
            final_category_type = next(
                t for name, t in DEFAULT_CATEGORIES
                if name == selected_category
            )

        existing_category = None

        for c in categories:
            if c.name == final_category_name and c.type == final_category_type:
                existing_category = c
                break

        if existing_category:
            category_id = existing_category.id
        else:
            new_category = add_category(
                session,
                final_category_name,
                final_category_type,
                st.session_state.user_id
            )
            category_id = new_category.id

        add_transaction(
            session,
            amount=amount,
            date=transaction_date,
            description=description,
            category_id=category_id,
            user_id=st.session_state.user_id
        )

        st.success("Transaction added successfully!")
        st.rerun()

    st.subheader("All Transactions")

    transactions = get_all_transactions(session, st.session_state.user_id)

    if not transactions:
        st.info("No transactions yet.")
    else:
        for t in transactions:
            is_income = t.category.type == "income"

            amount_color = "#34d399" if is_income else "#fb7185"
            amount_sign = "+" if is_income else "-"
            type_label = "Income" if is_income else "Expense"
            type_bg = "rgba(16,185,129,0.16)" if is_income else "rgba(244,63,94,0.16)"
            type_color = "#34d399" if is_income else "#fb7185"

            icon_class = "arrow-income" if is_income else "arrow-expense"

            st.html(f"""
<div class="card transaction-card">
    <div style="display:flex; align-items:center; justify-content:space-between; gap:18px;">
        <div style="display:flex; align-items:center; gap:14px; min-width:260px;">
            <div class="icon-box">
                <span class="arrow-icon {icon_class}"></span>
            </div>

            <div>
                <div style="font-size:15px; font-weight:600; color:#f8fafc;">
                    {t.description or "No description"}
                </div>
                <div style="font-size:13px; color:#94a3b8; margin-top:3px;">
                    {t.category.name} · {t.date}
                </div>
            </div>
        </div>

        <div class="badge" style="background:{type_bg}; color:{type_color};">
            {type_label}
        </div>

        <div class="amount" style="color:{amount_color}; min-width:120px; text-align:right;">
            {amount_sign}{money(t.amount)}
        </div>
    </div>
</div>
""")

            if st.button("Delete", key=f"del_tr_{t.id}"):
                delete_transaction(session, t.id, st.session_state.user_id)
                st.rerun()