# Indian Private Banks Performance Analytics

A classroom-ready Streamlit application comparing ICICI Bank, HDFC Bank, Axis Bank,
Kotak Mahindra Bank and Yes Bank. It provides five-year annual trends, a featured
**Q1 FY2027 (Apr–Jun 2026)** latest-quarter view, asset-quality analysis, live NSE
market performance and Excel/CSV downloads.

## What's included

- **Executive Dashboard** — latest-quarter spotlight, KPI leaders with year-on-year
  deltas, a **composite 0–100 scorecard** across eight direction-aware metrics, a
  **peer radar chart**, and single-parameter comparison.
- **Q1 FY2027 (Apr–Jun 2026)** — featured second tab for the most recent quarter,
  including an advances-vs-deposits growth comparison.
- **Annual Trends** — five-year trends plus a **CAGR** analysis for headline metrics.
- **NIM, NII & CASA growth** — level and basis-point movement analysis.
- **Asset Quality & Correlations** — NPA trends, CAR-vs-ROA bubble chart, and a
  **correlation heatmap** showing how the ratios move together.
- **Market Performance** — indexed NSE returns, volatility and Sharpe ratio (yfinance).
- **Insights & Glossary** — auto-generated per-bank commentary and a ratio glossary.
- **Downloads & Sources** — formatted Excel, CSVs, a one-page Markdown profile export,
  and a linked source register.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Upload the complete project to a GitHub repository, including `.streamlit` and `data`.
2. In Streamlit Community Cloud, select the repository and set the main file to `app.py`.
3. Deploy. No secrets are required.

## Data maintenance

Financial data is stored in `data/annual_bank_performance.csv` and `data/q1_fy27.csv`.
Update the CSV files for future periods without changing the application code. Keep
the reporting status and source register current. Live market data is obtained through
`yfinance`; the app degrades gracefully if that service is unavailable.

