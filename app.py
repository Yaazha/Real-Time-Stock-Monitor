from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

API_KEY = "Q84FUKMKA4UETESI"   # paste your key here

# Initialize Alpha Vantage
ts = TimeSeries(key=API_KEY, output_format='pandas')

# Get daily stock data for Apple
data, meta_data = ts.get_daily(symbol="AAPL", outputsize="compact")

print("Latest Stock Data:")
print(data.tail())

# Plot closing price
data['4. close'].plot(title="AAPL Closing Price", figsize=(10,5))
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.show()
