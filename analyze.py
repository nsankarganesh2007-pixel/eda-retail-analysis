"""Task 2: Exploratory Data Analysis (EDA)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Save charts to files; no pop-up window is required.
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "retail_orders.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
ALPHA = 0.05


def print_section(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_FILE, parse_dates=["order_date"])

    print_section("1. START WITH QUESTIONS")
    print("We will ask: How does sales change by month and category? Are there data quality problems?")
    print("Does average order value differ between discounted and non-discounted orders?")

    print_section("2. INSPECT STRUCTURE AND DATA TYPES")
    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    print("\nColumn types:\n", df.dtypes.to_string())
    print("\nFirst five rows:\n", df.head().to_string(index=False))
    print("\nNumeric summary:\n", df[["quantity", "unit_price", "discount"]].describe().round(2).to_string())

    print_section("3. CHECK DATA QUALITY")
    missing = df.isna().sum()
    duplicate_ids = int(df["order_id"].duplicated().sum())
    category_labels = sorted(df["category"].dropna().unique().tolist())
    invalid_dates = int(df["order_date"].isna().sum())
    print("Missing values by column:\n", missing.to_string())
    print(f"\nRepeated order IDs after first occurrence: {duplicate_ids}")
    print(f"Invalid/missing order dates: {invalid_dates}")
    print(f"Category labels before standardizing: {category_labels}")

    # Standardize spelling/case before comparing categories.
    cleaned = df.copy()
    cleaned["category"] = cleaned["category"].str.strip().str.title().replace({"Homegoods": "Home"})
    cleaned = cleaned.drop_duplicates(subset="order_id", keep="first")
    required = ["order_id", "order_date", "category", "quantity", "unit_price", "discount"]
    rows_before = len(cleaned)
    cleaned = cleaned.dropna(subset=required).copy()
    cleaned["sales"] = cleaned["quantity"] * cleaned["unit_price"] * (1 - cleaned["discount"])
    cleaned["month"] = cleaned["order_date"].dt.to_period("M").astype(str)
    cleaned["discounted"] = cleaned["discount"] > 0
    print(f"\nRows removed as duplicate IDs: {duplicate_ids}")
    print(f"Rows removed for missing required fields: {rows_before - len(cleaned)}")
    print(f"Rows available for analysis after cleaning: {len(cleaned)}")
    print("Note: data quality issues are reported before cleaning; raw CSV is preserved.")

    print_section("4. FIND TRENDS, PATTERNS, AND ANOMALIES")
    monthly_sales = cleaned.groupby("month")["sales"].sum().sort_index()
    category_sales = cleaned.groupby("category")["sales"].sum().sort_values(ascending=False)
    print(f"Highest-sales month: {monthly_sales.idxmax()} (${monthly_sales.max():,.2f})")
    print(f"Lowest-sales month: {monthly_sales.idxmin()} (${monthly_sales.min():,.2f})")
    print("Sales by category:\n", category_sales.map(lambda x: f"${x:,.2f}").to_string())

    q1, q3 = cleaned["sales"].quantile([0.25, 0.75])
    upper_fence = q3 + 1.5 * (q3 - q1)
    outliers = cleaned.loc[cleaned["sales"] > upper_fence, ["order_id", "sales"]]
    print(f"\nOutlier rule: sales > Q3 + 1.5 times IQR = ${upper_fence:,.2f}")
    if outliers.empty:
        print("No high-sales outliers found by this rule.")
    else:
        print("High-sales orders to review (not automatically errors):\n", outliers.to_string(index=False))

    print_section("5. TEST A SIMPLE HYPOTHESIS")
    group_yes = cleaned.loc[cleaned["discounted"], "sales"]
    group_no = cleaned.loc[~cleaned["discounted"], "sales"]
    test = stats.ttest_ind(group_yes, group_no, equal_var=False, alternative="two-sided")
    print("H0: mean order value is equal for discounted and non-discounted orders.")
    print("H1: the two mean order values differ.")
    print(f"Discounted mean: ${group_yes.mean():,.2f} (n={len(group_yes)})")
    print(f"Non-discounted mean: ${group_no.mean():,.2f} (n={len(group_no)})")
    print(f"Welch t statistic: {test.statistic:.3f} | p-value: {test.pvalue:.4f} | alpha: {ALPHA}")
    if test.pvalue < ALPHA:
        print("Conclusion: reject H0; this sample provides evidence of a difference in group means.")
    else:
        print("Conclusion: do not reject H0; this sample does not provide strong evidence of a difference.")
    print("This is an association in the sample, not proof that discounts cause the difference.")

    print_section("6. SAVE VISUALIZATIONS AND CLEANED DATA")
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly_sales.plot(kind="line", marker="o", color="#2563eb", ax=ax)
    ax.set(title="Monthly sales", xlabel="Month", ylabel="Sales ($)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "monthly_sales.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    category_sales.sort_values().plot(kind="barh", color="#16a085", ax=ax)
    ax.set(title="Sales by category", xlabel="Sales ($)", ylabel="Category")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sales_by_category.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.boxplot([group_no, group_yes], tick_labels=["No discount", "Discount"], showmeans=True)
    ax.set(title="Order sales by discount status", ylabel="Order sales ($)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "discount_comparison.png", dpi=150)
    plt.close(fig)

    cleaned.drop(columns=["month", "discounted"]).to_csv(OUTPUT_DIR / "cleaned_retail_orders.csv", index=False)
    summary = [
        "EDA SUMMARY", f"Input rows: {len(df)}", f"Rows after cleaning: {len(cleaned)}",
        f"Duplicate order IDs removed: {duplicate_ids}", f"Highest-sales month: {monthly_sales.idxmax()}",
        f"Highest-sales category: {category_sales.idxmax()}", f"Discount comparison p-value: {test.pvalue:.4f}",
        f"High-sales outlier count (1.5 times IQR): {len(outliers)}",
    ]
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("Saved: outputs/monthly_sales.png, outputs/sales_by_category.png, outputs/discount_comparison.png")
    print("Saved: outputs/cleaned_retail_orders.csv and outputs/summary.txt")


if __name__ == "__main__":
    main()

