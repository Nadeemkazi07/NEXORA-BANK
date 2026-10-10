from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - LOAN & RISK ANALYSIS
# ============================================================

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

loans = pd.read_csv(DATA_DIR / "loans.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")

loans["Loan_Start_Date"] = pd.to_datetime(
    loans["Loan_Start_Date"]
)

customers["Registration_Date"] = pd.to_datetime(
    customers["Registration_Date"]
)


print("\n" + "=" * 60)
print("NEXORA BANK - LOAN & RISK ANALYSIS")
print("=" * 60)


# ------------------------------------------------------------
# 2. LOAN PORTFOLIO KPIs
# ------------------------------------------------------------

total_loans = len(loans)

total_loan_value = loans["Loan_Amount"].sum()

average_loan = loans["Loan_Amount"].mean()

median_loan = loans["Loan_Amount"].median()

average_interest = loans["Interest_Rate"].mean()

average_tenure = loans["Tenure_Months"].mean()

average_emi = loans["EMI"].mean()

defaulted_loans = loans["Default_Flag"].sum()

default_rate = (
    defaulted_loans / total_loans * 100
)


print("\n" + "=" * 60)
print("LOAN PORTFOLIO KPIs")
print("=" * 60)

print(f"Total Loans              : {total_loans:,}")
print(f"Total Loan Value         : ₹{total_loan_value:,.2f}")
print(f"Average Loan Amount      : ₹{average_loan:,.2f}")
print(f"Median Loan Amount       : ₹{median_loan:,.2f}")
print(f"Average Interest Rate    : {average_interest:.2f}%")
print(f"Average Tenure           : {average_tenure:.2f} months")
print(f"Average EMI              : ₹{average_emi:,.2f}")
print(f"Defaulted Loans          : {defaulted_loans:,}")
print(f"Overall Default Rate     : {default_rate:.2f}%")


# ------------------------------------------------------------
# 3. LOAN TYPE ANALYSIS
# ------------------------------------------------------------

loan_type_analysis = (
    loans
    .groupby("Loan_Type")
    .agg(
        Loan_Count=("Loan_ID", "count"),
        Total_Loan_Amount=("Loan_Amount", "sum"),
        Average_Loan_Amount=("Loan_Amount", "mean"),
        Average_Interest_Rate=("Interest_Rate", "mean"),
        Average_Tenure=("Tenure_Months", "mean"),
        Average_EMI=("EMI", "mean")
    )
    .reset_index()
)

loan_type_analysis["Portfolio_Share"] = (
    loan_type_analysis["Total_Loan_Amount"]
    / total_loan_value
    * 100
).round(2)

loan_type_analysis = loan_type_analysis.sort_values(
    "Total_Loan_Amount",
    ascending=False
)


print("\n" + "=" * 60)
print("LOAN TYPE ANALYSIS")
print("=" * 60)

print(
    loan_type_analysis
    .round(2)
    .to_string(index=False)
)

