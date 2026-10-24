# Task 2: Exploratory Data Analysis (EDA)

A beginner-friendly, complete Python project that explores a small fictional retail-orders dataset. It demonstrates the five items in the task screenshot: asking questions, inspecting structure and data types, finding patterns/anomalies, checking a hypothesis with statistics and a chart, and spotting data quality problems.

## What you need

- Windows 10 or 11
- Python 3.10 or newer, with **Add Python to PATH** selected during installation
- Internet access for the one-time package installation

## Run it on Windows

1. Extract the ZIP file (if you received this project as a ZIP).
2. Open the extracted `eda_beginner_project` folder in File Explorer.
3. Click the address bar, type `cmd`, and press Enter. This opens Command Prompt in the project folder.
4. Create a virtual environment:

   ```bat
   py -m venv .venv
   ```

5. Activate it:

   ```bat
   .venv\Scripts\activate
   ```

6. Install the libraries:

   ```bat
   python -m pip install -r requirements.txt
   ```

7. Run the analysis:

   ```bat
   python analyze.py
   ```

The first run creates an `outputs` folder containing a cleaned CSV, a text summary, and three PNG charts. Re-running replaces those generated output files. The original sample data in `data\retail_orders.csv` is never changed.

## Questions this project answers

- How many orders and columns are in the file, and what type is each column?
- Are there missing values, duplicate order IDs, invalid dates, or inconsistent category names?
- How do monthly sales and sales by category change over the year?
- Are unusually large orders pulling the average above the typical order value?
- Is average order value different for discounted and non-discounted orders?

## Hypothesis

**H0:** Mean order value is the same for orders with a discount and orders without a discount.

**H1:** Mean order value differs between the two groups.

The script uses Welch's two-sided independent-samples t-test (`alpha = 0.05`) and explains what the p-value means. This checks for an association in this sample; it does not prove that discounts cause order values to change.

## Expected output

The console shows the dataset dimensions, column types, missing-value counts, quality checks, question-by-question findings, the test statistic/p-value, and where the charts were saved. Since the sample data is fixed, the results are repeatable. You should see:

- 120 input rows and 8 columns
- 2 repeated order IDs, 3 rows with at least one missing field, and 2 inconsistent `Home` category labels (spelling/case variants)
- Sales rising into the holiday season, with November the strongest month
- Electronics as the largest sales category
- A high-value order flagged as an outlier by the 1.5 times IQR rule
- A statistical comparison of discounted and non-discounted order values; interpret its reported p-value using 0.05 as the threshold

Minor differences in printed formatting can occur across library versions. The project does not assume the statistical result is causal.

## Files

- `analyze.py` — commented analysis script
- `data\retail_orders.csv` — deterministic fictional dataset with deliberate quality issues
- `requirements.txt` — Python packages needed
- `outputs\` — created when the script runs

## About the sample data

All customer IDs and transactions are fictional and generated for learning. The data intentionally includes missing values, duplicate order IDs, category label inconsistencies, and one unusually high sale so the quality-checking and anomaly sections have something to find. The script reports issues, standardizes category labels, removes duplicate order IDs (keeping the first row), and excludes rows missing required analysis fields before producing the cleaned dataset.


## Interpreting the statistical check

Welch's t-test is used so the two groups do not have to be assumed to have equal variance. The test still assumes independent orders and can be sensitive to unusually large values, so inspect the boxplot and the flagged outliers before drawing a business conclusion. This small fictional sample is for practicing the workflow, not making real decisions.
