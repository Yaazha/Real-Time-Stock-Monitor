import streamlit as st
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objs as go
import time
from plyer import notification

# -------------------------------
# STREAMLIT APP TITLE & SIDEBAR
# -------------------------------
st.title("📈 Real-Time Stock Price Monitoring with Alpha Vantage")
st.sidebar.header("Settings")

# User input
api_key = st.sidebar.text_input("Enter Alpha Vantage API Key", "")
stock_symbol = st.sidebar.text_input("Enter Stock Symbol", "AAPL").upper()
alert_price = st.sidebar.number_input("Set Price Alert", min_value=0.0, value=0.0, step=0.1)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 15, 60, 30)

# -------------------------------
# FUNCTION TO FETCH DATA
# -------------------------------
def fetch_data(symbol, api_key):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
    data = data.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })
    data.index = pd.to_datetime(data.index)
    return data

# -------------------------------
# FUNCTION TO PLOT DATA
# -------------------------------
def plot_stock(data, symbol):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=symbol))
    fig.update_layout(title=f"{symbol} Live Price Chart", xaxis_title="Time", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# MAIN REAL-TIME LOOP
# -------------------------------
st.subheader(f"Live Stock Price for {stock_symbol}")

if api_key:
    while True:
        try:
            data = fetch_data(stock_symbol, api_key)
            if not data.empty:
                current_price = data['Close'][-1]
                st.metric(label=f"{stock_symbol} Current Price", value=f"${current_price:.2f}")
                plot_stock(data, stock_symbol)

                # Notification
                if alert_price > 0 and current_price >= alert_price:
                    notification.notify(
                        title="Stock Price Alert 🚨",
                        message=f"{stock_symbol} has reached ${current_price:.2f}!",
                        timeout=5
                    )
                    st.success(f"🚨 Alert! {stock_symbol} has reached your target price: ${current_price:.2f}")
            else:
                st.warning("No data found. Check the stock symbol or API key.")
            
            time.sleep(refresh_interval)
        except Exception as e:
            st.error(f"Error: {e}")
            break
else:
    st.warning("Please enter your Alpha Vantage API Key in the sidebar to start monitoring.")
