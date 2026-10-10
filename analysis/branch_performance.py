from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - BRANCH PERFORMANCE ANALYSIS
# ============================================================

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

customers = pd.read_csv(DATA_DIR / "customers.csv")
accounts = pd.read_csv(DATA_DIR / "accounts.csv")
transactions = pd.read_csv(DATA_DIR / "transactions.csv")
loans = pd.read_csv(DATA_DIR / "loans.csv")


print("\n" + "=" * 65)
print("NEXORA BANK - BRANCH PERFORMANCE ANALYSIS")
print("=" * 65)


# ============================================================
# 2. CUSTOMER ANALYSIS BY BRANCH
# ============================================================

customer_branch = (
    customers
    .groupby("Branch_ID")
    .agg(
        Customer_Count=("Customer_ID", "nunique"),
        Average_Income=("Monthly_Income", "mean"),
        Average_Balance=("Account_Balance", "mean"),
        Average_Credit_Score=("Credit_Score", "mean")
    )
    .reset_index()
)


# ============================================================
# 3. ACCOUNT ANALYSIS BY BRANCH
# ============================================================

account_branch = (
    accounts
    .groupby("Branch_ID")
    .agg(
        Account_Count=("Account_ID", "nunique"),
        Total_Current_Balance=("Current_Balance", "sum"),
        Average_Current_Balance=("Current_Balance", "mean")
    )
    .reset_index()
)


# ============================================================
# 4. TRANSACTION ANALYSIS BY BRANCH
# ============================================================

transaction_branch = (
    transactions
    .groupby("Branch_ID")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Transaction_Value=("Amount", "sum"),
        Average_Transaction_Value=("Amount", "mean"),
        Unique_Transaction_Customers=("Customer_ID", "nunique")
    )
    .reset_index()
)


# ============================================================
# 5. LOAN ANALYSIS BY BRANCH
# ============================================================

