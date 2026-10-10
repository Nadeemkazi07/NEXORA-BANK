
USE nexora_bank;

-- 1. DATABASE CHECKS
SHOW TABLES;

SELECT 'branches' AS Table_Name, COUNT(*) AS Row_Count FROM branches
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL SELECT 'loans', COUNT(*) FROM loans
UNION ALL SELECT 'employees', COUNT(*) FROM employees;

-- 2. DATA QUALITY
SELECT COUNT(*) AS Total_Customers,
       COUNT(DISTINCT Customer_ID) AS Unique_Customers,
       COUNT(*) - COUNT(DISTINCT Customer_ID) AS Duplicate_Customer_IDs
FROM customers;

SELECT COUNT(*) AS Total_Accounts,
       COUNT(DISTINCT Account_ID) AS Unique_Accounts,
       COUNT(*) - COUNT(DISTINCT Account_ID) AS Duplicate_Account_IDs
FROM accounts;

SELECT COUNT(*) AS Total_Transactions,
       COUNT(DISTINCT Transaction_ID) AS Unique_Transactions,
       COUNT(*) - COUNT(DISTINCT Transaction_ID) AS Duplicate_Transaction_IDs
FROM transactions;

SELECT COUNT(*) AS Total_Loans,
       COUNT(DISTINCT Loan_ID) AS Unique_Loans,
       COUNT(*) - COUNT(DISTINCT Loan_ID) AS Duplicate_Loan_IDs
FROM loans;

-- 3. ACCOUNT ANALYSIS
SELECT COUNT(*) AS Total_Accounts,
       ROUND(SUM(Opening_Balance),2) AS Total_Opening_Balance,
       ROUND(SUM(Current_Balance),2) AS Total_Current_Balance,
       ROUND(AVG(Opening_Balance),2) AS Average_Opening_Balance,
       ROUND(AVG(Current_Balance),2) AS Average_Current_Balance,
       ROUND(SUM(Current_Balance)-SUM(Opening_Balance),2) AS Balance_Change,
       ROUND((SUM(Current_Balance)-SUM(Opening_Balance))*100.0/
             NULLIF(SUM(Opening_Balance),0),2) AS Balance_Growth_Percentage
FROM accounts;

SELECT Account_Status, COUNT(*) AS Account_Count,
       ROUND(SUM(Current_Balance),2) AS Total_Current_Balance,
       ROUND(AVG(Current_Balance),2) AS Average_Current_Balance,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM accounts),2) AS Percentage
FROM accounts
GROUP BY Account_Status ORDER BY Account_Count DESC;

SELECT Account_Type, COUNT(*) AS Account_Count,
       ROUND(SUM(Current_Balance),2) AS Total_Current_Balance,
       ROUND(AVG(Current_Balance),2) AS Average_Current_Balance,
       ROUND(AVG(Opening_Balance),2) AS Average_Opening_Balance,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM accounts),2) AS Percentage
FROM accounts
GROUP BY Account_Type ORDER BY Account_Count DESC;

SELECT b.Branch_ID,b.Branch_Name,b.City,
       COUNT(a.Account_ID) AS Account_Count,
       ROUND(SUM(a.Opening_Balance),2) AS Total_Opening_Balance,
       ROUND(SUM(a.Current_Balance),2) AS Total_Current_Balance,
       ROUND(SUM(a.Current_Balance)-SUM(a.Opening_Balance),2) AS Balance_Change,
       ROUND((SUM(a.Current_Balance)-SUM(a.Opening_Balance))*100.0/
             NULLIF(SUM(a.Opening_Balance),0),2) AS Balance_Growth_Percentage
FROM accounts a JOIN branches b ON a.Branch_ID=b.Branch_ID
GROUP BY b.Branch_ID,b.Branch_Name,b.City
ORDER BY Total_Current_Balance DESC;

SELECT Branch_ID,Account_Status,COUNT(*) AS Account_Count
FROM accounts GROUP BY Branch_ID,Account_Status
ORDER BY Branch_ID,Account_Status;

-- 4. TRANSACTION ANALYSIS
SELECT COUNT(*) AS Total_Transactions,
       ROUND(SUM(Amount),2) AS Total_Transaction_Value,
       ROUND(AVG(Amount),2) AS Average_Transaction,
       ROUND(MIN(Amount),2) AS Lowest_Transaction,
       ROUND(MAX(Amount),2) AS Highest_Transaction,
       COUNT(DISTINCT Customer_ID) AS Unique_Customers
FROM transactions;

SELECT Transaction_Status,COUNT(*) AS Transaction_Count,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM transactions),2) AS Percentage
FROM transactions
GROUP BY Transaction_Status ORDER BY Transaction_Count DESC;

