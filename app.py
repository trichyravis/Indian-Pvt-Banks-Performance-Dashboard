from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BANK_COLORS = {
    "ICICI Bank": "#F58220",
    "HDFC Bank": "#004C8F",
    "Axis Bank": "#97144D",
    "Kotak Mahindra Bank": "#ED1C24",
    "Yes Bank": "#005BAA",
}
TICKERS = {
    "ICICI Bank": "ICICIBANK.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Yes Bank": "YESBANK.NS",
}
METRICS = {
    "Net Profit (₹ crore)": ("net_profit_cr", True, "₹{:,.0f} Cr"),
    "Net Interest Income (₹ crore)": ("nii_cr", True, "₹{:,.0f} Cr"),
    "Net Interest Margin (%)": ("nim_pct", True, "{:.2f}%"),
    "Advances (₹ crore)": ("advances_cr", True, "₹{:,.0f} Cr"),
    "Deposits (₹ crore)": ("deposits_cr", True, "₹{:,.0f} Cr"),
    "CASA Ratio (%)": ("casa_pct", True, "{:.2f}%"),
    "Gross NPA (%)": ("gnpa_pct", False, "{:.2f}%"),
    "Net NPA (%)": ("nnpa_pct", False, "{:.2f}%"),
    "Return on Assets (%)": ("roa_pct", True, "{:.2f}%"),
    "Return on Equity (%)": ("roe_pct", True, "{:.2f}%"),
    "Capital Adequacy (%)": ("car_pct", True, "{:.2f}%"),
    "Cost-to-Income (%)": ("cost_income_pct", False, "{:.2f}%"),
}


