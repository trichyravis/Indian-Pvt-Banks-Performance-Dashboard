# Indian Private Banks Performance Analytics

A classroom-ready Streamlit application comparing ICICI Bank, HDFC Bank, Axis Bank,
Kotak Mahindra Bank and Yes Bank. It provides five-year annual trends, a dedicated
Q1 FY2027 tab for the quarter ended 30 June 2026, asset-quality analysis, live NSE
market performance and Excel/CSV downloads.

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

