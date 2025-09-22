import streamlit as st
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# -------------------------------
# API Key
# -------------------------------
ALPHA_VANTAGE_API_KEY = "Q84FUKMKA4UETESI"  # <-- Replace with your key

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Ultimate Stock Dashboard", layout="wide")
st.title("📊 Ultimate Real-Time Stock Monitoring Dashboard")

# -------------------------------
# Sidebar Settings
# -------------------------------
st.sidebar.header("Settings")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 15, 60, 30)

# Auto-refresh
st_autorefresh(interval=refresh_interval*1000, key="autorefresh")

# -------------------------------
# Initialize session state for alerts
# -------------------------------
if "alerts" not in st.session_state:
    st.session_state.alerts = []  # List of dicts: {'symbol':..., 'price':..., 'email':..., 'time':...}

# -------------------------------
# Helper Functions
# -------------------------------
@st.cache_data(ttl=30)
def fetch_stock_data(symbol, interval='1min', outputsize='compact'):
    try:
        ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        data, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize=outputsize)
        data = data.rename(columns={
            '1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume'
        })
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def plot_candlestick(data, symbol):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=symbol
    )])
    fig.update_layout(title=f"{symbol} Live Candlestick Chart",
                      xaxis_title="Time",
                      yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

def check_alerts(symbol, current_price):
    triggered = []
    for alert in st.session_state.alerts:
        if alert['symbol'] == symbol and current_price >= alert['price']:
            triggered.append(alert)
    return triggered

# -------------------------------
# Multi-Tab Layout
# -------------------------------
tabs = st.tabs(["Live Monitor", "Historical Analysis", "Active Alerts"])

# -------------------------------
# Tab 1: Live Monitor
# -------------------------------
with tabs[0]:
    st.subheader("🔴 Live Monitoring")
    stock_symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
    alert_price = st.number_input("Set Alert Price (Optional)", min_value=0.0, value=0.0, step=0.1)
    user_email = st.text_input("Enter Your Email for Alert (Optional)")

    if stock_symbol:
        data = fetch_stock_data(stock_symbol)
        if not data.empty:
            current_price = data['Close'][-1]
            st.metric(label=f"{stock_symbol} Current Price", value=f"${current_price:.2f}")
            plot_candlestick(data, stock_symbol)

            # Add alert to session state
            if st.button("Set Alert"):
                if alert_price > 0:
                    st.session_state.alerts.append({
                        'symbol': stock_symbol,
                        'price': alert_price,
                        'email': user_email,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success(f"Alert set for {stock_symbol} at ${alert_price:.2f}")
                else:
                    st.warning("Please set a valid alert price.")

            # Check triggered alerts
            triggered = check_alerts(stock_symbol, current_price)
            for alert in triggered:
                st.success(f"🚨 {alert['symbol']} reached ${current_price:.2f}! Alert set at ${alert['price']:.2f}")
        else:
            st.warning("No data found for this stock symbol.")

# -------------------------------
# Tab 2: Historical Analysis
# -------------------------------
with tabs[1]:
    st.subheader("📈 Historical Trend Analysis")
    hist_symbol = st.text_input("Enter Stock Symbol for History", "AAPL", key="hist")
    hist_interval = st.selectbox("Interval", ["1min", "5min", "15min", "30min", "60min"])
    hist_outputsize = st.selectbox("Data Size", ["compact", "full"])

    if hist_symbol:
        hist_data = fetch_stock_data(hist_symbol, interval=hist_interval, outputsize=hist_outputsize)
        if not hist_data.empty:
            st.line_chart(hist_data['Close'])
        else:
            st.warning("No historical data found.")

# -------------------------------
# Tab 3: Active Alerts
# -------------------------------
with tabs[2]:
    st.subheader("🚨 Active Alerts")
    if st.session_state.alerts:
        for i, alert in enumerate(st.session_state.alerts):
            st.info(f"{i+1}. {alert['symbol']} | Target: ${alert['price']} | Email: {alert['email']} | Set on: {alert['time']}")
        if st.button("Clear All Alerts"):
            st.session_state.alerts = []
            st.success("All alerts cleared!")
    else:
        st.info("No active alerts.")
