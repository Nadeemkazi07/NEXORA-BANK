from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - CUSTOMER ANALYSIS
# ============================================================

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# 1. LOAD CUSTOMER DATA
# ------------------------------------------------------------

customers = pd.read_csv(DATA_DIR / "customers.csv")

# Convert registration date to datetime
customers["Registration_Date"] = pd.to_datetime(
    customers["Registration_Date"]
)

print("\n" + "=" * 60)
print("NEXORA BANK - CUSTOMER ANALYSIS")
print("=" * 60)

print(f"\nTotal Customers: {customers['Customer_ID'].nunique():,}")


# ------------------------------------------------------------
# 2. CUSTOMER COUNT BY BRANCH
# ------------------------------------------------------------

branch_customers = (
    customers
    .groupby(["Branch_ID", "City"])
    .agg(
        Customer_Count=("Customer_ID", "nunique"),
        Average_Balance=("Account_Balance", "mean"),
        Average_Income=("Monthly_Income", "mean"),
        Average_Credit_Score=("Credit_Score", "mean")
    )
    .reset_index()
)

branch_customers = branch_customers.sort_values(
    "Customer_Count",
    ascending=False
)

print("\n" + "=" * 60)
print("CUSTOMERS BY BRANCH")
print("=" * 60)

print(branch_customers.round(2).to_string(index=False))

branch_customers.to_csv(
    REPORT_DIR / "customers_by_branch.csv",
    index=False
)


# ------------------------------------------------------------
# 3. GENDER ANALYSIS
# ------------------------------------------------------------

gender_analysis = (
    customers["Gender"]
    .value_counts()
    .reset_index()
)

gender_analysis.columns = [
    "Gender",
    "Customer_Count"
]

gender_analysis["Percentage"] = (
    gender_analysis["Customer_Count"]
    / len(customers)
    * 100
).round(2)

print("\n" + "=" * 60)
print("GENDER DISTRIBUTION")
print("=" * 60)

print(gender_analysis.to_string(index=False))

gender_analysis.to_csv(
    REPORT_DIR / "gender_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 4. ACCOUNT TYPE ANALYSIS
# ------------------------------------------------------------

account_analysis = (
    customers["Account_Type"]
    .value_counts()
    .reset_index()
)

account_analysis.columns = [
    "Account_Type",
    "Customer_Count"
]

account_analysis["Percentage"] = (
    account_analysis["Customer_Count"]
    / len(customers)
    * 100
).round(2)

print("\n" + "=" * 60)
print("ACCOUNT TYPE ANALYSIS")
print("=" * 60)

print(account_analysis.to_string(index=False))

account_analysis.to_csv(
    REPORT_DIR / "account_type_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 5. AGE GROUP ANALYSIS
# ------------------------------------------------------------

customers["Age_Group"] = pd.cut(
    customers["Age"],
    bins=[0, 25, 35, 45, 55, 65, 100],
    labels=[
        "18-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "65+"
    ]
)

age_analysis = (
    customers["Age_Group"]
    .value_counts()
    .sort_index()
    .reset_index()
)

age_analysis.columns = [
    "Age_Group",
    "Customer_Count"
]

print("\n" + "=" * 60)
print("AGE GROUP ANALYSIS")
print("=" * 60)

print(age_analysis.to_string(index=False))

age_analysis.to_csv(
    REPORT_DIR / "age_group_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 6. CUSTOMER SEGMENT ANALYSIS
# ------------------------------------------------------------

segment_analysis = (
    customers
    .groupby("Customer_Segment", observed=True)
    .agg(
        Customer_Count=("Customer_ID", "nunique"),
        Average_Income=("Monthly_Income", "mean"),
        Average_Balance=("Account_Balance", "mean"),
        Average_Credit_Score=("Credit_Score", "mean")
    )
    .reset_index()
)

segment_analysis["Percentage"] = (
    segment_analysis["Customer_Count"]
    / len(customers)
    * 100
).round(2)

print("\n" + "=" * 60)
print("CUSTOMER SEGMENT ANALYSIS")
print("=" * 60)

print(segment_analysis.round(2).to_string(index=False))

segment_analysis.to_csv(
    REPORT_DIR / "customer_segment_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 7. BRANCH-WISE CREDIT SCORE
# ------------------------------------------------------------

credit_analysis = (
    customers
    .groupby(["Branch_ID", "City"])
    .agg(
        Average_Credit_Score=("Credit_Score", "mean"),
        Minimum_Credit_Score=("Credit_Score", "min"),
        Maximum_Credit_Score=("Credit_Score", "max")
    )
    .reset_index()
)

print("\n" + "=" * 60)
print("BRANCH-WISE CREDIT SCORE")
print("=" * 60)

print(credit_analysis.round(2).to_string(index=False))

credit_analysis.to_csv(
    REPORT_DIR / "branch_credit_score_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 8. TOP 10 CUSTOMERS BY ACCOUNT BALANCE
# ------------------------------------------------------------

top_customers = (
    customers[
        [
            "Customer_ID",
            "Name",
            "City",
            "Branch_ID",
            "Account_Type",
            "Account_Balance",
            "Credit_Score"
        ]
    ]
    .sort_values(
        "Account_Balance",
        ascending=False
    )
    .head(10)
)

print("\n" + "=" * 60)
print("TOP 10 CUSTOMERS BY ACCOUNT BALANCE")
print("=" * 60)

print(top_customers.round(2).to_string(index=False))

top_customers.to_csv(
    REPORT_DIR / "top_10_customers.csv",
    index=False
)


# ============================================================
# VISUALIZATIONS
# ============================================================

# ------------------------------------------------------------
# 9. CUSTOMER COUNT BY BRANCH
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    branch_customers["City"],
    branch_customers["Customer_Count"]
)

plt.title("Customer Count by Branch")
plt.xlabel("Branch")
plt.ylabel("Number of Customers")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "customer_count_by_branch.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 10. ACCOUNT TYPE DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

plt.bar(
    account_analysis["Account_Type"],
    account_analysis["Customer_Count"]
)

plt.title("Customer Distribution by Account Type")
plt.xlabel("Account Type")
plt.ylabel("Number of Customers")

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "account_type_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 11. AGE GROUP DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.bar(
    age_analysis["Age_Group"].astype(str),
    age_analysis["Customer_Count"]
)

plt.title("Customer Distribution by Age Group")
plt.xlabel("Age Group")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "age_group_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 12. CUSTOMER SEGMENT DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.bar(
    segment_analysis["Customer_Segment"],
    segment_analysis["Customer_Count"]
)

plt.title("Customer Segment Distribution")
plt.xlabel("Customer Segment")
plt.ylabel("Number of Customers")

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "customer_segment_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 13. CREDIT SCORE DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.hist(
    customers["Credit_Score"],
    bins=20
)

plt.title("Credit Score Distribution")
plt.xlabel("Credit Score")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "credit_score_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 14. INCOME VS ACCOUNT BALANCE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    customers["Monthly_Income"],
    customers["Account_Balance"],
    alpha=0.5
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


# ------------------------------------------------------------
# FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CUSTOMER ANALYSIS COMPLETED")
print("=" * 60)

print("\nCSV reports created inside:")
print("reports/")

print("\nCharts created inside:")
print("reports/")

print("\nCustomer EDA completed successfully.")