SELECT Payment_Method,COUNT(*) AS Transaction_Count,
       ROUND(SUM(Amount),2) AS Total_Amount,
       ROUND(AVG(Amount),2) AS Average_Amount
FROM transactions
GROUP BY Payment_Method ORDER BY Total_Amount DESC;

SELECT b.Branch_ID,b.Branch_Name,COUNT(t.Transaction_ID) AS Transaction_Count,
       ROUND(SUM(t.Amount),2) AS Total_Transaction_Value,
       ROUND(AVG(t.Amount),2) AS Average_Transaction_Value
FROM transactions t JOIN branches b ON t.Branch_ID=b.Branch_ID
GROUP BY b.Branch_ID,b.Branch_Name
ORDER BY Total_Transaction_Value DESC;

-- 5. LOAN ANALYSIS
SELECT COUNT(*) AS Total_Loans,
       ROUND(SUM(Loan_Amount),2) AS Total_Loan_Value,
       ROUND(AVG(Loan_Amount),2) AS Average_Loan_Amount,
       ROUND(AVG(Interest_Rate),2) AS Average_Interest_Rate,
       ROUND(AVG(Tenure_Months),2) AS Average_Tenure,
       ROUND(AVG(EMI),2) AS Average_EMI,
       SUM(Default_Flag) AS Defaulted_Loans,
       ROUND(SUM(Default_Flag)*100.0/COUNT(*),2) AS Default_Rate
FROM loans;

SELECT Loan_Type,COUNT(*) AS Loan_Count,
       ROUND(SUM(Loan_Amount),2) AS Total_Loan_Amount,
       ROUND(AVG(Loan_Amount),2) AS Average_Loan_Amount,
       ROUND(AVG(Interest_Rate),2) AS Average_Interest_Rate,
       ROUND(AVG(Tenure_Months),2) AS Average_Tenure,
       ROUND(AVG(EMI),2) AS Average_EMI,
       ROUND(SUM(Loan_Amount)*100.0/(SELECT SUM(Loan_Amount) FROM loans),2) AS Portfolio_Share
FROM loans GROUP BY Loan_Type ORDER BY Total_Loan_Amount DESC;

SELECT Loan_Status,COUNT(*) AS Loan_Count,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM loans),2) AS Percentage
FROM loans GROUP BY Loan_Status ORDER BY Loan_Count DESC;

SELECT Default_Flag,COUNT(*) AS Loan_Count,
       ROUND(SUM(Loan_Amount),2) AS Total_Loan_Amount,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM loans),2) AS Percentage
FROM loans GROUP BY Default_Flag ORDER BY Default_Flag;

SELECT Loan_Type,COUNT(*) AS Total_Loans,
       SUM(Default_Flag) AS Defaulted_Loans,
       ROUND(SUM(Loan_Amount),2) AS Total_Loan_Amount,
       ROUND(SUM(Default_Flag)*100.0/COUNT(*),2) AS Default_Rate
FROM loans GROUP BY Loan_Type ORDER BY Default_Rate DESC;

SELECT CASE
         WHEN c.Credit_Score < 580 THEN 'Poor'
         WHEN c.Credit_Score < 670 THEN 'Fair'
         WHEN c.Credit_Score < 740 THEN 'Good'
         ELSE 'Excellent'
       END AS Credit_Score_Group,
       COUNT(l.Loan_ID) AS Total_Loans,
       SUM(l.Default_Flag) AS Defaulted_Loans,
       ROUND(AVG(l.Loan_Amount),2) AS Average_Loan_Amount,
       ROUND(SUM(l.Default_Flag)*100.0/COUNT(l.Loan_ID),2) AS Default_Rate
FROM loans l JOIN customers c ON l.Customer_ID=c.Customer_ID
GROUP BY CASE
         WHEN c.Credit_Score < 580 THEN 'Poor'
         WHEN c.Credit_Score < 670 THEN 'Fair'
         WHEN c.Credit_Score < 740 THEN 'Good'
         ELSE 'Excellent' END
ORDER BY Default_Rate DESC;

SELECT b.Branch_ID,b.Branch_Name,b.City,
       COUNT(l.Loan_ID) AS Loan_Count,
       ROUND(SUM(l.Loan_Amount),2) AS Total_Loan_Amount,
       ROUND(AVG(l.Loan_Amount),2) AS Average_Loan_Amount,
       SUM(l.Default_Flag) AS Defaulted_Loans,
       ROUND(SUM(l.Default_Flag)*100.0/COUNT(l.Loan_ID),2) AS Default_Rate
FROM loans l JOIN branches b ON l.Branch_ID=b.Branch_ID
GROUP BY b.Branch_ID,b.Branch_Name,b.City
ORDER BY Default_Rate DESC;

