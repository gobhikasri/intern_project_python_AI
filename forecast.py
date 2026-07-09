import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("dataset/noaa_data.csv")

# ONI values
data = df["Value"]

# Train ARIMA model
model = ARIMA(data, order=(5,1,0))
model_fit = model.fit()

# Forecast next 12 periods
forecast = model_fit.forecast(steps=12)

print("\nNext 12 Forecasted ONI Values:\n")
print(forecast)

# Plot
plt.figure(figsize=(12,6))

plt.plot(data, label="Historical ONI")
plt.plot(
    range(len(data), len(data)+12),
    forecast,
    label="Forecast ONI"
)

plt.legend()
plt.title("ONI Forecast")
plt.xlabel("Time")
plt.ylabel("ONI Value")

plt.show()