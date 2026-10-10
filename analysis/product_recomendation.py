from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# NEXORA BANK - CUSTOMER SEGMENTATION
# & PRODUCT RECOMMENDATION
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
products = pd.read_csv(DATA_DIR / "products.csv")


print("\n" + "=" * 60)
print("NEXORA BANK - CUSTOMER SEGMENTATION")
print("AND PRODUCT RECOMMENDATION")
print("=" * 60)


# ------------------------------------------------------------
# 2. LOAN SUMMARY
# ------------------------------------------------------------

loan_summary = (
    loans
    .groupby("Customer_ID")
    .agg(
        Loan_Count=("Loan_ID", "count"),
        Total_Loan_Amount=("Loan_Amount", "sum"),
        Default_Count=("Default_Flag", "sum")
    )
    .reset_index()
)


# ------------------------------------------------------------
# 3. TRANSACTION SUMMARY
# ------------------------------------------------------------

transaction_summary = (
    transactions
    .groupby("Customer_ID")
    .agg(
        Transaction_Count=("Transaction_ID", "count"),
        Total_Transaction_Value=("Amount", "sum")
    )
    .reset_index()
)


# ------------------------------------------------------------
# 4. MERGE CUSTOMER INFORMATION
# ------------------------------------------------------------

customer_data = customers.merge(
    loan_summary,
    on="Customer_ID",
    how="left"
)

customer_data = customer_data.merge(
    transaction_summary,
    on="Customer_ID",
    how="left"
)


customer_data[
    [
        "Loan_Count",
        "Total_Loan_Amount",
        "Default_Count",
        "Transaction_Count",
        "Total_Transaction_Value"
    ]
] = customer_data[
    [
        "Loan_Count",
        "Total_Loan_Amount",
        "Default_Count",
        "Transaction_Count",
        "Total_Transaction_Value"
    ]
].fillna(0)


# ------------------------------------------------------------
# 5. CUSTOMER VALUE SEGMENT
# ------------------------------------------------------------

def customer_segment(row):

    if (
        row["Account_Balance"] >= 500000
        and row["Monthly_Income"] >= 75000
    ):
        return "Premium"

    elif (
        row["Account_Balance"] >= 100000
        or row["Monthly_Income"] >= 50000
    ):
        return "High Value"

    elif (
        row["Account_Balance"] >= 25000
        or row["Monthly_Income"] >= 30000
    ):
        return "Regular"

    else:
        return "Low Value"


customer_data["Calculated_Segment"] = (
    customer_data.apply(
        customer_segment,
        axis=1
    )
)


# ------------------------------------------------------------
# 6. PRODUCT RECOMMENDATION
# ------------------------------------------------------------

def recommend_product(row):

    credit_score = row["Credit_Score"]
    income = row["Monthly_Income"]
    balance = row["Account_Balance"]
    loan_count = row["Loan_Count"]
    defaults = row["Default_Count"]
    transactions_count = row["Transaction_Count"]

    # Existing credit risk takes priority
    if defaults >= 2 or credit_score < 580:
        return "Savings Account"

    # Premium customers
    if (
        balance >= 500000
        and income >= 75000
        and credit_score >= 700
    ):
        return "Investment Product"

    # Premium credit-card profile
    if (
        income >= 75000
        and credit_score >= 700
        and balance >= 200000
    ):
        return "Premium Credit Card"

    # Personal loan profile
    if (
        income >= 50000
        and credit_score >= 680
        and loan_count == 0
    ):
        return "Personal Loan"

    # Credit card profile
    if (
        income >= 40000
        and credit_score >= 650
        and transactions_count >= 5
    ):
        return "Credit Card"

    # Existing stable customers
    if balance >= 100000:
        return "Investment Product"

    return "Savings Account"


customer_data["Recommended_Product"] = (
    customer_data.apply(
        recommend_product,
        axis=1
    )
)


# ------------------------------------------------------------
# 7. RECOMMENDATION REASON
# ------------------------------------------------------------

def recommendation_reason(row):

    product = row["Recommended_Product"]

    if product == "Investment Product":
        return (
            "High balance and income indicate "
            "potential investment capacity"
        )

    elif product == "Premium Credit Card":
        return (
            "High income, strong credit score "
            "and substantial balance"
        )

    elif product == "Personal Loan":
        return (
            "Good credit profile, sufficient income "
            "and no existing loan"
        )

    elif product == "Credit Card":
        return (
            "Stable income, good credit score "
            "and active transaction behavior"
        )

    return (
        "Suitable basic banking product based "
        "on current financial profile"
    )


