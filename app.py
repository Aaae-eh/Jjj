import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="ENGIE Stock Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-title {
        text-align: center;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 class='header-title'>📊 ENGIE Stock Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Real-time technical analysis for ENGIE (ENGI.PA)</p>", unsafe_allow_html=True)

# ============================================
# SIDEBAR - USER INPUTS
# ============================================
st.sidebar.markdown("### ⚙️ Dashboard Settings")
period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
rsi_period = st.sidebar.slider("RSI Period", min_value=5, max_value=50, value=14)
ma_short = st.sidebar.slider("Short MA (days)", min_value=5, max_value=30, value=20)
ma_long = st.sidebar.slider("Long MA (days)", min_value=30, max_value=200, value=50)

# ============================================
# DATA LOADING
# ============================================
ticker = "ENGI.PA"

@st.cache_data
def load_data(period):
    return yf.download(ticker, period=period, progress=False)

data = load_data(period)

# Calculate Technical Indicators
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data["RSI"] = compute_rsi(data["Close"], rsi_period)
data["MA_Short"] = data["Close"].rolling(ma_short).mean()
data["MA_Long"] = data["Close"].rolling(ma_long).mean()
data["Volume_MA"] = data["Volume"].rolling(20).mean()

# Get Latest Values
last_price = data["Close"].iloc[-1]
prev_price = data["Close"].iloc[-2]
price_change = last_price - prev_price
price_change_pct = (price_change / prev_price) * 100
last_rsi = data["RSI"].iloc[-1]
last_volume = data["Volume"].iloc[-1]

# ============================================
# KEY METRICS - TOP SECTION
# ============================================
st.markdown("### 💰 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Current Price",
        f"€{last_price:.2f}",
        f"{price_change:+.2f} ({price_change_pct:+.2f}%)",
        delta_color="normal"
    )

with col2:
    st.metric(
        "RSI (14)",
        f"{last_rsi:.1f}",
        "Neutral" if 40 <= last_rsi <= 65 else "Overbought" if last_rsi > 65 else "Oversold"
    )

with col3:
    ma_short_val = data["MA_Short"].iloc[-1]
    st.metric(
        f"MA {ma_short}",
        f"€{ma_short_val:.2f}",
        f"{((last_price - ma_short_val) / ma_short_val * 100):+.2f}%"
    )

with col4:
    ma_long_val = data["MA_Long"].iloc[-1]
    st.metric(
        f"MA {ma_long}",
        f"€{ma_long_val:.2f}",
        f"{((last_price - ma_long_val) / ma_long_val * 100):+.2f}%"
    )

with col5:
    st.metric(
        "Volume",
        f"{last_volume/1e6:.1f}M",
        f"Avg: {data['Volume_MA'].iloc[-1]/1e6:.1f}M"
    )

# ============================================
# TRADING SIGNAL
# ============================================
st.markdown("---")
signal = "🟡 NEUTRAL"
signal_explanation = "RSI is in normal range (40-65)"

if last_rsi < 30:
    signal = "🟢 STRONG BUY"
    signal_explanation = "RSI < 30 (Oversold) - Strong buying opportunity"
elif last_rsi < 40:
    signal = "🟢 BUY"
    signal_explanation = "RSI < 40 (Oversold) - Potential buying opportunity"
elif last_rsi > 70:
    signal = "🔴 STRONG SELL"
    signal_explanation = "RSI > 70 (Overbought) - Strong selling signal"
elif last_rsi > 65:
    signal = "🔴 SELL"
    signal_explanation = "RSI > 65 (Overbought) - Potential selling signal"

st.markdown(f"<h3 style='text-align: center; color: #ff6b6b;'>{signal}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>{signal_explanation}</p>", unsafe_allow_html=True)

# ============================================
# PRICE CHART WITH MOVING AVERAGES
# ============================================
st.markdown("### 📈 Price Chart & Moving Averages")

