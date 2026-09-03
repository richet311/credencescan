import re

MONEY_PATTERN = re.compile(r"\$?([\d,]+\.\d{2})")

FIELD_KEYWORDS = {
    "gross_income": ["gross income", "gross pay"],
    "net_income": ["net pay", "net income", "take-home"],
    "total_expenses": ["total expenses"],
    "balance": ["balance", "ending balance"],
}

SEARCH_WINDOW = 60


def extract_fields(text: str) -> dict[str, float]:
    lower = text.lower()
    fields: dict[str, float] = {}

    for field, keywords in FIELD_KEYWORDS.items():
        for keyword in keywords:
            idx = lower.find(keyword)
            if idx == -1:
                continue
            window = text[idx : idx + SEARCH_WINDOW]
            match = MONEY_PATTERN.search(window)
            if match:
                fields[field] = float(match.group(1).replace(",", ""))
                break

    return fields


def generate_insights(fields: dict[str, float]) -> list[str]:
    insights = []
    gross = fields.get("gross_income")
    net = fields.get("net_income")
    expenses = fields.get("total_expenses")

    if gross and net:
        withheld = gross - net
        rate = (withheld / gross) * 100
        insights.append(
            f"About {rate:.1f}% of gross income (${withheld:,.2f}) is withheld "
            "between gross and net pay."
        )

    if net and expenses:
        leftover = net - expenses
        if leftover >= 0:
            savings_rate = (leftover / net) * 100
            insights.append(
                f"Estimated savings rate is {savings_rate:.1f}% "
                f"(${leftover:,.2f} left after expenses)."
            )
        else:
            insights.append(
                f"Expenses exceed net income by ${abs(leftover):,.2f}. "
                "Consider reviewing discretionary spending."
            )

    if not insights:
        insights.append(
            "Not enough recognizable fields were found to generate a detailed "
            "insight. Try a document with clearer income/expense labels."
        )

    return insights
