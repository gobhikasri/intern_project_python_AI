import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

# Load NOAA ONI dataset
df = pd.read_csv("dataset/noaa_data.csv")

# ONI values
oni_values = df["Value"]

# Train ARIMA model
model = ARIMA(oni_values, order=(5, 1, 0))
model_fit = model.fit()

# Forecast next 6 periods
forecast = model_fit.forecast(steps=6)

print("\n===== EL NIÑO FORECAST REPORT =====\n")

# Risk classification function
def classify_risk(oni):
    if oni < 0.5:
        return "LOW RISK"
    elif oni <= 1.5:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"

high_risk_found = False

for i, value in enumerate(forecast, start=1):
    risk = classify_risk(value)

    print(f"Forecast Period {i}")
    print(f"Predicted ONI : {value:.2f}")
    print(f"Risk Level    : {risk}")
    print("-" * 35)

    if risk == "HIGH RISK":
        high_risk_found = True

print("\n===== FINAL ASSESSMENT =====")

if high_risk_found:
    print("⚠️ ALERT: Potential El Niño conditions detected.")
else:
    print("✓ No major El Niño warning detected.")