st.set_page_config(
    page_title="Indian Private Banks | Performance Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#0B2545; --blue:#123B65; --gold:#D4A017; --paper:#F6F8FC; }
        .stApp { background: linear-gradient(180deg,#F7F9FC 0%,#EEF3F8 100%); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#0B2545,#153F69); }
        [data-testid="stSidebar"] * { color:#FFFFFF !important; }
        [data-testid="stSidebar"] .stMultiSelect span,
        [data-testid="stSidebar"] [data-baseweb="select"] * { color:#102A43 !important; }
        .hero { padding:1.65rem 2rem; border-radius:20px; color:white;
          background:linear-gradient(115deg,#081F3A 0%,#124A78 70%,#A97908 150%);
          box-shadow:0 12px 32px rgba(11,37,69,.18); margin-bottom:1rem; }
        .hero h1 { margin:0; font-size:2.05rem; line-height:1.2; color:white; }
        .hero p { margin:.55rem 0 0; color:#E7F0FA; font-size:1rem; }
        .eyebrow { color:#F3C84B; text-transform:uppercase; letter-spacing:.12em;
          font-weight:800; font-size:.75rem; margin-bottom:.55rem; }
        div[data-testid="stMetric"] { background:white; border:1px solid #DCE5EF;
          border-radius:14px; padding:1rem; box-shadow:0 6px 18px rgba(20,50,80,.06); }
        div[data-testid="stMetric"] label { color:#52677D !important; font-weight:700 !important; }
        .stTabs [data-baseweb="tab-list"] { gap:.45rem; background:#DDE7F1; padding:.4rem;
          border-radius:13px; overflow-x:auto; }
        .stTabs [data-baseweb="tab"] { background:#FFFFFF !important; border:1px solid #C8D6E5;
          border-radius:9px !important; color:#102A43 !important; font-weight:750; padding:.55rem 1rem; }
        .stTabs [aria-selected="true"] { background:#0B3B67 !important; color:#FFFFFF !important;
          border-color:#0B3B67 !important; }
        .stButton button, .stDownloadButton button { background:#0B3B67 !important;
          color:white !important; border:1px solid #0B3B67 !important; border-radius:9px !important;
          font-weight:750 !important; }
        .stButton button:hover, .stDownloadButton button:hover { background:#D4A017 !important;
          color:#071A2F !important; border-color:#D4A017 !important; }
        .section-title { font-size:1.3rem; font-weight:850; color:#0B2545; margin:.4rem 0 .65rem; }
        .note { background:#FFF7DD; border-left:5px solid #D4A017; padding:.8rem 1rem;
          border-radius:9px; color:#4A3A0A; }
        .footer { text-align:center; color:#64778B; border-top:1px solid #D7E0EA;
          padding:1.2rem 0 .4rem; margin-top:2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    annual = pd.read_csv(DATA / "annual_bank_performance.csv", parse_dates=["period_end"])
    quarter = pd.read_csv(DATA / "q1_fy27.csv", parse_dates=["period_end"])
    sources = pd.read_csv(DATA / "sources.csv")
    for frame in (annual, quarter):
        numeric = frame.columns.difference(["bank", "period", "period_end", "status"])
        frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="coerce")
    return annual, quarter, sources


def chart_layout(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
        font=dict(family="Arial", color="#233B53"),
        legend_title_text="", hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E7EDF4", zeroline=False)
    return fig


def ranking(frame: pd.DataFrame, column: str, higher_better: bool) -> pd.DataFrame:
    out = frame[["bank", column]].dropna().copy()
    out["Rank"] = out[column].rank(ascending=not higher_better, method="min").astype(int)
    return out.sort_values("Rank")


def workbook_bytes(annual: pd.DataFrame, quarter: pd.DataFrame, sources: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        annual.to_excel(writer, index=False, sheet_name="Annual FY22-FY26")
        quarter.to_excel(writer, index=False, sheet_name="Q1 FY2027")
        sources.to_excel(writer, index=False, sheet_name="Sources")
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            ws.sheet_view.showGridLines = False
            for cell in ws[1]:
                cell.font = __import__("openpyxl").styles.Font(bold=True, color="FFFFFF")
                cell.fill = __import__("openpyxl").styles.PatternFill("solid", fgColor="0B3B67")
            for col in ws.columns:
                letter = col[0].column_letter
                width = min(max(len(str(c.value or "")) for c in col) + 2, 42)
                ws.column_dimensions[letter].width = width
    return output.getvalue()


@st.cache_data(ttl=1800, show_spinner=False)
def market_prices(tickers: tuple[str, ...], start: str, end: str) -> pd.DataFrame:
    try:
        import yfinance as yf
        raw = yf.download(list(tickers), start=start, end=end, auto_adjust=True, progress=False)
        if raw.empty:
            return pd.DataFrame()
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
        if isinstance(close, pd.Series):
            close = close.to_frame(name=tickers[0])
        return close.dropna(how="all")
    except Exception:
        return pd.DataFrame()


inject_css()
annual, quarter, sources = load_data()

st.markdown(
    """<div class="hero"><div class="eyebrow">The Mountain Path Academy · Banking Analytics</div>
    <h1>Performance Analysis of India’s Leading Private Banks</h1>
    <p>ICICI Bank · HDFC Bank · Axis Bank · Kotak Mahindra Bank · Yes Bank</p></div>""",
    unsafe_allow_html=True,
)

all_banks = list(BANK_COLORS)
with st.sidebar:
    st.markdown("## Analysis controls")
    selected = st.multiselect("Banks", all_banks, default=all_banks)
    if not selected:
        st.warning("Select at least one bank.")
        selected = all_banks
    period = st.selectbox("Latest annual snapshot", annual["period"].drop_duplicates().tolist()[::-1])
    st.markdown("---")
    st.caption("Figures in ₹ crore unless otherwise stated. Use the Sources tab before citing the analysis.")

a = annual[annual["bank"].isin(selected)].copy()
q = quarter[quarter["bank"].isin(selected)].copy()
latest = a[a["period"] == period]

tabs = st.tabs([
    "Executive Dashboard", "Annual Trends", "Q1 FY2027 — Jun 2026",
    "Asset Quality", "Market Performance", "Downloads & Sources"
])

with tabs[0]:
    st.markdown('<div class="section-title">Executive performance snapshot</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    profit_leader = ranking(latest, "net_profit_cr", True).iloc[0]
    nim_leader = ranking(latest, "nim_pct", True).iloc[0]
    quality_leader = ranking(latest, "gnpa_pct", False).iloc[0]
    roa_leader = ranking(latest, "roa_pct", True).iloc[0]
    c1.metric("Highest net profit", profit_leader["bank"], f"₹{profit_leader['net_profit_cr']:,.0f} Cr")
    c2.metric("Highest NIM", nim_leader["bank"], f"{nim_leader['nim_pct']:.2f}%")
    c3.metric("Lowest gross NPA", quality_leader["bank"], f"{quality_leader['gnpa_pct']:.2f}%")
    c4.metric("Highest ROA", roa_leader["bank"], f"{roa_leader['roa_pct']:.2f}%")

    metric_label = st.selectbox("Compare parameter", list(METRICS), index=0, key="exec_metric")
    col, higher, fmt = METRICS[metric_label]
    rank = ranking(latest, col, higher)
    fig = px.bar(rank, x="bank", y=col, color="bank", color_discrete_map=BANK_COLORS,
                 text=col, title=f"{metric_label} · {period}")
    fig.update_traces(texttemplate="%{text:,.2f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(chart_layout(fig), use_container_width=True)
    display_rank = rank.rename(columns={"bank": "Bank", col: metric_label})
    st.dataframe(display_rank, hide_index=True, use_container_width=True)

with tabs[1]:
    st.markdown('<div class="section-title">Five-year audited trend analysis</div>', unsafe_allow_html=True)
    metric_label = st.selectbox("Trend parameter", list(METRICS), index=0, key="trend_metric")
    col, _, _ = METRICS[metric_label]
    trend = a.dropna(subset=[col])
    fig = px.line(trend, x="period", y=col, color="bank", markers=True,
                  color_discrete_map=BANK_COLORS, title=f"{metric_label}: FY2022–FY2026")
    st.plotly_chart(chart_layout(fig), use_container_width=True)
    pivot = trend.pivot(index="bank", columns="period", values=col).reset_index()
    st.dataframe(pivot, hide_index=True, use_container_width=True)

with tabs[2]:
    st.markdown('<div class="section-title">Q1 FY2027 · Quarter ended 30 June 2026</div>', unsafe_allow_html=True)
    st.markdown('<div class="note">Quarterly results are unaudited/limited-review figures. Annual and quarterly values are intentionally presented in separate tabs.</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    q_profit = ranking(q, "net_profit_cr", True).iloc[0]
    q_growth = ranking(q, "advances_growth_yoy_pct", True).iloc[0]
    q_nim = ranking(q, "nim_pct", True).iloc[0]
    q_gnpa = ranking(q, "gnpa_pct", False).iloc[0]
    c1.metric("Profit leader", q_profit["bank"], f"₹{q_profit['net_profit_cr']:,.0f} Cr")
    c2.metric("Advances growth leader", q_growth["bank"], f"{q_growth['advances_growth_yoy_pct']:.1f}% YoY")
    c3.metric("NIM leader", q_nim["bank"], f"{q_nim['nim_pct']:.2f}%")
    c4.metric("Lowest GNPA", q_gnpa["bank"], f"{q_gnpa['gnpa_pct']:.2f}%")
    q_options = {
        "Net Profit (₹ crore)": ("net_profit_cr", True), "NII (₹ crore)": ("nii_cr", True),
        "NIM (%)": ("nim_pct", True), "Advances Growth YoY (%)": ("advances_growth_yoy_pct", True),
        "Deposits Growth YoY (%)": ("deposits_growth_yoy_pct", True), "Gross NPA (%)": ("gnpa_pct", False),
        "Net NPA (%)": ("nnpa_pct", False), "ROA (%)": ("roa_pct", True), "ROE (%)": ("roe_pct", True),
        "Provisions (₹ crore)": ("provisions_cr", False),
    }
    q_label = st.selectbox("Quarterly parameter", q_options, key="q_metric")
    q_col, q_high = q_options[q_label]
    q_rank = ranking(q, q_col, q_high)
    fig = px.bar(q_rank, x="bank", y=q_col, color="bank", text=q_col,
                 color_discrete_map=BANK_COLORS, title=f"{q_label} · Q1 FY2027")
    fig.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
    st.plotly_chart(chart_layout(fig), use_container_width=True)
    st.dataframe(q_rank.rename(columns={"bank": "Bank", q_col: q_label}), hide_index=True, use_container_width=True)

with tabs[3]:
    st.markdown('<div class="section-title">Asset quality and capital resilience</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    for container, col, title in [(left, "gnpa_pct", "Gross NPA (%)"), (right, "nnpa_pct", "Net NPA (%)")]:
        fig = px.line(a, x="period", y=col, color="bank", markers=True,
                      color_discrete_map=BANK_COLORS, title=title)
        container.plotly_chart(chart_layout(fig, 390), use_container_width=True)
    fig = px.scatter(latest, x="car_pct", y="roa_pct", size="advances_cr", color="bank",
                     color_discrete_map=BANK_COLORS, hover_name="bank",
                     title=f"Capital adequacy versus return on assets · {period}",
                     labels={"car_pct": "Capital adequacy (%)", "roa_pct": "ROA (%)"})
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with tabs[4]:
    st.markdown('<div class="section-title">NSE shareholder-return analysis</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    start = m1.date_input("Start date", value=pd.Timestamp("2022-04-01"), max_value=pd.Timestamp.today())
    end = m2.date_input("End date", value=pd.Timestamp.today(), max_value=pd.Timestamp.today())
    if start >= end:
        st.error("Start date must be before end date.")
    else:
        ticker_list = tuple(TICKERS[b] for b in selected)
        prices = market_prices(ticker_list, str(start), str(end + pd.Timedelta(days=1)))
        if prices.empty:
            st.warning("Live market data is temporarily unavailable. Financial-analysis tabs remain fully functional.")
        else:
            reverse = {v: k for k, v in TICKERS.items()}
            prices = prices.rename(columns=reverse)
            normalized = prices.div(prices.iloc[0]).mul(100)
            long = normalized.reset_index().melt(id_vars=normalized.index.name or "Date", var_name="Bank", value_name="Indexed value")
            xname = long.columns[0]
            fig = px.line(long, x=xname, y="Indexed value", color="Bank", color_discrete_map=BANK_COLORS,
                          title="Indexed share-price performance (start = 100)")
            st.plotly_chart(chart_layout(fig), use_container_width=True)
            returns = prices.pct_change().dropna()
            summary = pd.DataFrame({
                "Total return (%)": (prices.iloc[-1] / prices.iloc[0] - 1) * 100,
                "Annualised volatility (%)": returns.std() * np.sqrt(252) * 100,
                "Sharpe ratio (RF=0%)": returns.mean() / returns.std() * np.sqrt(252),
            }).replace([np.inf, -np.inf], np.nan).round(2)
            st.dataframe(summary.reset_index(names="Bank"), hide_index=True, use_container_width=True)

with tabs[5]:
    st.markdown('<div class="section-title">Download data and review sources</div>', unsafe_allow_html=True)
    excel = workbook_bytes(a, q, sources)
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download complete Excel", excel, "private_banks_performance.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    d2.download_button("Download annual CSV", a.to_csv(index=False).encode(), "annual_bank_performance.csv",
                       "text/csv", use_container_width=True)
    d3.download_button("Download Q1 FY2027 CSV", q.to_csv(index=False).encode(), "q1_fy27.csv",
                       "text/csv", use_container_width=True)
    st.markdown("#### Data sources")
    st.dataframe(sources, hide_index=True, use_container_width=True, column_config={
        "source_url": st.column_config.LinkColumn("Source link", display_text="Open source")
    })
    st.info("Research note: verify transcribed figures against the linked filings before publication or investment use. Market data may be delayed and is not investment advice.")

st.markdown('<div class="footer"><b>The Mountain Path Academy</b><br>Applied finance through data, Excel and Python · Educational use only</div>', unsafe_allow_html=True)

