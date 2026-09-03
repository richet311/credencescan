import csv
import random
from pathlib import Path

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_PATH = DATA_DIR / "synthetic_documents.csv"

SAMPLES_PER_CLASS = 200


def _money(low: float, high: float) -> float:
    return round(random.uniform(low, high), 2)


def make_pay_stub() -> str:
    gross = _money(2500, 8000)
    deductions = _money(300, gross * 0.35)
    net = round(gross - deductions, 2)
    return (
        f"{fake.company()}\n"
        f"Pay Stub for {fake.name()}\n"
        f"Pay Period: {fake.date_this_year()}\n"
        f"Gross Income: ${gross:,.2f}\n"
        f"Deductions: ${deductions:,.2f}\n"
        f"Net Pay: ${net:,.2f}\n"
        f"Employee ID: {fake.bothify('EMP-####')}\n"
    )


def make_bank_statement() -> str:
    opening = _money(500, 15000)
    deposits = _money(100, 5000)
    withdrawals = _money(100, 4000)
    closing = round(opening + deposits - withdrawals, 2)
    return (
        f"Account Statement\n"
        f"Account Holder: {fake.name()}\n"
        f"Statement Period: {fake.month_name()} {fake.year()}\n"
        f"Opening Balance: ${opening:,.2f}\n"
        f"Total Deposits: ${deposits:,.2f}\n"
        f"Total Withdrawals: ${withdrawals:,.2f}\n"
        f"Balance: ${closing:,.2f}\n"
        f"Account Number: {fake.bothify('####-####-####')}\n"
    )


def make_budget_sheet() -> str:
    income = _money(2500, 7000)
    housing = _money(600, 2200)
    food = _money(150, 900)
    transport = _money(100, 600)
    other = _money(100, 800)
    total_expenses = round(housing + food + transport + other, 2)
    return (
        f"Monthly Budget Sheet\n"
        f"Prepared for: {fake.name()}\n"
        f"Month: {fake.month_name()} {fake.year()}\n"
        f"Net Pay: ${income:,.2f}\n"
        f"Housing: ${housing:,.2f}\n"
        f"Food: ${food:,.2f}\n"
        f"Transportation: ${transport:,.2f}\n"
        f"Other: ${other:,.2f}\n"
        f"Total Expenses: ${total_expenses:,.2f}\n"
    )


GENERATORS = {
    "pay_stub": make_pay_stub,
    "bank_statement": make_bank_statement,
    "budget_sheet": make_budget_sheet,
}


def generate() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for label, generator in GENERATORS.items():
        for _ in range(SAMPLES_PER_CLASS):
            rows.append({"text": generator(), "label": label})

    random.shuffle(rows)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} synthetic documents to {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
