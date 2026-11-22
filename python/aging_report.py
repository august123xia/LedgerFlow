from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"


def get_aging_bucket(days):
    if days < 0:
        return "Not due"
    elif days <= 30:
        return "0-30 days"
    elif days <= 60:
        return "31-60 days"
    elif days <= 90:
        return "61-90 days"
    else:
        return "90+ days"


def build_aging_reports(report_date, input_path=None):
    input_path = input_path if input_path is not None else DATA_DIR / "invoices.csv"

    df = pd.read_csv(input_path)

    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["due_date"] = pd.to_datetime(df["due_date"])

    report_date = pd.to_datetime(report_date, errors="raise")

    df["days_overdue"] = (report_date - df["due_date"]).dt.days
    df["aging_bucket"] = df["days_overdue"].apply(get_aging_bucket)

    aging_report = df
    unpaid_aging_report = df[df["status"] == "unpaid"]
    overdue_report = df[
        (df["status"] == "unpaid")
        & (df["days_overdue"] > 0)
    ].sort_values("days_overdue", ascending=False)

    overdue_summary_by_bucket = (
        overdue_report
        .groupby("aging_bucket")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    return {
        "aging_report": aging_report,
        "unpaid_aging_report": unpaid_aging_report,
        "overdue_report": overdue_report,
        "overdue_summary_by_bucket": overdue_summary_by_bucket,
    }


def generate_aging_reports(report_date="2026-09-16"):
    reports = build_aging_reports(report_date)
    OUTPUT_DIR.mkdir(exist_ok=True)
    aging_report = reports["aging_report"]
    unpaid_aging_report = reports["unpaid_aging_report"]
    overdue_report = reports["overdue_report"]
    overdue_summary_by_bucket = reports["overdue_summary_by_bucket"]

    aging_report.to_csv(OUTPUT_DIR / "aging_report.csv", index=False)
    unpaid_aging_report.to_csv(OUTPUT_DIR / "unpaid_aging_report.csv", index=False)
    overdue_report.to_csv(OUTPUT_DIR / "overdue_report.csv", index=False)
    overdue_summary_by_bucket.to_csv(
        OUTPUT_DIR / "overdue_summary_by_bucket.csv",
        index=False
    )

    print("Aging reports generated successfully.")
    print("Output files:")
    print("- outputs/aging_report.csv")
    print("- outputs/unpaid_aging_report.csv")
    print("- outputs/overdue_report.csv")
    print("- outputs/overdue_summary_by_bucket.csv")


if __name__ == "__main__":
    generate_aging_reports()