fig_price = go.Figure()

fig_price.add_trace(go.Scatter(
    x=data.index, y=data["Close"],
    mode='lines', name='Price',
    line=dict(color='#1f77b4', width=2)
))

fig_price.add_trace(go.Scatter(
    x=data.index, y=data["MA_Short"],
    mode='lines', name=f'MA {ma_short}',
    line=dict(color='#ff7f0e', width=2, dash='dash')
))

fig_price.add_trace(go.Scatter(
    x=data.index, y=data["MA_Long"],
    mode='lines', name=f'MA {ma_long}',
    line=dict(color='#d62728', width=2, dash='dash')
))

fig_price.update_layout(
    title="",
    xaxis_title="Date",
    yaxis_title="Price (€)",
    hovermode='x unified',
    height=400,
    template='plotly_light'
)

st.plotly_chart(fig_price, use_container_width=True)

# ============================================
# RSI CHART
# ============================================
st.markdown("### 📊 RSI (Relative Strength Index)")

fig_rsi = go.Figure()

fig_rsi.add_trace(go.Scatter(
    x=data.index, y=data["RSI"],
    mode='lines', name='RSI',
    line=dict(color='#9467bd', width=2),
    fill='tozeroy'
))

# Add overbought/oversold zones
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")

fig_rsi.update_layout(
    title="",
    xaxis_title="Date",
    yaxis_title="RSI",
    hovermode='x unified',
    height=300,
    template='plotly_light',
    yaxis=dict(range=[0, 100])
)

st.plotly_chart(fig_rsi, use_container_width=True)

# ============================================
# VOLUME CHART
# ============================================
st.markdown("### 📊 Trading Volume")

fig_volume = go.Figure()

colors = ['green' if data["Close"].iloc[i] >= data["Close"].iloc[i-1] else 'red' 
          for i in range(1, len(data))]
colors.insert(0, 'gray')

fig_volume.add_trace(go.Bar(
    x=data.index, y=data["Volume"],
    name='Volume',
    marker_color=colors,
    opacity=0.7
))

fig_volume.add_trace(go.Scatter(
    x=data.index, y=data["Volume_MA"],
    mode='lines', name='20-day MA',
    line=dict(color='blue', width=2)
))

fig_volume.update_layout(
    title="",
    xaxis_title="Date",
    yaxis_title="Volume",
    hovermode='x unified',
    height=300,
    template='plotly_light'
)

st.plotly_chart(fig_volume, use_container_width=True)

# ============================================
# STATISTICS TABLE
# ============================================
st.markdown("### 📋 Detailed Statistics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Price Statistics")
    stats_data = {
        "Metric": ["Current Price", "52-Week High", "52-Week Low", "Average Price", "Price Change (%)"],
        "Value": [
            f"€{last_price:.2f}",
            f"€{data['Close'].max():.2f}",
            f"€{data['Close'].min():.2f}",
            f"€{data['Close'].mean():.2f}",
            f"{price_change_pct:+.2f}%"
        ]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

with col2:
    st.markdown("#### Technical Indicators")
    indicators_data = {
        "Indicator": ["RSI", "MA Short Status", "MA Long Status", "Volatility (%)"],
        "Value": [
            f"{last_rsi:.1f}",
            "Price Above" if last_price > data["MA_Short"].iloc[-1] else "Price Below",
            "Price Above" if last_price > data["MA_Long"].iloc[-1] else "Price Below",
            f"{(data['Close'].std() / data['Close'].mean() * 100):.2f}%"
        ]
    }
    st.dataframe(pd.DataFrame(indicators_data), use_container_width=True, hide_index=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
    <p style='text-align: center; color: gray; font-size: 12px;'>
    📱 Dashboard last updated: 2026-04-10 11:57:57<br>
    ⚠️ Disclaimer: This dashboard is for informational purposes only. Always do your own research before trading.
    </p>
""", unsafe_allow_html=True)