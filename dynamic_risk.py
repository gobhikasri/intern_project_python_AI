import pandas as pd
import json
import os
from statsmodels.tsa.arima.model import ARIMA


# --------------------------------------
# Load NOAA ONI Dataset
# --------------------------------------

df = pd.read_csv(
    "dataset/noaa_data.csv"
)


oni_values = df["Value"]



# --------------------------------------
# ARIMA Forecast Model
# --------------------------------------

model = ARIMA(
    oni_values,
    order=(5,1,0)
)

model_fit = model.fit()


# Forecast next 6 periods

forecast = model_fit.forecast(
    steps=6
)


# Maximum expected ONI

future_oni = float(
    max(forecast)
)



print("\n===== EL NIÑO FORECAST =====")

print(
    f"Maximum Forecasted ONI: {future_oni:.2f}"
)



# --------------------------------------
# Determine El Niño Strength
# --------------------------------------

def el_nino_strength(oni):

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



strength = el_nino_strength(
    future_oni
)


print(
    "Predicted Condition:",
    strength
)




# --------------------------------------
# Load Country Impact Database
# --------------------------------------

with open(
    "data/country_impacts.json",
    "r"
) as file:

    countries = json.load(file)




# --------------------------------------
# Dynamic Risk Calculation
# --------------------------------------

def calculate_risk(
        base_risk,
        oni
):

    if oni >= 2.0:

        return "High"


    elif oni >= 1.5:

        if base_risk == "Low":
            return "Medium"

        return "High"



    elif oni >= 1.0:

        if base_risk == "High":
            return "Medium"

        return "Low"



    else:

        return "Low"





# --------------------------------------
# Generate Dynamic Country Risk
# --------------------------------------

dynamic_results = {}



for country, data in countries.items():


    new_risk = calculate_risk(

        data["risk"],

        future_oni

    )


    dynamic_results[country] = {


        "region":
        data["region"],


        "risk":
        new_risk,


        "effects":
        data["effects"],


        "forecast_oni":
        round(future_oni,2),


        "condition":
        strength

    }




# --------------------------------------
# Save Dynamic Risk File
# --------------------------------------

os.makedirs(
    "data",
    exist_ok=True
)



with open(
    "data/dynamic_risk.json",
    "w"
) as file:

    json.dump(
        dynamic_results,
        file,
        indent=4
    )



print("\n===== DYNAMIC RISK GENERATED =====")

for country, info in dynamic_results.items():

    print(
        country,
        "→",
        info["risk"]
    )


print(
    "\nSaved: data/dynamic_risk.json"
)