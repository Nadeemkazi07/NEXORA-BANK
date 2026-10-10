import streamlit as st
import pandas as pd
import hashlib
import hmac
import re
import secrets
from sqlalchemy import create_engine, text


# ---------- NEXORA BANK DARK THEME ----------
st.markdown("""
<style>
/* Main application */
.stApp {
    background: #0b1020;
    color: #e5e7eb;
}

[data-testid="stHeader"] {
    background: #0b1020;
}

[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263244;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Text */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #e5e7eb;
}

/* Login page */
.login-wrap {
    text-align: center;
    padding: 55px 20px 20px 20px;
}

.login-logo {
    font-size: 64px;
    margin-bottom: 8px;
}

.login-brand {
    font-size: 38px;
    font-weight: 800;
    letter-spacing: 3px;
    color: #f8fafc !important;
}

.login-caption {
    color: #94a3b8 !important;
    font-size: 16px;
    margin-top: 8px;
    margin-bottom: 35px;
}

/* Cards */
.nexora-card {
    background: #111827;
    border: 1px solid #263244;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 18px;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background-color: #111827 !important;
    color: #f8fafc !important;
    border-color: #374151 !important;
}

.stTextInput input::placeholder {
    color: #64748b !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    border-radius: 9px;
    border: 1px solid #374151;
    background: #1f2937;
    color: #f8fafc !important;
    font-weight: 600;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border-color: #64748b;
    background: #374151;
}

/* Tables/dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #263244;
    border-radius: 10px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #263244;
    border-radius: 12px;
    padding: 14px;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #94a3b8 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #f8fafc !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #111827;
    border: 1px solid #263244;
    border-radius: 10px;
}

/* Alerts */
.stAlert {
    background: #111827;
}

/* Markdown links */
a {
    color: #93c5fd !important;
}
</style>
""", unsafe_allow_html=True)
# ---------- END DARK THEME ----------

st.set_page_config(page_title="NEXORA BANK", page_icon="🏦", layout="wide")

def get_engine():
    return create_engine(
        "mysql+pymysql://root:system@localhost:3306/nexora_bank",
        pool_pre_ping=True
    )

def run_query(query, params=None):
    engine = get_engine()
    try:
        with engine.connect() as connection:
            return pd.read_sql(text(query), connection, params=params or {})
    finally:
        engine.dispose()

def money(value):
    return "₹0.00" if pd.isna(value) else f"₹{float(value):,.2f}"

def number(value):
    return "0" if pd.isna(value) else f"{int(value):,}"

def logout():
    st.session_state.clear()
    st.rerun()

def password_is_valid(password):
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character."
    return True, ""


def hash_password(password):
    iterations = 120000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_password):
    stored_password = str(stored_password)
    if stored_password.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt_hex, digest_hex = stored_password.split("$", 3)
            digest = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"),
                bytes.fromhex(salt_hex), int(iterations)
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        except (ValueError, TypeError):
            return False
    # Existing accounts can still log in once; successful login upgrades the password.
    return hmac.compare_digest(password, stored_password)


def authenticate(username, password, expected_role):
    result = run_query("""
        SELECT User_ID, Username, Password, Role, Customer_ID
        FROM users
        WHERE Username = :username
        LIMIT 1
    """, {"username": username})

    if result.empty:
        return None

    user = result.iloc[0]
    if str(user["Role"]).strip().lower() != expected_role.lower():
        return None
    if not verify_password(password, user["Password"]):
        return None

    if not str(user["Password"]).startswith("pbkdf2_sha256$"):
        engine = get_engine()
        try:
            with engine.begin() as connection:
                connection.execute(
                    text("""
                        UPDATE users SET Password = :password
                        WHERE User_ID = :user_id
                    """),
                    {"password": hash_password(password), "user_id": int(user["User_ID"])}
                )
        finally:
            engine.dispose()

    return user

