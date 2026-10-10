# NEXORA BANK — Banking Analytics & Customer Insights

A data analytics project that transforms banking data into actionable insights through Python, SQL, Streamlit, and Power BI.

**Developed by:** Sayed Nadeem Kazi  
**Project Guide:** Maimuneesa Kazi  
**Institute:** Apponix Academy  
**Course:** Data Analytics

---

## Project Overview

NEXORA BANK is a banking analytics project designed to analyze customer profiles, account balances, transactions, loan portfolios, branch performance, and customer risk.

The project combines data processing, SQL-based analysis, interactive visualizations, and a Streamlit application to help users explore banking performance and identify useful business insights.

## Business Objectives

- Analyze customer demographics and financial profiles.
- Monitor transaction volumes, values, payment methods, and transaction status.
- Evaluate loan portfolios and identify default-risk patterns.
- Compare branch-level performance.
- Segment customers and generate product recommendations.
- Identify data-quality issues and improve reporting.
- Present analytical findings through interactive dashboards and reports.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data analysis and application development |
| Pandas | Data manipulation and analysis |
| MySQL | Relational database and SQL analysis |
| Streamlit | Interactive banking analytics application |
| Power BI | Business intelligence and dashboard reporting |
| Matplotlib / visualization libraries | Charts and graphical analysis |
| Git and GitHub | Version control and project documentation |

## Project Features

### 1. Customer Analytics
- Customer financial profile analysis
- Income and account-balance analysis
- Customer segmentation
- Customer-level transaction analysis

### 2. Transaction Analytics
- Transaction volume and value analysis
- Payment-method comparisons
- Transaction status analysis
- Monthly transaction trends

### 3. Loan Portfolio Analysis
- Loan type and loan amount analysis
- Interest rate and tenure analysis
- Loan default-rate analysis
- Credit-score and loan-risk analysis

### 4. Branch Performance
- Customer distribution by branch
- Branch-level account and balance analysis
- Branch transaction performance
- Branch loan portfolio and risk comparisons

### 5. Customer Product Recommendations
The project analyzes customer financial and banking characteristics to generate product recommendations that can support customer engagement and business decision-making.

### 6. Data Quality
- Missing-value checks
- Duplicate-record checks
- Dataset validation
- Data quality reporting

### 7. Interactive Application
The Streamlit application provides a user interface for exploring banking analytics. The project includes login functionality and separate administrator and user interfaces.

## Dataset Overview

The project analyzes the following banking datasets:

| Dataset | Records |
|---|---:|
| Customers | 10,000 |
| Transactions | 50,000 |
| Loans | 5,000 |
| Branches | 8 |

Additional datasets cover accounts, employees, and products.

## Key Analytical Findings

- **Total transaction value:** Approximately ₹1.24 billion
- **Total loan portfolio:** Approximately ₹11.82 billion
- **Loan defaults:** 443
- **Overall loan default rate:** 8.86%

These figures summarize the project dataset and are intended for analytical demonstration, not as verified financial information from a real bank.

## Repository Structure

```text
NEXORA-BANK/
├── README.md
├── .gitignore
├── app2.py
├── SQL/
│   └── SQL_ANALYSIS.sql
├── analysis/
│   ├── account_analysis.py
│   ├── branch_performance.py
│   ├── customer_analysis.py
│   ├── customer_risk_analysis.py
│   ├── data_quality.py
│   ├── loan_analysis.py
│   ├── product_recomendation.py
│   └── transaction_analysis.py
├── data/
│   ├── accounts.csv
│   ├── branches.csv
│   ├── customers.csv
│   ├── employees.csv
│   ├── loans.csv
│   ├── products.csv
│   └── transactions.csv
└── reports/
    ├── CSV analytical reports
    └── PNG charts and visualizations
```

## Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- MySQL Server
- Git
- Visual Studio Code (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/Nadeemkazi07/NEXORA-BANK.git
cd NEXORA-BANK
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the packages required by the application and analysis scripts. For example, if these match the imports in your project:

```bash
pip install streamlit pandas sqlalchemy pymysql matplotlib
```

Install any additional libraries imported by your existing code.

### 4. Configure MySQL

1. Start your MySQL Server.
2. Create or configure the project database.
3. Configure the database connection using environment variables or Streamlit secrets.
4. Prepare the required tables and data before running database-dependent features.

Never publish your database password, private credentials, or sensitive customer records.

### 5. Run the Streamlit application

```bash
streamlit run app2.py
```

Open the local URL displayed in your terminal.

**Note:** The exact database setup and dependency list should be confirmed against the current application code and SQL script.

## Project Learning Outcomes

This project demonstrates practical experience in:

- Data cleaning and exploratory data analysis
- SQL queries and relational data handling
- Banking KPI analysis
- Customer and loan-risk analysis
- Data visualization and dashboard development
- Interactive application development
- Analytical reporting and business interpretation
- Version control with Git and GitHub

## Future Enhancements

- Expand automated data-quality monitoring.
- Add scheduled reporting and data refresh workflows.
- Improve authentication and access-control management.
- Extend predictive risk analysis after model development and evaluation.
- Deploy the application in a secure hosted environment.

## Disclaimer

NEXORA BANK is an educational data analytics project. Dataset values are used for demonstration and should not be interpreted as actual financial information from a real banking institution. Product recommendations and risk analysis are analytical outputs, not financial advice.

## Author

**Sayed Nadeem Kazi**

- GitHub: [@Nadeemkazi07](https://github.com/Nadeemkazi07)
- Project repository: [NEXORA-BANK](https://github.com/Nadeemkazi07/NEXORA-BANK)