-- 6. CUSTOMER + ACCOUNT JOIN
SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Monthly_Income,c.Credit_Score,
       a.Account_Type,a.Account_Status,ROUND(a.Current_Balance,2) AS Current_Balance
FROM customers c JOIN accounts a ON c.Customer_ID=a.Customer_ID
LIMIT 20;

-- 7. CUSTOMER FINANCIAL SUMMARY
-- Transactions and loans are aggregated separately to prevent row multiplication.
SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Monthly_Income,c.Credit_Score,
       ROUND(a.Current_Balance,2) AS Account_Balance,
       COALESCE(t.Transaction_Count,0) AS Transaction_Count,
       COALESCE(t.Total_Transaction_Value,0) AS Total_Transaction_Value,
       COALESCE(l.Loan_Count,0) AS Loan_Count,
       COALESCE(l.Total_Loan_Amount,0) AS Total_Loan_Amount,
       COALESCE(l.Default_Count,0) AS Default_Count
FROM customers c
LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
LEFT JOIN (
    SELECT Customer_ID,COUNT(*) AS Transaction_Count,
           ROUND(SUM(Amount),2) AS Total_Transaction_Value
    FROM transactions GROUP BY Customer_ID
) t ON c.Customer_ID=t.Customer_ID
LEFT JOIN (
    SELECT Customer_ID,COUNT(*) AS Loan_Count,
           ROUND(SUM(Loan_Amount),2) AS Total_Loan_Amount,
           SUM(Default_Flag) AS Default_Count
    FROM loans GROUP BY Customer_ID
) l ON c.Customer_ID=l.Customer_ID
LIMIT 20;

-- 8. HIGH-RISK CUSTOMERS
SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Credit_Score,c.Monthly_Income,
       ROUND(a.Current_Balance,2) AS Account_Balance,
       l.Loan_Count,ROUND(l.Total_Loan_Amount,2) AS Total_Loan_Amount,
       l.Default_Count,t.Transaction_Count,
       ROUND(t.Total_Transaction_Value,2) AS Total_Transaction_Value,
       ROUND(l.Total_Loan_Amount/NULLIF(c.Monthly_Income*12,0),2)
         AS Loan_to_Annual_Income
FROM customers c
LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
LEFT JOIN (
    SELECT Customer_ID,COUNT(*) AS Loan_Count,
           SUM(Loan_Amount) AS Total_Loan_Amount,
           SUM(Default_Flag) AS Default_Count
    FROM loans GROUP BY Customer_ID
) l ON c.Customer_ID=l.Customer_ID
LEFT JOIN (
    SELECT Customer_ID,COUNT(*) AS Transaction_Count,
           SUM(Amount) AS Total_Transaction_Value
    FROM transactions GROUP BY Customer_ID
) t ON c.Customer_ID=t.Customer_ID
WHERE c.Credit_Score < 580 AND COALESCE(l.Default_Count,0)>0
ORDER BY Loan_to_Annual_Income DESC,l.Default_Count DESC
LIMIT 20;

-- 9. RISK CATEGORY SUMMARY
SELECT CASE
         WHEN c.Credit_Score < 580 OR COALESCE(l.Default_Count,0)>=2
           THEN 'High Risk'
         WHEN c.Credit_Score < 670 OR COALESCE(l.Default_Count,0)=1
           THEN 'Medium Risk'
         ELSE 'Low Risk'
       END AS Risk_Category,
       COUNT(*) AS Customer_Count,
       ROUND(AVG(c.Credit_Score),2) AS Average_Credit_Score,
       ROUND(AVG(a.Current_Balance),2) AS Average_Balance,
       ROUND(AVG(COALESCE(l.Total_Loan_Amount,0)),2) AS Average_Loan_Amount
FROM customers c
LEFT JOIN accounts a ON c.Customer_ID=a.Customer_ID
LEFT JOIN (
    SELECT Customer_ID,SUM(Loan_Amount) AS Total_Loan_Amount,
           SUM(Default_Flag) AS Default_Count
    FROM loans GROUP BY Customer_ID
) l ON c.Customer_ID=l.Customer_ID
GROUP BY CASE
         WHEN c.Credit_Score < 580 OR COALESCE(l.Default_Count,0)>=2
           THEN 'High Risk'
         WHEN c.Credit_Score < 670 OR COALESCE(l.Default_Count,0)=1
           THEN 'Medium Risk'
         ELSE 'Low Risk' END
ORDER BY Customer_Count DESC;

-- 10. BRANCH PERFORMANCE
SELECT b.Branch_ID,b.Branch_Name,b.City,
       COUNT(DISTINCT c.Customer_ID) AS Customer_Count,
       COUNT(DISTINCT a.Account_ID) AS Account_Count,
       COUNT(DISTINCT t.Transaction_ID) AS Transaction_Count,
       COUNT(DISTINCT l.Loan_ID) AS Loan_Count,
       ROUND(AVG(c.Credit_Score),2) AS Average_Credit_Score
