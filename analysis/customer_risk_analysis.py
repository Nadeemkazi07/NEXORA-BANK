from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - CUSTOMER RISK ANALYSIS
# ============================================================

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

customers = pd.read_csv(DATA_DIR / "customers.csv")
loans = pd.read_csv(DATA_DIR / "loans.csv")
transactions = pd.read_csv(DATA_DIR / "transactions.csv")


print("\n" + "=" * 60)
print("NEXORA BANK - CUSTOMER RISK ANALYSIS")
print("=" * 60)


# ------------------------------------------------------------
# 2. LOAN INFORMATION BY CUSTOMER
# ------------------------------------------------------------

loan_summary = (
    loans
    .groupby("Customer_ID")
    .agg(
        Loan_Count=("Loan_ID", "count"),
        Total_Loan_Amount=("Loan_Amount", "sum"),
        Default_Count=("Default_Flag", "sum"),
        Average_Interest_Rate=("Interest_Rate", "mean")
    )
    .reset_index()
)


# ------------------------------------------------------------
# 3. TRANSACTION INFORMATION BY CUSTOMER
# ------------------------------------------------------------

transaction_summary = (
    transactions
    .groupby("Customer_ID")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Transaction_Value=("Amount", "sum"),
        Average_Transaction_Value=("Amount", "mean")
    )
    .reset_index()
)


# ------------------------------------------------------------
# 4. MERGE CUSTOMER DATA
# ------------------------------------------------------------

risk_data = customers.merge(
    loan_summary,
    on="Customer_ID",
    how="left"
)

risk_data = risk_data.merge(
    transaction_summary,
    on="Customer_ID",
    how="left"
)


# ------------------------------------------------------------
# 5. FILL CUSTOMERS WITHOUT LOANS / TRANSACTIONS
# ------------------------------------------------------------

risk_columns = [
    "Loan_Count",
    "Total_Loan_Amount",
    "Default_Count",
    "Average_Interest_Rate",
    "Transaction_Count",
    "Total_Transaction_Value",
    "Average_Transaction_Value"
]

risk_data[risk_columns] = (
    risk_data[risk_columns]
    .fillna(0)
)


# ------------------------------------------------------------
# 6. RISK SCORE CALCULATION
# ------------------------------------------------------------

risk_data["Risk_Score"] = 0


# Credit score risk
risk_data.loc[
    risk_data["Credit_Score"] < 580,
    "Risk_Score"
] += 40

risk_data.loc[
    (risk_data["Credit_Score"] >= 580)
    & (risk_data["Credit_Score"] < 670),
    "Risk_Score"
] += 25

risk_data.loc[
    (risk_data["Credit_Score"] >= 670)
    & (risk_data["Credit_Score"] < 740),
    "Risk_Score"
] += 10


# Default risk
risk_data.loc[
    risk_data["Default_Count"] >= 2,
    "Risk_Score"
] += 30

risk_data.loc[
    risk_data["Default_Count"] == 1,
    "Risk_Score"
] += 20


# Loan exposure risk
risk_data.loc[
    risk_data["Total_Loan_Amount"] >= 5000000,
    "Risk_Score"
] += 15

risk_data.loc[
    (risk_data["Total_Loan_Amount"] >= 2000000)
    & (risk_data["Total_Loan_Amount"] < 5000000),
    "Risk_Score"
] += 10


# Income vs loan exposure
loan_to_income = (
    risk_data["Total_Loan_Amount"]
    / (risk_data["Monthly_Income"] * 12)
)

risk_data["Loan_to_Annual_Income"] = loan_to_income


risk_data.loc[
    risk_data["Loan_to_Annual_Income"] >= 10,
    "Risk_Score"
] += 15

risk_data.loc[
    (risk_data["Loan_to_Annual_Income"] >= 5)
    & (risk_data["Loan_to_Annual_Income"] < 10),
    "Risk_Score"
] += 10


# ------------------------------------------------------------
# 7. RISK CATEGORY
# ------------------------------------------------------------

risk_data["Risk_Category"] = pd.cut(
    risk_data["Risk_Score"],
    bins=[-1, 29, 59, 1000],
    labels=[
        "Low Risk",
        "Medium Risk",
        "High Risk"
    ]
)


# ------------------------------------------------------------
# 8. RISK REASON
# ------------------------------------------------------------

