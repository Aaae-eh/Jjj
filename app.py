import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="ENGIE Stock Dashboard", layout="wide")

st.title("📊 ENGIE Stock Analysis Dashboard")
st.markdown("Real-time technical analysis for ENGIE (ENGI.PA)")

# Sidebar settings
st.sidebar.markdown("### ⚙️ Settings")
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y"], index=2)

# Load data
ticker = "ENGI.PA"

@st.cache_data(ttl=3600)
def load_stock_data(ticker, period):
    data = yf.download(ticker, period=period, progress=False)
    return data.dropna() if data is not None else None

try:
    data = load_stock_data(ticker, period)
    
    if data is None or len(data) < 14:
        st.warning("⚠️ Unable to fetch stock data. Markets may be closed.")
        st.stop()
    
    # Calculate indicators
    def compute_rsi(series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    data["RSI"] = compute_rsi(data["Close"], 14)
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    
    last_price = data["Close"].iloc[-1]
    last_rsi = data["RSI"].iloc[-1]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"€{last_price:.2f}")
    col2.metric("RSI", f"{last_rsi:.1f}")
    col3.metric("High", f"€{data['Close'].max():.2f}")
    col4.metric("Low", f"€{data['Close'].min():.2f}")
    
    # Signal
    st.markdown("---")
    if last_rsi < 30:
        st.success("🟢 STRONG BUY")
    elif last_rsi < 40:
        st.success("🟢 BUY")
    elif last_rsi > 70:
        st.error("🔴 STRONG SELL")
    elif last_rsi > 65:
        st.error("🔴 SELL")
    else:
        st.info("🟡 NEUTRAL")
    
    # Price Chart
    st.markdown("### 📈 Price Chart")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Price", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20", line=dict(color="orange", dash="dash")))
    fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50", line=dict(color="red", dash="dash")))
    fig.update_layout(height=400, template="plotly_light", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    # RSI Chart
    st.markdown("### 📊 RSI")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI", line=dict(color="purple")))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(height=300, template="plotly_light", yaxis_range=[0, 100])
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Disclaimer: For info only")

except Exception as e:
    st.error(f"Error: {e}")