FROM branches b
LEFT JOIN customers c ON b.Branch_ID=c.Branch_ID
LEFT JOIN accounts a ON b.Branch_ID=a.Branch_ID
LEFT JOIN transactions t ON b.Branch_ID=t.Branch_ID
LEFT JOIN loans l ON b.Branch_ID=l.Branch_ID
GROUP BY b.Branch_ID,b.Branch_Name,b.City
ORDER BY Customer_Count DESC;

-- 11. PRODUCT RECOMMENDATION
SELECT c.Customer_ID,c.Name,c.Branch_ID,c.Monthly_Income,c.Credit_Score,
       a.Account_Type,ROUND(a.Current_Balance,2) AS Account_Balance,
       CASE
         WHEN c.Credit_Score>=720 AND a.Current_Balance>=300000
           THEN 'Premium Credit Card'
         WHEN c.Credit_Score>=680 AND a.Current_Balance>=200000
           THEN 'Credit Card'
         WHEN c.Monthly_Income>=60000 AND a.Current_Balance>=100000
           THEN 'Investment Product'
         WHEN c.Monthly_Income>=45000 AND c.Credit_Score>=650
           THEN 'Personal Loan'
         ELSE 'Savings Account'
       END AS Recommended_Product
FROM customers c JOIN accounts a ON c.Customer_ID=a.Customer_ID
LIMIT 20;

SELECT Recommended_Product,COUNT(*) AS Customer_Count
FROM (
    SELECT c.Customer_ID,
           CASE
             WHEN c.Credit_Score>=720 AND a.Current_Balance>=300000
               THEN 'Premium Credit Card'
             WHEN c.Credit_Score>=680 AND a.Current_Balance>=200000
               THEN 'Credit Card'
             WHEN c.Monthly_Income>=60000 AND a.Current_Balance>=100000
               THEN 'Investment Product'
             WHEN c.Monthly_Income>=45000 AND c.Credit_Score>=650
               THEN 'Personal Loan'
             ELSE 'Savings Account'
           END AS Recommended_Product
    FROM customers c JOIN accounts a ON c.Customer_ID=a.Customer_ID
) recommendations
GROUP BY Recommended_Product
ORDER BY Customer_Count DESC;

-- 12. BRANCH-WISE PRODUCT RECOMMENDATIONS
SELECT c.Branch_ID,b.Branch_Name,
       CASE
         WHEN c.Credit_Score>=720 AND a.Current_Balance>=300000
           THEN 'Premium Credit Card'
         WHEN c.Credit_Score>=680 AND a.Current_Balance>=200000
           THEN 'Credit Card'
         WHEN c.Monthly_Income>=60000 AND a.Current_Balance>=100000
           THEN 'Investment Product'
         WHEN c.Monthly_Income>=45000 AND c.Credit_Score>=650
           THEN 'Personal Loan'
         ELSE 'Savings Account'
       END AS Recommended_Product,
       COUNT(*) AS Customer_Count
FROM customers c
JOIN accounts a ON c.Customer_ID=a.Customer_ID
JOIN branches b ON c.Branch_ID=b.Branch_ID
GROUP BY c.Branch_ID,b.Branch_Name,Recommended_Product
ORDER BY c.Branch_ID,Customer_Count DESC;

-- 13. FINAL BUSINESS QUERIES
SELECT Account_ID,Customer_ID,Branch_ID,Account_Type,
       ROUND(Current_Balance,2) AS Current_Balance,Account_Status
FROM accounts ORDER BY Current_Balance DESC LIMIT 20;

SELECT c.Customer_ID,c.Name,c.Branch_ID,
       COUNT(t.Transaction_ID) AS Transaction_Count,
       ROUND(SUM(t.Amount),2) AS Total_Transaction_Value
FROM customers c JOIN transactions t ON c.Customer_ID=t.Customer_ID
GROUP BY c.Customer_ID,c.Name,c.Branch_ID
ORDER BY Total_Transaction_Value DESC LIMIT 20;

SELECT c.Customer_ID,c.Name,c.Branch_ID,
       COUNT(l.Loan_ID) AS Loan_Count,
       ROUND(SUM(l.Loan_Amount),2) AS Total_Loan_Amount,
       SUM(l.Default_Flag) AS Default_Count
FROM customers c JOIN loans l ON c.Customer_ID=l.Customer_ID
GROUP BY c.Customer_ID,c.Name,c.Branch_ID
ORDER BY Total_Loan_Amount DESC LIMIT 20;

-- END OF NEXORA BANK SQL ANALYSIS