def login_form(expected_role):
    label = "User" if expected_role.lower() == "user" else "Admin"

    with st.form(f"{expected_role.lower()}_login_form"):
        username = st.text_input("Username", placeholder=f"Enter {label.lower()} username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button = st.form_submit_button(f"🔐 {label} Login", use_container_width=True)

    if login_button:
        username = username.strip()
        if not username or not password:
            st.warning("Please enter username and password.")
            return

        user = authenticate(username, password, expected_role)
        if user is None:
            st.error(f"Invalid {label.lower()} username/password or incorrect account role.")
            return

        st.session_state.logged_in = True
        st.session_state.username = str(user["Username"])
        st.session_state.role = str(user["Role"])
        st.session_state.customer_id = None if pd.isna(user["Customer_ID"]) else str(user["Customer_ID"])
        st.rerun()

def forgot_password_form():
    """Reset a User password after verifying Username + Customer ID."""
    st.subheader("🔑 Forgot Password")
    st.caption("Verify your NEXORA BANK account before creating a new password.")

    with st.form("forgot_password_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your registered username"
        )
        customer_id = st.text_input(
            "Customer ID",
            placeholder="Example: C100001"
        )
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter your new password"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password"
        )
        reset_button = st.form_submit_button(
            "🔄 Reset Password",
            use_container_width=True
        )

    if not reset_button:
        return

    username = username.strip()
    customer_id = customer_id.strip().upper()

    if not username or not customer_id or not new_password or not confirm_password:
        st.warning("Please fill in all fields.")
        return

    if new_password != confirm_password:
        st.error("New passwords do not match.")
        return

    valid, message = password_is_valid(new_password)
    if not valid:
        st.error(message)
        return

    account = run_query(
        """
        SELECT User_ID
        FROM users
        WHERE Username = :username
          AND Customer_ID = :customer_id
          AND Role = 'User'
        LIMIT 1
        """,
        {"username": username, "customer_id": customer_id}
    )

    if account.empty:
        st.error("Username and Customer ID could not be verified.")
        return

    engine = get_engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    UPDATE users
                    SET Password = :password
                    WHERE User_ID = :user_id
                      AND Role = 'User'
                """),
                {
                    "password": hash_password(new_password),
                    "user_id": int(account.iloc[0]["User_ID"])
                }
            )
        st.success(
            "Password reset successfully. You can now log in with your new password."
        )
    except Exception as e:
        st.error(f"Could not reset password: {e}")
    finally:
        engine.dispose()


def register_form():
    st.subheader("📝 Create a User Account")
    st.caption("Register using an existing NEXORA BANK Customer ID.")

    with st.form("register_form"):
        customer_id = st.text_input("Customer ID", placeholder="Example: C100001")
        username = st.text_input("Choose Username", placeholder="Create a username")
        password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_button = st.form_submit_button("📝 Register", use_container_width=True)

    if not register_button:
        return

    customer_id = customer_id.strip().upper()
    username = username.strip()

    if not customer_id or not username or not password or not confirm_password:
        st.warning("Please fill in all registration fields.")
        return

    if password != confirm_password:
        st.error("Passwords do not match.")
        return

    valid, message = password_is_valid(password)
    if not valid:
        st.error(message)
        st.info("Use 8+ characters with uppercase, lowercase, a number and a special character.")
        return

    customer = run_query(
        "SELECT Customer_ID, Name FROM customers WHERE Customer_ID = :customer_id LIMIT 1",
        {"customer_id": customer_id}
    )
    if customer.empty:
        st.error("Customer ID was not found in the NEXORA BANK customer records.")
        return

    existing_username = run_query(
        "SELECT User_ID FROM users WHERE Username = :username LIMIT 1",
        {"username": username}
    )
    if not existing_username.empty:
        st.error("That username is already registered. Please choose another username.")
        return

    existing_customer = run_query(
        "SELECT User_ID FROM users WHERE Customer_ID = :customer_id LIMIT 1",
        {"customer_id": customer_id}
    )
    if not existing_customer.empty:
        st.error("This Customer ID already has a login account. Please use the existing login.")
        return

    engine = get_engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO users (Username, Password, Role, Customer_ID)
                    VALUES (:username, :password, 'User', :customer_id)
                """),
                {"username": username, "password": hash_password(password), "customer_id": customer_id}
            )
        customer_name = str(customer.iloc[0]["Name"])
        st.success(f"Registration successful! Welcome, {customer_name}. You can now log in with your new username.")
    except Exception as e:
        st.error(f"Registration failed: {e}")
    finally:
        engine.dispose()

