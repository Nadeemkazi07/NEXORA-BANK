from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - ACCOUNT & FINANCIAL ANALYSIS
# ============================================================

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

accounts = pd.read_csv(DATA_DIR / "accounts.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")


print("\n" + "=" * 65)
print("NEXORA BANK - ACCOUNT & FINANCIAL ANALYSIS")
print("=" * 65)


# ============================================================
# 2. ACCOUNT KPIs
# ============================================================

total_accounts = accounts["Account_ID"].nunique()

total_opening_balance = accounts["Opening_Balance"].sum()

total_current_balance = accounts["Current_Balance"].sum()

average_opening_balance = accounts["Opening_Balance"].mean()

average_current_balance = accounts["Current_Balance"].mean()

balance_change = (
    total_current_balance - total_opening_balance
)

balance_growth_percentage = (
    balance_change / total_opening_balance
) * 100


print("\n" + "=" * 65)
print("ACCOUNT KPIs")
print("=" * 65)

print(f"Total Accounts          : {total_accounts:,}")
print(
    f"Total Opening Balance  : ₹{total_opening_balance:,.2f}"
)
print(
    f"Total Current Balance  : ₹{total_current_balance:,.2f}"
)
print(
    f"Average Opening Balance: ₹{average_opening_balance:,.2f}"
)
print(
    f"Average Current Balance: ₹{average_current_balance:,.2f}"
)
print(
    f"Balance Change         : ₹{balance_change:,.2f}"
)
print(
    f"Balance Growth         : {balance_growth_percentage:.2f}%"
)


# ============================================================
# 3. ACCOUNT STATUS ANALYSIS
# ============================================================

status_analysis = (
    accounts
    .groupby("Account_Status")
    .agg(
        Account_Count=("Account_ID", "count"),
        Total_Current_Balance=("Current_Balance", "sum"),
        Average_Current_Balance=("Current_Balance", "mean")
    )
    .reset_index()
)

status_analysis["Percentage"] = (
    status_analysis["Account_Count"]
    / total_accounts
    * 100
).round(2)


print("\n" + "=" * 65)
print("ACCOUNT STATUS ANALYSIS")
print("=" * 65)

