from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - TRANSACTION ANALYSIS
# ============================================================

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# 1. LOAD TRANSACTION DATA
# ------------------------------------------------------------

transactions = pd.read_csv(
    DATA_DIR / "transactions.csv"
)

# Convert transaction date
transactions["Transaction_Date"] = pd.to_datetime(
    transactions["Transaction_Date"]
)

print("\n" + "=" * 60)
print("NEXORA BANK - TRANSACTION ANALYSIS")
print("=" * 60)


# ------------------------------------------------------------
# 2. BASIC TRANSACTION KPIs
# ------------------------------------------------------------

total_transactions = len(transactions)

total_amount = transactions["Amount"].sum()

average_transaction = transactions["Amount"].mean()

median_transaction = transactions["Amount"].median()

highest_transaction = transactions["Amount"].max()

lowest_transaction = transactions["Amount"].min()

unique_customers = transactions["Customer_ID"].nunique()


print("\n" + "=" * 60)
print("TRANSACTION KPIs")
print("=" * 60)

print(f"Total Transactions       : {total_transactions:,}")
print(f"Total Transaction Value  : ₹{total_amount:,.2f}")
print(f"Average Transaction      : ₹{average_transaction:,.2f}")
print(f"Median Transaction       : ₹{median_transaction:,.2f}")
print(f"Highest Transaction      : ₹{highest_transaction:,.2f}")
print(f"Lowest Transaction       : ₹{lowest_transaction:,.2f}")
print(f"Unique Customers         : {unique_customers:,}")


# ------------------------------------------------------------
# 3. TRANSACTION STATUS
# ------------------------------------------------------------

status_analysis = (
    transactions["Transaction_Status"]
    .value_counts()
    .reset_index()
)

status_analysis.columns = [
    "Transaction_Status",
    "Transaction_Count"
]

status_analysis["Percentage"] = (
    status_analysis["Transaction_Count"]
    / total_transactions
    * 100
).round(2)

print("\n" + "=" * 60)
print("TRANSACTION STATUS")
print("=" * 60)

print(status_analysis.to_string(index=False))

status_analysis.to_csv(
    REPORT_DIR / "transaction_status_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 4. PAYMENT METHOD ANALYSIS
# ------------------------------------------------------------

payment_analysis = (
    transactions
    .groupby("Payment_Method")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Amount=("Amount", "sum"),
        Average_Amount=("Amount", "mean")
    )
    .reset_index()
)

payment_analysis["Percentage"] = (
    payment_analysis["Transaction_Count"]
    / total_transactions
    * 100
).round(2)

payment_analysis = payment_analysis.sort_values(
    "Total_Amount",
    ascending=False
)

print("\n" + "=" * 60)
print("PAYMENT METHOD ANALYSIS")
print("=" * 60)

print(payment_analysis.round(2).to_string(index=False))

payment_analysis.to_csv(
    REPORT_DIR / "payment_method_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 5. TRANSACTION TYPE ANALYSIS
# ------------------------------------------------------------

transaction_type_analysis = (
    transactions
    .groupby("Transaction_Type")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Amount=("Amount", "sum"),
        Average_Amount=("Amount", "mean")
    )
    .reset_index()
)

transaction_type_analysis = transaction_type_analysis.sort_values(
    "Total_Amount",
    ascending=False
)

print("\n" + "=" * 60)
print("TRANSACTION TYPE ANALYSIS")
print("=" * 60)

print(
    transaction_type_analysis
    .round(2)
    .to_string(index=False)
)