loan_branch = (
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


loan_branch["Default_Rate"] = (
    loan_branch["Defaulted_Loans"]
    / loan_branch["Loan_Count"]
    * 100
)


# ============================================================
# 6. COMBINE BRANCH ANALYSIS
# ============================================================

branch_performance = customer_branch.merge(
    account_branch,
    on="Branch_ID",
    how="outer"
)

branch_performance = branch_performance.merge(
    transaction_branch,
    on="Branch_ID",
    how="outer"
)

branch_performance = branch_performance.merge(
    loan_branch,
    on="Branch_ID",
    how="outer"
)


# ============================================================
# 7. CALCULATE ADDITIONAL KPIs
# ============================================================

branch_performance["Transaction_Value_Per_Customer"] = (
    branch_performance["Total_Transaction_Value"]
    / branch_performance["Customer_Count"]
)


branch_performance["Loan_Amount_Per_Customer"] = (
    branch_performance["Total_Loan_Amount"]
    / branch_performance["Customer_Count"]
)


branch_performance["Transactions_Per_Customer"] = (
    branch_performance["Transaction_Count"]
    / branch_performance["Customer_Count"]
)


# ============================================================
# 8. BRANCH PERFORMANCE SCORE
# ============================================================
#
# This is an analytical score for academic/business analysis.
# It is NOT a real bank credit or regulatory score.
#
# Higher transaction activity, customer base and balances
# contribute positively.
#
# High default rates reduce the score.
# ============================================================

branch_performance["Performance_Score"] = (
    (
        branch_performance["Customer_Count"]
        / branch_performance["Customer_Count"].max()
    ) * 30
    +
    (
        branch_performance["Total_Transaction_Value"]
        / branch_performance["Total_Transaction_Value"].max()
    ) * 30
    +
    (
        branch_performance["Total_Current_Balance"]
        / branch_performance["Total_Current_Balance"].max()
    ) * 20
    +
    (
        branch_performance["Loan_Count"]
        / branch_performance["Loan_Count"].max()
    ) * 20
    -
    (
        branch_performance["Default_Rate"]
        / branch_performance["Default_Rate"].max()
    ) * 10
)


branch_performance["Performance_Score"] = (
    branch_performance["Performance_Score"]
    .round(2)
)


# ============================================================
# 9. DISPLAY BRANCH PERFORMANCE
# ============================================================

print("\n" + "=" * 65)
print("BRANCH PERFORMANCE SUMMARY")
print("=" * 65)

display_columns = [
    "Branch_ID",
    "Customer_Count",
    "Account_Count",
    "Total_Current_Balance",
    "Transaction_Count",
    "Total_Transaction_Value",
    "Loan_Count",
    "Total_Loan_Amount",
    "Defaulted_Loans",
    "Default_Rate",
    "Average_Credit_Score",
    "Performance_Score"
]

print(
    branch_performance[
        display_columns
    ]
    .round(2)
    .sort_values(
        "Performance_Score",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# 10. HEAD OFFICE ANALYSIS
# ============================================================

head_office = branch_performance[
    branch_performance["Branch_ID"] == "HO001"
]


print("\n" + "=" * 65)
print("HEAD OFFICE - BENGALURU")
print("=" * 65)

if not head_office.empty:

    print(
        head_office[
            display_columns
        ]
        .round(2)
        .to_string(index=False)
    )


# ============================================================
# 11. HUBBALLI ANALYSIS
# ============================================================

hubballi = branch_performance[
    branch_performance["Branch_ID"] == "BR002"
]


print("\n" + "=" * 65)
print("HUBBALLI BRANCH")
print("=" * 65)

if not hubballi.empty:

    print(
        hubballi[
            display_columns
        ]
        .round(2)
        .to_string(index=False)
    )


# ============================================================
# 12. DHARWAD ANALYSIS
# ============================================================

dharwad = branch_performance[
    branch_performance["Branch_ID"] == "BR003"
]


print("\n" + "=" * 65)
print("DHARWAD BRANCH")
print("=" * 65)

if not dharwad.empty:

    print(
        dharwad[
            display_columns
        ]
        .round(2)
        .to_string(index=False)
    )


# ============================================================
# 13. TOP BRANCHES BY TRANSACTION VALUE
# ============================================================

print("\n" + "=" * 65)
print("BRANCHES BY TRANSACTION VALUE")
print("=" * 65)

transaction_ranking = (
    branch_performance[
        [
            "Branch_ID",
            "Transaction_Count",
            "Total_Transaction_Value",
            "Average_Transaction_Value"
        ]
    ]
    .sort_values(
        "Total_Transaction_Value",
        ascending=False
    )
)

print(
    transaction_ranking
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 14. BRANCH DEFAULT ANALYSIS
# ============================================================

print("\n" + "=" * 65)
print("BRANCH DEFAULT ANALYSIS")
print("=" * 65)

default_ranking = (
    branch_performance[
        [
            "Branch_ID",
            "Loan_Count",
            "Defaulted_Loans",
            "Default_Rate"
        ]
    ]
    .sort_values(
        "Default_Rate",
        ascending=False
)
)
print(
    default_ranking
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 15. SAVE MAIN REPORT
# ============================================================

branch_performance.to_csv(
    REPORT_DIR / "branch_performance_analysis.csv",
    index=False
)


# ============================================================
# 16. SAVE TRANSACTION REPORT
# ============================================================

transaction_ranking.to_csv(
    REPORT_DIR / "branch_transaction_performance.csv",
    index=False
)


# ============================================================
# 17. SAVE DEFAULT REPORT
# ============================================================

default_ranking.to_csv(
    REPORT_DIR / "branch_default_analysis.csv",
    index=False
)


# ============================================================
# 18. CUSTOMER COUNT CHART
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    branch_performance["Branch_ID"],
    branch_performance["Customer_Count"]
)

plt.title("Customers by Branch")
plt.xlabel("Branch")
plt.ylabel("Number of Customers")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_customer_count.png",
    dpi=300
)

plt.close()


# ============================================================
# 19. TRANSACTION VALUE CHART
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    branch_performance["Branch_ID"],
    branch_performance["Total_Transaction_Value"]
)

plt.title("Transaction Value by Branch")
plt.xlabel("Branch")
plt.ylabel("Total Transaction Value")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_transaction_value.png",
    dpi=300
)

plt.close()


# ============================================================
# 20. DEFAULT RATE CHART
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    branch_performance["Branch_ID"],
    branch_performance["Default_Rate"]
)

plt.title("Loan Default Rate by Branch")
plt.xlabel("Branch")
plt.ylabel("Default Rate (%)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_default_rate.png",
    dpi=300
)

plt.close()


# ============================================================
# 21. PERFORMANCE SCORE CHART
# ============================================================

performance_chart = branch_performance.sort_values(
    "Performance_Score",
    ascending=False
)

plt.figure(figsize=(10, 6))

plt.bar(
    performance_chart["Branch_ID"],
    performance_chart["Performance_Score"]
)

plt.title("Branch Performance Score")
plt.xlabel("Branch")
plt.ylabel("Performance Score")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_performance_score.png",
    dpi=300
)

plt.close()


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 65)
print("BRANCH PERFORMANCE ANALYSIS COMPLETED")
print("=" * 65)

print("\nCSV reports saved inside:")
print("reports/")

print("\nCharts saved inside:")
print("reports/")

print("\nBranch performance analysis completed successfully.")