print(
    status_analysis
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 4. ACCOUNT TYPE ANALYSIS
# ============================================================

account_type_analysis = (
    accounts
    .groupby("Account_Type")
    .agg(
        Account_Count=("Account_ID", "count"),
        Total_Current_Balance=("Current_Balance", "sum"),
        Average_Current_Balance=("Current_Balance", "mean"),
        Average_Opening_Balance=("Opening_Balance", "mean")
    )
    .reset_index()
)

account_type_analysis["Percentage"] = (
    account_type_analysis["Account_Count"]
    / total_accounts
    * 100
).round(2)


print("\n" + "=" * 65)
print("ACCOUNT TYPE ANALYSIS")
print("=" * 65)

print(
    account_type_analysis
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 5. BALANCE GROWTH ANALYSIS
# ============================================================

accounts["Balance_Change"] = (
    accounts["Current_Balance"]
    - accounts["Opening_Balance"]
)

accounts["Balance_Growth_Percentage"] = (
    accounts["Balance_Change"]
    / accounts["Opening_Balance"]
    * 100
)


balance_growth_summary = pd.DataFrame({
    "Metric": [
        "Total Opening Balance",
        "Total Current Balance",
        "Total Balance Change",
        "Average Balance Change",
        "Median Balance Change"
    ],
    "Value": [
        accounts["Opening_Balance"].sum(),
        accounts["Current_Balance"].sum(),
        accounts["Balance_Change"].sum(),
        accounts["Balance_Change"].mean(),
        accounts["Balance_Change"].median()
    ]
})


print("\n" + "=" * 65)
print("BALANCE GROWTH ANALYSIS")
print("=" * 65)

print(
    balance_growth_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 6. BRANCH-WISE ACCOUNT ANALYSIS
# ============================================================

branch_account_analysis = (
    accounts
    .groupby("Branch_ID")
    .agg(
        Account_Count=("Account_ID", "count"),
        Total_Opening_Balance=("Opening_Balance", "sum"),
        Total_Current_Balance=("Current_Balance", "sum"),
        Average_Current_Balance=("Current_Balance", "mean")
    )
    .reset_index()
)

branch_account_analysis["Balance_Change"] = (
    branch_account_analysis["Total_Current_Balance"]
    - branch_account_analysis["Total_Opening_Balance"]
)

branch_account_analysis["Balance_Growth_Percentage"] = (
    branch_account_analysis["Balance_Change"]
    / branch_account_analysis["Total_Opening_Balance"]
    * 100
)


print("\n" + "=" * 65)
print("BRANCH-WISE ACCOUNT ANALYSIS")
print("=" * 65)

print(
    branch_account_analysis
    .round(2)
    .sort_values(
        "Total_Current_Balance",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# 7. ACCOUNT STATUS BY BRANCH
# ============================================================

branch_status = (
    accounts
    .groupby(
        [
            "Branch_ID",
            "Account_Status"
        ]
    )
    .size()
    .reset_index(
        name="Account_Count"
    )
)


print("\n" + "=" * 65)
print("ACCOUNT STATUS BY BRANCH")
print("=" * 65)

print(
    branch_status
    .sort_values(
        ["Branch_ID", "Account_Count"],
        ascending=[True, False]
    )
    .to_string(index=False)
)


# ============================================================
# 8. CUSTOMER FINANCIAL PROFILE
# ============================================================

customer_financial = (
    customers
    .groupby("Customer_Segment")
    .agg(
        Customer_Count=("Customer_ID", "nunique"),
        Average_Income=("Monthly_Income", "mean"),
        Average_Account_Balance=("Account_Balance", "mean"),
        Average_Credit_Score=("Credit_Score", "mean")
    )
    .reset_index()
)


customer_financial["Percentage"] = (
    customer_financial["Customer_Count"]
    / customer_financial["Customer_Count"].sum()
    * 100
).round(2)


print("\n" + "=" * 65)
print("CUSTOMER FINANCIAL PROFILE")
print("=" * 65)

print(
    customer_financial
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 9. INCOME VS ACCOUNT BALANCE
# ============================================================

income_balance = customers[
    [
        "Customer_ID",
        "Monthly_Income",
        "Account_Balance",
        "Credit_Score",
        "Customer_Segment",
        "Branch_ID"
    ]
].copy()

income_balance["Annual_Income"] = (
    income_balance["Monthly_Income"] * 12
)

income_balance["Balance_to_Annual_Income"] = (
    income_balance["Account_Balance"]
    / income_balance["Annual_Income"]
)


print("\n" + "=" * 65)
print("INCOME VS ACCOUNT BALANCE")
print("=" * 65)

print(
    income_balance[
        [
            "Monthly_Income",
            "Account_Balance",
            "Credit_Score",
            "Balance_to_Annual_Income"
        ]
    ]
    .describe()
    .round(2)
    .to_string()
)


# ============================================================
# 10. TOP 20 ACCOUNTS BY CURRENT BALANCE
# ============================================================

top_accounts = (
    accounts[
        [
            "Account_ID",
            "Customer_ID",
            "Branch_ID",
            "Account_Type",
            "Current_Balance",
            "Account_Status"
        ]
    ]
    .sort_values(
        "Current_Balance",
        ascending=False
    )
    .head(20)
)


print("\n" + "=" * 65)
print("TOP 20 ACCOUNTS BY CURRENT BALANCE")
print("=" * 65)

print(
    top_accounts
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 11. SAVE REPORTS
# ============================================================

status_analysis.to_csv(
    REPORT_DIR / "account_status_analysis.csv",
    index=False
)

account_type_analysis.to_csv(
    REPORT_DIR / "account_type_analysis.csv",
    index=False
)

balance_growth_summary.to_csv(
    REPORT_DIR / "balance_growth_summary.csv",
    index=False
)

branch_account_analysis.to_csv(
    REPORT_DIR / "branch_account_analysis.csv",
    index=False
)

branch_status.to_csv(
    REPORT_DIR / "branch_account_status.csv",
    index=False
)

customer_financial.to_csv(
    REPORT_DIR / "customer_financial_profile.csv",
    index=False
)

income_balance.to_csv(
    REPORT_DIR / "income_balance_analysis.csv",
    index=False
)

top_accounts.to_csv(
    REPORT_DIR / "top_20_accounts.csv",
    index=False
)


# ============================================================
# 12. ACCOUNT TYPE CHART
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    account_type_analysis["Account_Type"],
    account_type_analysis["Account_Count"]
)

plt.title("Account Distribution by Account Type")
plt.xlabel("Account Type")
plt.ylabel("Number of Accounts")

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "account_type_distribution.png",
    dpi=300
)

plt.close()


# ============================================================
# 13. ACCOUNT STATUS CHART
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    status_analysis["Account_Status"],
    status_analysis["Account_Count"]
)

plt.title("Account Status Distribution")
plt.xlabel("Account Status")
plt.ylabel("Number of Accounts")

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "account_status_distribution.png",
    dpi=300
)

plt.close()


# ============================================================
# 14. BRANCH BALANCE CHART
# ============================================================

branch_chart = branch_account_analysis.sort_values(
    "Total_Current_Balance",
    ascending=False
)

plt.figure(figsize=(10, 6))

plt.bar(
    branch_chart["Branch_ID"],
    branch_chart["Total_Current_Balance"]
)

plt.title("Current Account Balance by Branch")
plt.xlabel("Branch")
plt.ylabel("Total Current Balance")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_current_balance.png",
    dpi=300
)

plt.close()


# ============================================================
# 15. BALANCE GROWTH CHART
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    branch_chart["Branch_ID"],
    branch_chart["Balance_Growth_Percentage"]
)

plt.title("Account Balance Growth by Branch")
plt.xlabel("Branch")
plt.ylabel("Balance Growth (%)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_balance_growth.png",
    dpi=300
)

plt.close()


# ============================================================
# 16. INCOME VS BALANCE SCATTER PLOT
# ============================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    customers["Monthly_Income"],
    customers["Account_Balance"]
)

plt.title("Monthly Income vs Account Balance")
plt.xlabel("Monthly Income")
plt.ylabel("Account Balance")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "income_vs_account_balance.png",
    dpi=300
)

plt.close()


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 65)
print("ACCOUNT & FINANCIAL ANALYSIS COMPLETED")
print("=" * 65)

print("\nCSV reports saved inside:")
print("reports/")

print("\nCharts saved inside:")
print("reports/")

print("\nAccount analysis completed successfully.")