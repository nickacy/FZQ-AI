from fzq_ai_agent.pipeline.daily_brief import daily_brief_main
from fzq_ai_agent.pipeline.bias_scoring import score_items_for_date
from fzq_ai_agent.pipeline.run_daily import run_for_date
from fzq_ai_agent.report.pdf_report import generate_daily_pdf

date = "2026-05-06"

print("=== Bias Scoring ===")
score_items_for_date(date)

print("=== Daily Brief ===")
print(daily_brief_main(date))

print("=== Run Daily ===")
run_for_date(date)

print("=== PDF Export ===")
print(generate_daily_pdf(date, "test_report.pdf"))
