import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Global Top10 Stocks Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("🌍 Global Top10 Market Cap Stocks Dashboard")
st.caption("최근 1년간 글로벌 시가총액 Top10 기업의 주가 변화")

# 글로벌 시가총액 Top10 (2025 기준)
stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Berkshire Hathaway": "BRK-B"
}

end = datetime.today()
start = end - timedelta(days=365)

@st.cache_data(ttl=3600)
def load_data():
    data = {}

    for name, ticker in stocks.items():
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                progress=False,
                auto_adjust=True
            )

            if len(df) > 0:
                df = df[['Close']]
                df.columns = [name]
                data[name] = df

        except:
            pass

    return pd.concat(data.values(), axis=1)

price_df = load_data()

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

# 시작점을 100으로 정규화
normalized = price_df / price_df.iloc[0] * 100

st.sidebar.header("설정")

selected = st.sidebar.multiselect(
    "기업 선택",
    normalized.columns,
    default=list(normalized.columns)
)

chart_type = st.sidebar.radio(
    "그래프 종류",
    ["수익률 비교 (%)", "실제 주가"]
)

fig = go.Figure()

if chart_type == "수익률 비교 (%)":

    for company in selected:
        fig.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized[company],
                mode="lines",
                name=company,
                line=dict(width=2)
            )
        )

    fig.update_layout(
        title="최근 1년 수익률 비교 (시작=100)",
        xaxis_title="Date",
        yaxis_title="Indexed Price",
        hovermode="x unified",
        template="plotly_white",
        height=700
    )

else:

    for company in selected:
        fig.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df[company],
                mode="lines",
                name=company,
                line=dict(width=2)
            )
        )

    fig.update_layout(
        title="최근 1년 실제 주가",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
        height=700
    )

st.plotly_chart(fig, use_container_width=True)

st.divider()

latest = pd.DataFrame()

latest["현재가"] = price_df.iloc[-1]
latest["1년 수익률(%)"] = (
    (price_df.iloc[-1] / price_df.iloc[0] - 1) * 100
).round(2)

latest = latest.sort_values(
    "1년 수익률(%)",
    ascending=False
)

st.subheader("📊 최근 1년 성과")

st.dataframe(
    latest.style.format({
        "현재가": "{:.2f}",
        "1년 수익률(%)": "{:.2f}%"
    }),
    use_container_width=True
)

winner = latest.index[0]
loser = latest.index[-1]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🏆 최고 수익률",
        winner,
        f"{latest.iloc[0]['1년 수익률(%)']:.2f}%"
    )

with col2:
    st.metric(
        "📉 최저 수익률",
        loser,
        f"{latest.iloc[-1]['1년 수익률(%)']:.2f}%"
    )
