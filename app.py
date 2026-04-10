import streamlit as st
import pandas as pd
import yfinance as yf

# Title of the app
st.title("ENGIE Stock Analysis Dashboard")

# Download stock data
ticker = "ENGI.PA"  # ENGIE ticker symbol
data = yf.download(ticker, start="2020-01-01", end="2026-04-10")

# Display the data
st.subheader("Stock Data")
st.line_chart(data['Close'])

# Display basic statistics
st.subheader("Basic Statistics")
st.write(data.describe())