def login():
    st.markdown(
        '<div class="login-wrap"><div class="login-logo">🏦</div>'
        '<div class="login-brand">NEXORA BANK</div>'
        '<div class="login-caption">Secure Banking Analytics Portal</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("### Choose your login")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 👤 Customer / User")
        st.caption("Access your personal banking dashboard.")
        if st.button("Continue to User Login", use_container_width=True, type="primary"):
            st.session_state.login_type = "User"
            st.rerun()

    with col2:
        st.markdown("#### 🔐 Administrator")
        st.caption("Access banking analytics and administration.")
        if st.button("Continue to Admin Login", use_container_width=True):
            st.session_state.login_type = "Admin"
            st.rerun()

    st.markdown("---")
    st.caption("New customer? Register from the User Login page using an existing Customer ID.")

    role = st.session_state.get("login_type")
    if role in ("User", "Admin"):
        st.markdown(f"## {'👤 User Login' if role == 'User' else '🔐 Admin Login'}")

        if role == "User":
            login_tab, register_tab, forgot_tab = st.tabs(
                ["🔐 Login", "📝 Register", "🔑 Forgot Password"]
            )
            with login_tab:
                login_form("User")
            with register_tab:
                register_form()
            with forgot_tab:
                forgot_password_form()
        else:
            login_form("Admin")

        if st.button("← Back to login selection", use_container_width=True):
            st.session_state.login_type = None
            st.rerun()

def admin_dashboard():
    st.header("🏠 Executive Dashboard")
    st.caption("NEXORA BANK — MySQL-powered banking analytics")

    customer = run_query("""
        SELECT COUNT(*) AS total_customers,
               ROUND(AVG(Monthly_Income),2) AS avg_income,
               ROUND(AVG(Credit_Score),2) AS avg_credit_score
        FROM customers
    """).iloc[0]

    transaction = run_query("""
        SELECT COUNT(*) AS total_transactions,
               ROUND(SUM(Amount),2) AS transaction_value,
               ROUND(AVG(Amount),2) AS avg_transaction
        FROM transactions
    """).iloc[0]

    loan = run_query("""
        SELECT COUNT(*) AS total_loans,
               ROUND(SUM(Loan_Amount),2) AS loan_value,
               SUM(Default_Flag) AS defaulted_loans,
               ROUND(SUM(Default_Flag)*100.0/COUNT(*),2) AS default_rate
        FROM loans
    """).iloc[0]

    account = run_query("""
        SELECT COUNT(*) AS total_accounts,
               ROUND(SUM(Current_Balance),2) AS total_balance
        FROM accounts
    """).iloc[0]

    cols = st.columns(4)
    cols[0].metric("👥 Customers", number(customer["total_customers"]))
    cols[1].metric("💳 Transactions", number(transaction["total_transactions"]))
    cols[2].metric("🏦 Loans", number(loan["total_loans"]))
    cols[3].metric("⚠️ Default Rate", f'{loan["default_rate"]:.2f}%')

    st.markdown("---")
    cols = st.columns(4)
    cols[0].metric("💰 Transaction Value", money(transaction["transaction_value"]))
    cols[1].metric("💵 Loan Portfolio", money(loan["loan_value"]))
    cols[2].metric("🏧 Account Balance", money(account["total_balance"]))
    cols[3].metric("⭐ Avg Credit Score", f'{customer["avg_credit_score"]:.2f}')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Transaction Status")
        df = run_query("""
            SELECT Transaction_Status, COUNT(*) AS Transaction_Count
            FROM transactions GROUP BY Transaction_Status
            ORDER BY Transaction_Count DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            st.bar_chart(df.set_index("Transaction_Status"))

    with col2:
        st.subheader("🏦 Loan Type Portfolio")
        df = run_query("""
            SELECT Loan_Type, ROUND(SUM(Loan_Amount),2) AS Total_Loan_Amount
            FROM loans GROUP BY Loan_Type
            ORDER BY Total_Loan_Amount DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            st.bar_chart(df.set_index("Loan_Type"))

    st.success("✅ NEXORA BANK connected successfully to MySQL")

def customer_analysis():
    st.header("👥 Customer Analysis")
    kpi = run_query("""
        SELECT COUNT(*) AS customers,
               ROUND(AVG(Monthly_Income),2) AS avg_income,
               ROUND(AVG(Credit_Score),2) AS avg_score,
               ROUND(AVG(Current_Balance),2) AS avg_balance
        FROM customers c LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
    """).iloc[0]

    cols = st.columns(4)
    cols[0].metric("Customers", number(kpi["customers"]))
    cols[1].metric("Avg Income", money(kpi["avg_income"]))
    cols[2].metric("Avg Credit Score", f'{kpi["avg_score"]:.2f}')
    cols[3].metric("Avg Balance", money(kpi["avg_balance"]))
    st.markdown("---")

    search = st.text_input("🔎 Search by Customer ID or Name")
    query = """
        SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Monthly_Income,c.Credit_Score,
               a.Account_Type,a.Account_Status,ROUND(a.Current_Balance,2) AS Current_Balance
        FROM customers c LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
    """
    if search.strip():
        query += " WHERE c.Customer_ID LIKE :search OR c.Name LIKE :search"
        df = run_query(query, {"search": f"%{search.strip()}%"})
    else:
        df = run_query(query + " LIMIT 1000")

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("📥 Download Customer Data", df.to_csv(index=False),
                       "nexora_customers.csv", "text/csv")

def branch_analysis():
    st.header("🏢 Branch Analysis")
    st.caption("Branch-wise customers, accounts, transactions, loans and balances")

    # Separate aggregations prevent row multiplication when tables are joined.
    branch_df = run_query("""
        SELECT
            b.Branch_ID,
            b.Branch_Name,
            b.City,
            COALESCE(c.Customer_Count, 0) AS Customer_Count,
            COALESCE(a.Account_Count, 0) AS Account_Count,
            COALESCE(t.Transaction_Count, 0) AS Transaction_Count,
            COALESCE(t.Transaction_Value, 0) AS Transaction_Value,
            COALESCE(l.Loan_Count, 0) AS Loan_Count,
            COALESCE(l.Loan_Value, 0) AS Loan_Value,
            COALESCE(c.Average_Credit_Score, 0) AS Average_Credit_Score
        FROM branches b
        LEFT JOIN (
            SELECT Branch_ID,
                   COUNT(*) AS Customer_Count,
                   ROUND(AVG(Credit_Score), 2) AS Average_Credit_Score
            FROM customers
            GROUP BY Branch_ID
        ) c ON b.Branch_ID = c.Branch_ID
        LEFT JOIN (
            SELECT Branch_ID, COUNT(*) AS Account_Count
            FROM accounts
            GROUP BY Branch_ID
        ) a ON b.Branch_ID = a.Branch_ID
        LEFT JOIN (
            SELECT Branch_ID,
                   COUNT(*) AS Transaction_Count,
                   ROUND(SUM(Amount), 2) AS Transaction_Value
            FROM transactions
            GROUP BY Branch_ID
        ) t ON b.Branch_ID = t.Branch_ID
        LEFT JOIN (
            SELECT Branch_ID,
                   COUNT(*) AS Loan_Count,
                   ROUND(SUM(Loan_Amount), 2) AS Loan_Value
            FROM loans
            GROUP BY Branch_ID
        ) l ON b.Branch_ID = l.Branch_ID
        ORDER BY Customer_Count DESC
    """)

    if branch_df.empty:
        st.warning("No branch data was returned from the database.")
        return

    numeric_cols = [
        "Customer_Count", "Account_Count", "Transaction_Count",
        "Transaction_Value", "Loan_Count", "Loan_Value",
        "Average_Credit_Score"
    ]
    for col in numeric_cols:
        branch_df[col] = pd.to_numeric(branch_df[col], errors="coerce").fillna(0)

    st.subheader("📋 Branch Performance")
    st.dataframe(branch_df, use_container_width=True, hide_index=True)

    selected = st.selectbox("Select Branch", branch_df["Branch_Name"].tolist())
    row = branch_df.loc[branch_df["Branch_Name"] == selected].iloc[0]

    cols = st.columns(4)
    cols[0].metric("👥 Customers", number(row["Customer_Count"]))
    cols[1].metric("🏧 Accounts", number(row["Account_Count"]))
    cols[2].metric("💳 Transactions", number(row["Transaction_Count"]))
    cols[3].metric("🏦 Loans", number(row["Loan_Count"]))

    cols = st.columns(3)
    cols[0].metric("Transaction Value", money(row["Transaction_Value"]))
    cols[1].metric("Loan Value", money(row["Loan_Value"]))
    cols[2].metric("Avg Credit Score", f'{row["Average_Credit_Score"]:.2f}')

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Customers by Branch")
        st.bar_chart(
            branch_df[["Branch_Name", "Customer_Count"]].set_index("Branch_Name")
        )

    with col2:
        st.subheader("💰 Loan Value by Branch")
        st.bar_chart(
            branch_df[["Branch_Name", "Loan_Value"]].set_index("Branch_Name")
        )

    st.subheader("💳 Transaction Value by Branch")
    st.bar_chart(
        branch_df[["Branch_Name", "Transaction_Value"]].set_index("Branch_Name")
    )

    st.download_button(
        "📥 Download Branch Analysis",
        branch_df.to_csv(index=False),
        "nexora_branch_analysis.csv",
        "text/csv"
    )

def transaction_analysis():
    st.header("💳 Transaction Analysis")
    kpi = run_query("""
        SELECT COUNT(*) AS total_transactions,ROUND(SUM(Amount),2) AS total_value,
               ROUND(AVG(Amount),2) AS avg_amount,COUNT(DISTINCT Customer_ID) AS unique_customers
        FROM transactions
    """).iloc[0]
    cols = st.columns(4)
    cols[0].metric("Transactions", number(kpi["total_transactions"]))
    cols[1].metric("Total Value", money(kpi["total_value"]))
    cols[2].metric("Average Transaction", money(kpi["avg_amount"]))
    cols[3].metric("Unique Customers", number(kpi["unique_customers"]))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📌 Transaction Status")
        status = run_query("""
            SELECT Transaction_Status,COUNT(*) AS Transaction_Count
            FROM transactions GROUP BY Transaction_Status ORDER BY Transaction_Count DESC
        """)
        st.dataframe(status, use_container_width=True, hide_index=True)
        st.bar_chart(status.set_index("Transaction_Status"))
    with col2:
        st.subheader("💳 Payment Method")
        payment = run_query("""
            SELECT Payment_Method,COUNT(*) AS Transaction_Count,
                   ROUND(SUM(Amount),2) AS Total_Amount,
                   ROUND(AVG(Amount),2) AS Average_Amount
            FROM transactions GROUP BY Payment_Method ORDER BY Total_Amount DESC
        """)
        st.dataframe(payment, use_container_width=True, hide_index=True)
        st.bar_chart(payment.set_index("Payment_Method")["Total_Amount"])

    st.subheader("🏢 Transaction Value by Branch")
    branch = run_query("""
        SELECT b.Branch_ID,b.Branch_Name,b.City,
               COUNT(t.Transaction_ID) AS Transaction_Count,
               ROUND(SUM(t.Amount),2) AS Total_Transaction_Value,
               ROUND(AVG(t.Amount),2) AS Average_Transaction
        FROM transactions t JOIN branches b ON t.Branch_ID=b.Branch_ID
        GROUP BY b.Branch_ID,b.Branch_Name,b.City
        ORDER BY Total_Transaction_Value DESC
    """)
    st.dataframe(branch, use_container_width=True, hide_index=True)
    st.download_button("📥 Download Transaction Analysis", branch.to_csv(index=False),
                       "nexora_transaction_analysis.csv", "text/csv")

def loan_analysis():
    st.header("🏦 Loan Portfolio Analysis")
    kpi = run_query("""
        SELECT COUNT(*) AS total_loans,ROUND(SUM(Loan_Amount),2) AS total_value,
               ROUND(AVG(Loan_Amount),2) AS avg_loan,ROUND(AVG(Interest_Rate),2) AS avg_interest,
               ROUND(AVG(Tenure_Months),2) AS avg_tenure,ROUND(AVG(EMI),2) AS avg_emi,
               SUM(Default_Flag) AS defaults,
               ROUND(SUM(Default_Flag)*100.0/COUNT(*),2) AS default_rate
        FROM loans
    """).iloc[0]
    cols = st.columns(4)
    cols[0].metric("Total Loans", number(kpi["total_loans"]))
    cols[1].metric("Loan Portfolio", money(kpi["total_value"]))
    cols[2].metric("Average Loan", money(kpi["avg_loan"]))
    cols[3].metric("Default Rate", f'{kpi["default_rate"]:.2f}%')
    cols = st.columns(4)
    cols[0].metric("Avg Interest Rate", f'{kpi["avg_interest"]:.2f}%')
    cols[1].metric("Avg Tenure", f'{kpi["avg_tenure"]:.2f} months')
    cols[2].metric("Average EMI", money(kpi["avg_emi"]))
    cols[3].metric("Defaulted Loans", number(kpi["defaults"]))

    loan_type = run_query("""
        SELECT Loan_Type,COUNT(*) AS Total_Loans,SUM(Default_Flag) AS Defaulted_Loans,
               ROUND(SUM(Loan_Amount),2) AS Total_Loan_Amount,
               ROUND(SUM(Default_Flag)*100.0/COUNT(*),2) AS Default_Rate
        FROM loans GROUP BY Loan_Type ORDER BY Total_Loan_Amount DESC
    """)
    st.subheader("📋 Loan Type Analysis")
    st.dataframe(loan_type, use_container_width=True, hide_index=True)
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(loan_type[["Loan_Type","Total_Loan_Amount"]].set_index("Loan_Type"))
    with col2:
        st.bar_chart(loan_type[["Loan_Type","Default_Rate"]].set_index("Loan_Type"))

    credit = run_query("""
        SELECT CASE
            WHEN c.Credit_Score<580 THEN 'Poor'
            WHEN c.Credit_Score<670 THEN 'Fair'
            WHEN c.Credit_Score<740 THEN 'Good'
            ELSE 'Excellent' END AS Credit_Score_Group,
            COUNT(l.Loan_ID) AS Total_Loans,SUM(l.Default_Flag) AS Defaulted_Loans,
            ROUND(AVG(l.Loan_Amount),2) AS Average_Loan_Amount,
            ROUND(SUM(l.Default_Flag)*100.0/COUNT(l.Loan_ID),2) AS Default_Rate
        FROM loans l JOIN customers c ON l.Customer_ID=c.Customer_ID
        GROUP BY Credit_Score_Group ORDER BY Default_Rate DESC
    """)
    st.subheader("⭐ Credit Score Group Analysis")
    st.dataframe(credit, use_container_width=True, hide_index=True)
    st.download_button("📥 Download Loan Analysis", loan_type.to_csv(index=False),
                       "nexora_loan_analysis.csv", "text/csv")

def risk_analysis():
    st.header("⚠️ Risk Analysis")
    risk = run_query("""
        SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Credit_Score,c.Monthly_Income,
               ROUND(a.Current_Balance,2) AS Account_Balance,
               COALESCE(l.Loan_Count,0) AS Loan_Count,
               ROUND(COALESCE(l.Total_Loan_Amount,0),2) AS Total_Loan_Amount,
               COALESCE(l.Default_Count,0) AS Default_Count,
               CASE
                 WHEN c.Credit_Score<580 OR COALESCE(l.Default_Count,0)>=2 THEN 'High Risk'
                 WHEN c.Credit_Score<670 OR COALESCE(l.Default_Count,0)=1 THEN 'Medium Risk'
                 ELSE 'Low Risk' END AS Risk_Category
        FROM customers c
        LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
        LEFT JOIN (
            SELECT Customer_ID,COUNT(*) AS Loan_Count,SUM(Loan_Amount) AS Total_Loan_Amount,
                   SUM(Default_Flag) AS Default_Count
            FROM loans GROUP BY Customer_ID
        ) l ON c.Customer_ID=l.Customer_ID
    """)
    summary = risk.groupby("Risk_Category").size().reset_index(name="Customer_Count")
    cols = st.columns(3)
    for i, category in enumerate(["High Risk","Medium Risk","Low Risk"]):
        value = summary.loc[summary["Risk_Category"]==category,"Customer_Count"]
        cols[i].metric(category, f'{int(value.iloc[0]) if not value.empty else 0:,}')

    selected = st.selectbox("Filter Risk Category", ["All","High Risk","Medium Risk","Low Risk"])
    display_df = risk if selected=="All" else risk[risk["Risk_Category"]==selected]
    st.dataframe(display_df.head(1000), use_container_width=True, hide_index=True)
    st.subheader("📊 Risk Distribution")
    st.bar_chart(summary.set_index("Risk_Category"))
    st.download_button("📥 Download Risk Analysis", risk.to_csv(index=False),
                       "nexora_risk_analysis.csv", "text/csv")

def product_recommendations():
    st.header("🎯 Product Recommendations")
    recommendations = run_query("""
        SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Monthly_Income,c.Credit_Score,
               ROUND(a.Current_Balance,2) AS Account_Balance,
               CASE
                 WHEN c.Credit_Score>=720 AND a.Current_Balance>=300000 THEN 'Premium Credit Card'
                 WHEN c.Credit_Score>=680 AND a.Current_Balance>=200000 THEN 'Credit Card'
                 WHEN c.Monthly_Income>=60000 AND a.Current_Balance>=100000 THEN 'Investment Product'
                 WHEN c.Monthly_Income>=45000 AND c.Credit_Score>=650 THEN 'Personal Loan'
                 ELSE 'Savings Account' END AS Recommended_Product
        FROM customers c JOIN accounts a ON c.Customer_ID=a.Customer_ID
    """)
    summary = recommendations.groupby("Recommended_Product").size().reset_index(name="Customer_Count").sort_values("Customer_Count",ascending=False)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.bar_chart(summary.set_index("Recommended_Product"))
    branch_summary = recommendations.groupby(["Branch_ID","Recommended_Product"]).size().reset_index(name="Customer_Count")
    st.subheader("🏢 Branch-wise Recommendations")
    st.dataframe(branch_summary, use_container_width=True, hide_index=True)
    selected = st.selectbox("Select Product", ["All"] + summary["Recommended_Product"].tolist())
    display_df = recommendations if selected=="All" else recommendations[recommendations["Recommended_Product"]==selected]
    st.dataframe(display_df.head(1000), use_container_width=True, hide_index=True)
    st.download_button("📥 Download Product Recommendations", recommendations.to_csv(index=False),
                       "nexora_product_recommendations.csv", "text/csv")

def reports():
    st.header("📥 Reports & Downloads")
    reports_list = {
        "Customer Report": "SELECT Customer_ID,Name,Branch_ID,Monthly_Income,Credit_Score FROM customers",
        "Account Report": "SELECT Account_ID,Customer_ID,Branch_ID,Account_Type,Account_Status,Opening_Balance,Current_Balance FROM accounts",
        "Transaction Report": "SELECT Transaction_ID,Customer_ID,Branch_ID,Transaction_Date,Transaction_Type,Payment_Method,Amount,Transaction_Status FROM transactions",
        "Loan Report": "SELECT Loan_ID,Customer_ID,Branch_ID,Loan_Type,Loan_Amount,Interest_Rate,Tenure_Months,Loan_Status,Default_Flag,Loan_Start_Date,EMI FROM loans"
    }
    for name, query in reports_list.items():
        with st.expander(name):
            df = run_query(query)
            st.write(f"Rows: {len(df):,}")
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {name}", df.to_csv(index=False),
                               f"{name.lower().replace(' ','_')}.csv", "text/csv", key=name)

def user_dashboard():
    st.header("👤 Customer Dashboard")
    customer_id = st.session_state.get("customer_id")
    if not customer_id:
        st.warning("Your user account is not linked to a Customer_ID.")
        return

    customer = run_query("""
        SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Monthly_Income,c.Credit_Score,
               a.Account_Type,a.Account_Status,a.Opening_Balance,a.Current_Balance
        FROM customers c LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
        WHERE c.Customer_ID=:customer_id LIMIT 1
    """, {"customer_id": customer_id})

    if customer.empty:
        st.error("Customer record not found.")
        return

    c = customer.iloc[0]
    st.subheader(f"Welcome, {c['Name']} 👋")
    cols = st.columns(4)
    cols[0].metric("Customer ID", c["Customer_ID"])
    cols[1].metric("Credit Score", f'{c["Credit_Score"]:.0f}')
    cols[2].metric("Account Balance", money(c["Current_Balance"]))
    cols[3].metric("Monthly Income", money(c["Monthly_Income"]))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏧 Account Details")
        info = pd.DataFrame({
            "Field":["Branch","Account Type","Account Status","Opening Balance","Current Balance"],
            "Value":[c["Branch_ID"],c["Account_Type"],c["Account_Status"],money(c["Opening_Balance"]),money(c["Current_Balance"])]
        })
        st.dataframe(info, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("💳 Recent Transactions")
        tx = run_query("""
            SELECT Transaction_ID,Transaction_Date,Payment_Method,Amount,Transaction_Status
            FROM transactions WHERE Customer_ID=:customer_id
            ORDER BY Transaction_Date DESC LIMIT 10
        """, {"customer_id": customer_id})
        st.dataframe(tx, use_container_width=True, hide_index=True)

    st.subheader("🏦 Your Loans")
    loans = run_query("""
        SELECT Loan_ID,Loan_Type,Loan_Amount,Interest_Rate,Tenure_Months,EMI,Loan_Status,Default_Flag
        FROM loans WHERE Customer_ID=:customer_id ORDER BY Loan_Start_Date DESC
    """, {"customer_id": customer_id})
    if loans.empty:
        st.info("No loans found for your customer account.")
    else:
        st.dataframe(loans, use_container_width=True, hide_index=True)

    recommendation = run_query("""
        SELECT CASE
          WHEN c.Credit_Score>=720 AND a.Current_Balance>=300000 THEN 'Premium Credit Card'
          WHEN c.Credit_Score>=680 AND a.Current_Balance>=200000 THEN 'Credit Card'
          WHEN c.Monthly_Income>=60000 AND a.Current_Balance>=100000 THEN 'Investment Product'
          WHEN c.Monthly_Income>=45000 AND c.Credit_Score>=650 THEN 'Personal Loan'
          ELSE 'Savings Account' END AS Recommended_Product
        FROM customers c JOIN accounts a ON c.Customer_ID=a.Customer_ID
        WHERE c.Customer_ID=:customer_id LIMIT 1
    """, {"customer_id": customer_id})
    if not recommendation.empty:
        st.success(f'Recommended Product: **{recommendation.iloc[0]["Recommended_Product"]}**')


def update_username(new_username):
    """Update the logged-in user's username after checking uniqueness."""
    new_username = new_username.strip()

    if not new_username:
        return False, "Username cannot be empty."

    current_username = str(st.session_state.get("username", ""))

    if new_username == current_username:
        return False, "Please enter a different username."

    existing = run_query(
        "SELECT User_ID FROM users WHERE Username = :username LIMIT 1",
        {"username": new_username}
    )

    if not existing.empty:
        return False, "That username is already in use. Please choose another one."

    engine = get_engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    UPDATE users
                    SET Username = :new_username
                    WHERE Username = :current_username
                """),
                {
                    "new_username": new_username,
                    "current_username": current_username
                }
            )
        st.session_state.username = new_username
        return True, "Username updated successfully."
    except Exception as e:
        return False, f"Could not update username: {e}"
    finally:
        engine.dispose()


def update_password(current_password, new_password, confirm_password):
    """Change the logged-in user's password using the same verification as login."""
    if not current_password or not new_password or not confirm_password:
        return False, "Please fill in all password fields."

    if new_password != confirm_password:
        return False, "New password and confirmation password do not match."

    if new_password == current_password:
        return False, "New password must be different from the current password."

    valid, message = password_is_valid(new_password)
    if not valid:
        return False, message

    username = str(st.session_state.get("username", ""))

    account = run_query(
        "SELECT User_ID, Password FROM users WHERE Username = :username LIMIT 1",
        {"username": username}
    )

    if account.empty:
        return False, "User account could not be found."

    if not verify_password(current_password, account.iloc[0]["Password"]):
        return False, "Current password is incorrect."

    engine = get_engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    UPDATE users
                    SET Password = :new_password
                    WHERE User_ID = :user_id
                """),
                {
                    "new_password": hash_password(new_password),
                    "user_id": int(account.iloc[0]["User_ID"])
                }
            )
        return True, "Password changed successfully."
    except Exception as e:
        return False, f"Could not change password: {e}"
    finally:
        engine.dispose()


def account_settings():
    st.header("⚙️ Account Settings")
    st.caption("Manage your NEXORA BANK login account.")

    current_username = str(st.session_state.get("username", ""))
    role = str(st.session_state.get("role", "User"))
    customer_id = st.session_state.get("customer_id")

    st.info(
        f"Logged in as **{current_username}**  |  "
        f"Role: **{role}**"
    )

    # Profile information
    st.subheader("👤 Profile")
    profile_name = None

    if str(role).lower() == "user" and customer_id:
        profile = run_query(
            """
            SELECT Customer_ID, Name, Branch_ID
            FROM customers
            WHERE Customer_ID = :customer_id
            LIMIT 1
            """,
            {"customer_id": customer_id}
        )

        if not profile.empty:
            profile_name = str(profile.iloc[0]["Name"])
            cols = st.columns(3)
            cols[0].metric("Customer Name", profile_name)
            cols[1].metric("Customer ID", str(profile.iloc[0]["Customer_ID"]))
            cols[2].metric("Branch", str(profile.iloc[0]["Branch_ID"]))

    st.markdown("---")

    # Username change
    st.subheader("✏️ Change Username")

    with st.form("change_username_form"):
        new_username = st.text_input(
            "New Username",
            value=current_username,
            placeholder="Enter your new username"
        )
        username_button = st.form_submit_button(
            "💾 Update Username",
            use_container_width=True
        )

    if username_button:
        success, message = update_username(new_username)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    st.markdown("---")

    # Password change
    st.subheader("🔐 Change Password")

    with st.form("change_password_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter your new password"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password"
        )

        password_button = st.form_submit_button(
            "🔑 Change Password",
            use_container_width=True
        )

    if password_button:
        success, message = update_password(
            current_password,
            new_password,
            confirm_password
        )

        if success:
            st.success(message)
            st.info("Your new password will be used the next time you log in.")
        else:
            st.error(message)

    st.markdown("---")
    st.caption(
        "For this version, password storage follows your existing NEXORA BANK "
        "users table structure. Password hashing can be added as a separate security upgrade."
    )


def admin_app():
    st.sidebar.title("🏦 NEXORA BANK")
    st.sidebar.success(f"Admin: {st.session_state.username}")
    page = st.sidebar.radio("Navigation", [
        "🏠 Dashboard","👥 Customers","🏢 Branch Analysis","💳 Transactions",
        "🏦 Loans","⚠️ Risk Analysis","🎯 Product Recommendations","📥 Reports",
        "⚙️ Account Settings"
    ])
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    pages = {
        "🏠 Dashboard": admin_dashboard,
        "👥 Customers": customer_analysis,
        "🏢 Branch Analysis": branch_analysis,
        "💳 Transactions": transaction_analysis,
        "🏦 Loans": loan_analysis,
        "⚠️ Risk Analysis": risk_analysis,
        "🎯 Product Recommendations": product_recommendations,
        "📥 Reports": reports,
        "⚙️ Account Settings": account_settings
    }
    pages[page]()

def user_app():
    st.sidebar.title("🏦 NEXORA BANK")
    st.sidebar.success(f"User: {st.session_state.username}")

    page = st.sidebar.radio(
        "Navigation",
        [
            "👤 My Dashboard",
            "⚙️ Account Settings"
        ]
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    if page == "👤 My Dashboard":
        user_dashboard()
    elif page == "⚙️ Account Settings":
        account_settings()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_type" not in st.session_state:
    st.session_state.login_type = None

if not st.session_state.logged_in:
    login()
elif str(st.session_state.role).lower() == "admin":
    admin_app()
else:
    user_app()
