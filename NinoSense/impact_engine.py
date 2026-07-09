import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

# Load NOAA ONI dataset
df = pd.read_csv("dataset/noaa_data.csv")

# Train ARIMA model
model = ARIMA(df["Value"], order=(5, 1, 0))
model_fit = model.fit()

# Forecast next 6 periods
forecast = model_fit.forecast(steps=6)

# Get highest forecasted ONI value
max_forecast_oni = max(forecast)

print("\n===== EL NIÑO IMPACT ASSESSMENT =====\n")
print(f"Maximum Forecasted ONI: {max_forecast_oni:.2f}\n")


# Determine El Niño strength
def get_strength(oni):
    if oni < 0.5:
        return "Neutral"
    elif oni < 1.0:
        return "Weak El Niño"
    elif oni < 1.5:
        return "Moderate El Niño"
    elif oni < 2.0:
        return "Strong El Niño"
    else:
        return "Very Strong El Niño"


strength = get_strength(max_forecast_oni)

print(f"Predicted Event Strength: {strength}\n")


# Regional impact database
impacts = {
    "India": [
        "Reduced southwest monsoon rainfall",
        "Drought risk in some regions",
        "Above-normal temperatures"
    ],

    "Australia": [
        "Dry conditions",
        "Bushfire risk",
        "Water scarcity"
    ],

    "Peru": [
        "Heavy rainfall",
        "Flooding risk",
        "Landslide risk"
    ],

    "Indonesia": [
        "Reduced rainfall",
        "Agricultural stress",
        "Forest fire risk"
    ],

    "Southern USA": [
        "Wetter-than-normal winter",
        "Localized flooding risk"
    ]
}

print("===== REGIONAL IMPACTS =====\n")

for region, effects in impacts.items():

    print(f"{region}")
    print("-" * len(region))

    for effect in effects:
        print(f"• {effect}")

    print()