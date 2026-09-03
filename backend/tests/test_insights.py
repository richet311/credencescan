from app.services.insights import extract_fields, generate_insights


def test_extract_fields_finds_gross_and_net_income():
    text = "Gross Income: $5000.00\nNet Pay: $3800.00"
    fields = extract_fields(text)
    assert fields["gross_income"] == 5000.00
    assert fields["net_income"] == 3800.00


def test_extract_fields_ignores_unrecognized_text():
    assert extract_fields("Nothing relevant here.") == {}


def test_generate_insights_withholding_rate():
    insights = generate_insights({"gross_income": 5000.0, "net_income": 3800.0})
    assert any("24.0%" in insight for insight in insights)


def test_generate_insights_savings_rate():
    insights = generate_insights({"net_income": 4000.0, "total_expenses": 3000.0})
    assert any("25.0%" in insight for insight in insights)


def test_generate_insights_overspending_warning():
    insights = generate_insights({"net_income": 2000.0, "total_expenses": 2500.0})
    assert any("exceed" in insight for insight in insights)


def test_generate_insights_fallback_when_no_fields():
    insights = generate_insights({})
    assert "Not enough recognizable fields" in insights[0]