def get_risk_reason(row):

    reasons = []

    if row["Credit_Score"] < 580:
        reasons.append("Poor credit score")

    elif row["Credit_Score"] < 670:
        reasons.append("Fair credit score")

    if row["Default_Count"] >= 2:
        reasons.append("Multiple loan defaults")

    elif row["Default_Count"] == 1:
        reasons.append("Previous loan default")

    if row["Total_Loan_Amount"] >= 5000000:
        reasons.append("High loan exposure")

    elif row["Total_Loan_Amount"] >= 2000000:
        reasons.append("Moderate loan exposure")

    if row["Loan_to_Annual_Income"] >= 10:
        reasons.append("High loan-to-income ratio")

    elif row["Loan_to_Annual_Income"] >= 5:
        reasons.append("Elevated loan-to-income ratio")

    if not reasons:
        return "No major risk indicators"

    return "; ".join(reasons)


risk_data["Risk_Reason"] = risk_data.apply(
    get_risk_reason,
    axis=1
)


# ------------------------------------------------------------
# 9. CUSTOMER RISK REPORT
# ------------------------------------------------------------

risk_report = risk_data[
    [
        "Customer_ID",
        "Name",
        "Branch_ID",
        "Credit_Score",
        "Monthly_Income",
        "Account_Balance",
        "Loan_Count",
        "Total_Loan_Amount",
        "Default_Count",
        "Transaction_Count",
        "Total_Transaction_Value",
        "Loan_to_Annual_Income",
        "Risk_Score",
        "Risk_Category",
        "Risk_Reason"
    ]
].copy()


risk_report = risk_report.sort_values(
    "Risk_Score",
    ascending=False
)


# ------------------------------------------------------------
# 10. DISPLAY TOP HIGH-RISK CUSTOMERS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("TOP 20 HIGH-RISK CUSTOMERS")
print("=" * 60)

print(
    risk_report
    .head(20)
    .round(2)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 11. RISK CATEGORY SUMMARY
# ------------------------------------------------------------

risk_summary = (
    risk_report
    .groupby("Risk_Category", observed=True)
    .agg(
        Customer_Count=("Customer_ID", "count"),
        Average_Credit_Score=("Credit_Score", "mean"),
        Average_Balance=("Account_Balance", "mean"),
        Average_Loan_Amount=("Total_Loan_Amount", "mean"),
        Average_Risk_Score=("Risk_Score", "mean")
    )
    .reset_index()
)

risk_summary["Percentage"] = (
    risk_summary["Customer_Count"]
    / len(risk_report)
    * 100
).round(2)


print("\n" + "=" * 60)
print("RISK CATEGORY SUMMARY")
print("=" * 60)

print(
    risk_summary
    .round(2)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 12. BRANCH-WISE RISK ANALYSIS
# ------------------------------------------------------------

branch_risk = (
    risk_report
    .groupby("Branch_ID")
    .agg(
        Customer_Count=("Customer_ID", "count"),
        Average_Risk_Score=("Risk_Score", "mean"),
        High_Risk_Customers=(
            "Risk_Category",
            lambda x: (x == "High Risk").sum()
        ),
        Medium_Risk_Customers=(
            "Risk_Category",
            lambda x: (x == "Medium Risk").sum()
        ),
        Low_Risk_Customers=(
            "Risk_Category",
            lambda x: (x == "Low Risk").sum()
        ),
        Average_Credit_Score=("Credit_Score", "mean"),
        Total_Loan_Exposure=("Total_Loan_Amount", "sum")
    )
    .reset_index()
)

branch_risk["High_Risk_Percentage"] = (
    branch_risk["High_Risk_Customers"]
    / branch_risk["Customer_Count"]
    * 100
).round(2)


print("\n" + "=" * 60)
print("BRANCH-WISE CUSTOMER RISK")
print("=" * 60)

print(
    branch_risk
    .round(2)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 13. SAVE REPORTS
# ------------------------------------------------------------

risk_report.to_csv(
    REPORT_DIR / "customer_risk_analysis.csv",
    index=False
)

risk_summary.to_csv(
    REPORT_DIR / "risk_category_summary.csv",
    index=False
)

branch_risk.to_csv(
    REPORT_DIR / "branch_customer_risk.csv",
    index=False
)


# ------------------------------------------------------------
# 14. RISK CATEGORY CHART
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.bar(
    risk_summary["Risk_Category"].astype(str),
    risk_summary["Customer_Count"]
)

plt.title("Customer Risk Category Distribution")
plt.xlabel("Risk Category")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "customer_risk_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 15. BRANCH HIGH-RISK CUSTOMER CHART
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    branch_risk["Branch_ID"],
    branch_risk["High_Risk_Percentage"]
)

plt.title("High-Risk Customer Percentage by Branch")
plt.xlabel("Branch")
plt.ylabel("High-Risk Customers (%)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_high_risk_percentage.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CUSTOMER RISK ANALYSIS COMPLETED")
print("=" * 60)

print("\nCSV reports saved inside:")
print("reports/")

print("\nCharts saved inside:")
print("reports/")

print("\nCustomer risk analysis completed successfully.")