customer_data["Recommendation_Reason"] = (
    customer_data.apply(
        recommendation_reason,
        axis=1
    )
)


# ------------------------------------------------------------
# 8. SEGMENT SUMMARY
# ------------------------------------------------------------

segment_summary = (
    customer_data
    .groupby("Calculated_Segment")
    .agg(
        Customer_Count=("Customer_ID", "count"),
        Average_Income=("Monthly_Income", "mean"),
        Average_Balance=("Account_Balance", "mean"),
        Average_Credit_Score=("Credit_Score", "mean"),
        Average_Transaction_Value=(
            "Total_Transaction_Value",
            "mean"
        )
    )
    .reset_index()
)

segment_summary["Percentage"] = (
    segment_summary["Customer_Count"]
    / len(customer_data)
    * 100
).round(2)


print("\n" + "=" * 60)
print("CUSTOMER SEGMENTATION")
print("=" * 60)

print(
    segment_summary
    .round(2)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 9. PRODUCT RECOMMENDATION SUMMARY
# ------------------------------------------------------------

product_summary = (
    customer_data
    .groupby("Recommended_Product")
    .agg(
        Customer_Count=("Customer_ID", "count"),
        Average_Income=("Monthly_Income", "mean"),
        Average_Balance=("Account_Balance", "mean"),
        Average_Credit_Score=("Credit_Score", "mean")
    )
    .reset_index()
)

product_summary["Percentage"] = (
    product_summary["Customer_Count"]
    / len(customer_data)
    * 100
).round(2)

product_summary = product_summary.sort_values(
    "Customer_Count",
    ascending=False
)


print("\n" + "=" * 60)
print("PRODUCT RECOMMENDATION SUMMARY")
print("=" * 60)

print(
    product_summary
    .round(2)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 10. BRANCH-WISE PRODUCT RECOMMENDATION
# ------------------------------------------------------------

branch_product = (
    customer_data
    .groupby(
        [
            "Branch_ID",
            "Recommended_Product"
        ]
    )
    .size()
    .reset_index(
        name="Customer_Count"
    )
)


print("\n" + "=" * 60)
print("BRANCH-WISE PRODUCT RECOMMENDATIONS")
print("=" * 60)

print(
    branch_product
    .sort_values(
        ["Branch_ID", "Customer_Count"],
        ascending=[True, False]
    )
    .to_string(index=False)
)


# ------------------------------------------------------------
# 11. SAVE CUSTOMER RECOMMENDATIONS
# ------------------------------------------------------------

recommendation_report = customer_data[
    [
        "Customer_ID",
        "Name",
        "Branch_ID",
        "Account_Type",
        "Monthly_Income",
        "Account_Balance",
        "Credit_Score",
        "Loan_Count",
        "Total_Loan_Amount",
        "Default_Count",
        "Transaction_Count",
        "Total_Transaction_Value",
        "Calculated_Segment",
        "Recommended_Product",
        "Recommendation_Reason"
    ]
].copy()


recommendation_report.to_csv(
    REPORT_DIR / "customer_product_recommendations.csv",
    index=False
)

segment_summary.to_csv(
    REPORT_DIR / "customer_segment_summary.csv",
    index=False
)

product_summary.to_csv(
    REPORT_DIR / "product_recommendation_summary.csv",
    index=False
)

branch_product.to_csv(
    REPORT_DIR / "branch_product_recommendations.csv",
    index=False
)


# ------------------------------------------------------------
# 12. SEGMENT CHART
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    segment_summary["Calculated_Segment"],
    segment_summary["Customer_Count"]
)

plt.title("Customer Segmentation")
plt.xlabel("Customer Segment")
plt.ylabel("Number of Customers")

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "customer_segmentation.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 13. PRODUCT RECOMMENDATION CHART
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    product_summary["Recommended_Product"],
    product_summary["Customer_Count"]
)

plt.title("Recommended Banking Products")
plt.xlabel("Recommended Product")
plt.ylabel("Number of Customers")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "product_recommendations.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 14. FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CUSTOMER SEGMENTATION & PRODUCT RECOMMENDATION COMPLETED")
print("=" * 60)

print("\nCSV reports saved inside:")
print("reports/")

print("\nCharts saved inside:")
print("reports/")

print("\nCustomer segmentation completed successfully.")