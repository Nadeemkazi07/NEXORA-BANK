from pathlib import Path
import pandas as pd


# Project folders
DATA_DIR = Path("data")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


# Files to analyze
files = {
    "Branches": "branches.csv",
    "Customers": "customers.csv",
    "Accounts": "accounts.csv",
    "Transactions": "transactions.csv",
    "Loans": "loans.csv",
    "Employees": "employees.csv",
    "Products": "products.csv"
}


def check_dataset(name, filename):

    file_path = DATA_DIR / filename

    print("\n" + "=" * 60)
    print(f"{name.upper()} DATA QUALITY CHECK")
    print("=" * 60)

    df = pd.read_csv(file_path)

    print(f"Rows              : {len(df):,}")
    print(f"Columns           : {len(df.columns)}")
    print(f"Missing Values    : {df.isnull().sum().sum():,}")
    print(f"Duplicate Rows    : {df.duplicated().sum():,}")

    print("\nColumn Names:")
    print(list(df.columns))

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values by Column:")

    missing = df.isnull().sum()

    if missing.sum() == 0:
        print("No missing values found.")
    else:
        print(missing[missing > 0])

    print("\nBasic Statistics:")

    numeric_columns = df.select_dtypes(include="number").columns

    if len(numeric_columns) > 0:
        print(df[numeric_columns].describe().round(2))

    return {
        "Dataset": name,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing_Values": int(df.isnull().sum().sum()),
        "Duplicate_Rows": int(df.duplicated().sum())
    }


def main():

    print("\n")
    print("=" * 60)
    print("       NEXORA BANK - DATA QUALITY ANALYSIS")
    print("=" * 60)

    results = []

    for name, filename in files.items():

        try:
            result = check_dataset(name, filename)
            results.append(result)

        except FileNotFoundError:
            print(f"\nFile not found: {filename}")

        except Exception as e:
            print(f"\nError while processing {filename}: {e}")

    # Create final report
    if results:

        report = pd.DataFrame(results)

        report.to_csv(
            REPORT_DIR / "data_quality_report.csv",
            index=False
        )

        print("\n")
        print("=" * 60)
        print("DATA QUALITY SUMMARY")
        print("=" * 60)

        print(report.to_string(index=False))

        print("\nReport created:")
        print("reports/data_quality_report.csv")

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()