loan_type_analysis.to_csv(
    REPORT_DIR / "loan_type_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 4. LOAN STATUS ANALYSIS
# ------------------------------------------------------------

loan_status_analysis = (
    loans["Loan_Status"]
    .value_counts()
    .reset_index()
)

loan_status_analysis.columns = [
    "Loan_Status",
    "Loan_Count"
]

loan_status_analysis["Percentage"] = (
    loan_status_analysis["Loan_Count"]
    / total_loans
    * 100
).round(2)


print("\n" + "=" * 60)
print("LOAN STATUS ANALYSIS")
print("=" * 60)

print(
    loan_status_analysis
    .to_string(index=False)
)

loan_status_analysis.to_csv(
    REPORT_DIR / "loan_status_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 5. DEFAULT ANALYSIS
# ------------------------------------------------------------

default_analysis = (
    loans
    .groupby("Default_Flag")
    .agg(
        Loan_Count=("Loan_ID", "count"),
        Total_Loan_Amount=("Loan_Amount", "sum")
    )
    .reset_index()
)

default_analysis["Percentage"] = (
    default_analysis["Loan_Count"]
    / total_loans
    * 100
).round(2)

print("\n" + "=" * 60)
print("DEFAULT ANALYSIS")
print("=" * 60)

print(
    default_analysis
    .round(2)
    .to_string(index=False)
)

default_analysis.to_csv(
    REPORT_DIR / "default_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 6. DEFAULT RATE BY LOAN TYPE
# ------------------------------------------------------------

loan_default_analysis = (
    loans
    .groupby("Loan_Type")
    .agg(
        Total_Loans=("Loan_ID", "count"),
        Defaulted_Loans=("Default_Flag", "sum"),
        Total_Loan_Amount=("Loan_Amount", "sum")
    )
    .reset_index()
)

loan_default_analysis["Default_Rate"] = (
    loan_default_analysis["Defaulted_Loans"]
    / loan_default_analysis["Total_Loans"]
    * 100
).round(2)

loan_default_analysis = loan_default_analysis.sort_values(
    "Default_Rate",
    ascending=False
)


print("\n" + "=" * 60)
print("DEFAULT RATE BY LOAN TYPE")
print("=" * 60)

print(
    loan_default_analysis
    .round(2)
    .to_string(index=False)
)

loan_default_analysis.to_csv(
    REPORT_DIR / "default_rate_by_loan_type.csv",
    index=False
)


# ------------------------------------------------------------
# 7. CREDIT SCORE GROUP
# ------------------------------------------------------------

customers["Credit_Score_Group"] = pd.cut(
    customers["Credit_Score"],
    bins=[0, 579, 669, 739, 850],
    labels=[
        "Poor",
        "Fair",
        "Good",
        "Excellent"
    ]
)

loan_customer_data = loans.merge(
    customers[
        [
            "Customer_ID",
            "Credit_Score",
            "Credit_Score_Group"
        ]
    ],
    on="Customer_ID",
    how="left"
)


# ------------------------------------------------------------
# 8. DEFAULT RATE BY CREDIT SCORE
# ------------------------------------------------------------

credit_default_analysis = (
    loan_customer_data
    .groupby("Credit_Score_Group", observed=True)
    .agg(
        Total_Loans=("Loan_ID", "count"),
        Defaulted_Loans=("Default_Flag", "sum"),
        Average_Loan_Amount=("Loan_Amount", "mean")
    )
    .reset_index()
)

credit_default_analysis["Default_Rate"] = (
    credit_default_analysis["Defaulted_Loans"]
    / credit_default_analysis["Total_Loans"]
    * 100
).round(2)


print("\n" + "=" * 60)
print("DEFAULT RATE BY CREDIT SCORE GROUP")
print("=" * 60)

print(
    credit_default_analysis
    .round(2)
    .to_string(index=False)
)

credit_default_analysis.to_csv(
    REPORT_DIR / "default_rate_by_credit_score.csv",
    index=False
)


# ------------------------------------------------------------
# 9. BRANCH-WISE LOAN ANALYSIS
# ------------------------------------------------------------

branch_loan_analysis = (
    loans
    .groupby("Branch_ID")
    .agg(
        Loan_Count=("Loan_ID", "count"),
        Total_Loan_Amount=("Loan_Amount", "sum"),
        Average_Loan_Amount=("Loan_Amount", "mean"),
        Defaulted_Loans=("Default_Flag", "sum")
    )
    .reset_index()
)

branch_loan_analysis["Default_Rate"] = (
    branch_loan_analysis["Defaulted_Loans"]
    / branch_loan_analysis["Loan_Count"]
    * 100
).round(2)

branch_loan_analysis = branch_loan_analysis.sort_values(
    "Total_Loan_Amount",
    ascending=False
)


print("\n" + "=" * 60)
print("BRANCH-WISE LOAN ANALYSIS")
print("=" * 60)

print(
    branch_loan_analysis
    .round(2)
    .to_string(index=False)
)

branch_loan_analysis.to_csv(
    REPORT_DIR / "branch_loan_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 10. LOAN AMOUNT DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.hist(
    loans["Loan_Amount"],
    bins=30
)

plt.title("Loan Amount Distribution")
plt.xlabel("Loan Amount (₹)")
plt.ylabel("Number of Loans")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "loan_amount_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 11. LOAN TYPE PORTFOLIO
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    loan_type_analysis["Loan_Type"],
    loan_type_analysis["Total_Loan_Amount"]
)

plt.title("Loan Portfolio by Loan Type")
plt.xlabel("Loan Type")
plt.ylabel("Total Loan Amount (₹)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "loan_portfolio_by_type.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 12. DEFAULT RATE BY LOAN TYPE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    loan_default_analysis["Loan_Type"],
    loan_default_analysis["Default_Rate"]
)

plt.title("Default Rate by Loan Type")
plt.xlabel("Loan Type")
plt.ylabel("Default Rate (%)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "default_rate_by_loan_type.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 13. DEFAULT RATE BY CREDIT SCORE
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.bar(
    credit_default_analysis["Credit_Score_Group"].astype(str),
    credit_default_analysis["Default_Rate"]
)

plt.title("Default Rate by Credit Score Group")
plt.xlabel("Credit Score Group")
plt.ylabel("Default Rate (%)")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "default_rate_by_credit_score.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 14. BRANCH LOAN PORTFOLIO
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    branch_loan_analysis["Branch_ID"],
    branch_loan_analysis["Total_Loan_Amount"]
)

plt.title("Loan Portfolio by Branch")
plt.xlabel("Branch")
plt.ylabel("Total Loan Amount (₹)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "loan_portfolio_by_branch.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("LOAN & RISK ANALYSIS COMPLETED")
print("=" * 60)

print("\nCSV reports saved inside:")
print("reports/")

print("\nCharts saved inside:")
print("reports/")

print("\nLoan and risk analysis completed successfully.")