transaction_type_analysis.to_csv(
    REPORT_DIR / "transaction_type_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 6. MONTHLY TRANSACTION ANALYSIS
# ------------------------------------------------------------

transactions["Month"] = (
    transactions["Transaction_Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_analysis = (
    transactions
    .groupby("Month")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Amount=("Amount", "sum"),
        Average_Amount=("Amount", "mean")
    )
    .reset_index()
)

print("\n" + "=" * 60)
print("MONTHLY TRANSACTION ANALYSIS")
print("=" * 60)

print(
    monthly_analysis
    .round(2)
    .to_string(index=False)
)

monthly_analysis.to_csv(
    REPORT_DIR / "monthly_transaction_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 7. BRANCH-WISE TRANSACTION ANALYSIS
# ------------------------------------------------------------

branch_analysis = (
    transactions
    .groupby("Branch_ID")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Amount=("Amount", "sum"),
        Average_Amount=("Amount", "mean"),
        Unique_Customers=("Customer_ID", "nunique")
    )
    .reset_index()
)

branch_analysis["Amount_Per_Customer"] = (
    branch_analysis["Total_Amount"]
    / branch_analysis["Unique_Customers"]
)

branch_analysis = branch_analysis.sort_values(
    "Total_Amount",
    ascending=False
)

print("\n" + "=" * 60)
print("BRANCH-WISE TRANSACTION ANALYSIS")
print("=" * 60)

print(
    branch_analysis
    .round(2)
    .to_string(index=False)
)

branch_analysis.to_csv(
    REPORT_DIR / "branch_transaction_analysis.csv",
    index=False
)


# ------------------------------------------------------------
# 8. HIGH-VALUE TRANSACTIONS
# ------------------------------------------------------------

high_value_transactions = (
    transactions
    .sort_values(
        "Amount",
        ascending=False
    )
    .head(20)
)

print("\n" + "=" * 60)
print("TOP 20 HIGH-VALUE TRANSACTIONS")
print("=" * 60)

print(
    high_value_transactions[
        [
            "Transaction_ID",
            "Customer_ID",
            "Transaction_Date",
            "Transaction_Type",
            "Amount",
            "Payment_Method",
            "Branch_ID",
            "Transaction_Status"
        ]
    ]
    .round(2)
    .to_string(index=False)
)

high_value_transactions.to_csv(
    REPORT_DIR / "top_20_transactions.csv",
    index=False
)


# ------------------------------------------------------------
# 9. CUSTOMER TRANSACTION ANALYSIS
# ------------------------------------------------------------

customer_transactions = (
    transactions
    .groupby("Customer_ID")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Transaction_Value=("Amount", "sum"),
        Average_Transaction_Value=("Amount", "mean")
    )
    .reset_index()
)

customer_transactions = customer_transactions.sort_values(
    "Total_Transaction_Value",
    ascending=False
)

print("\n" + "=" * 60)
print("TOP 10 CUSTOMERS BY TRANSACTION VALUE")
print("=" * 60)

print(
    customer_transactions
    .head(10)
    .round(2)
    .to_string(index=False)
)

customer_transactions.to_csv(
    REPORT_DIR / "customer_transaction_analysis.csv",
    index=False
)


# ============================================================
# VISUALIZATIONS
# ============================================================


# ------------------------------------------------------------
# 10. PAYMENT METHOD CHART
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    payment_analysis["Payment_Method"],
    payment_analysis["Transaction_Count"]
)

plt.title("Transactions by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Number of Transactions")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "transactions_by_payment_method.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 11. MONTHLY TRANSACTION TREND
# ------------------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_analysis["Month"],
    monthly_analysis["Total_Amount"],
    marker="o"
)

plt.title("Monthly Transaction Value")
plt.xlabel("Month")
plt.ylabel("Transaction Value (₹)")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "monthly_transaction_trend.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 12. BRANCH TRANSACTION VALUE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    branch_analysis["Branch_ID"],
    branch_analysis["Total_Amount"]
)

plt.title("Transaction Value by Branch")
plt.xlabel("Branch")
plt.ylabel("Total Transaction Value (₹)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "branch_transaction_value.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 13. TRANSACTION AMOUNT DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.hist(
    transactions["Amount"],
    bins=30
)

plt.title("Transaction Amount Distribution")
plt.xlabel("Transaction Amount (₹)")
plt.ylabel("Number of Transactions")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "transaction_amount_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 14. TRANSACTION TYPE VALUE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    transaction_type_analysis["Transaction_Type"],
    transaction_type_analysis["Total_Amount"]
)

plt.title("Transaction Value by Transaction Type")
plt.xlabel("Transaction Type")
plt.ylabel("Total Transaction Value (₹)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "transaction_type_value.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("TRANSACTION ANALYSIS COMPLETED")
print("=" * 60)

print("\nCSV reports saved inside:")
print("reports/")

print("\nCharts saved inside:")
print("reports/")

print("\nTransaction EDA completed successfully.")