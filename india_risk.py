import json
import os


# -----------------------------------
# Forecasted ONI Value
# -----------------------------------

forecast_oni = 1.8


# -----------------------------------
# Risk Calculation
# -----------------------------------

def calculate_risk(base_risk, oni):

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

    return "Low"


# -----------------------------------
# Effects Database
# -----------------------------------

risk_effects = {

    "High": [
        "Heatwave risk",
        "Reduced rainfall",
        "Drought possibility",
        "Water shortage risk",
        "Agricultural stress"
    ],

    "Medium": [
        "Rainfall variability",
        "Above normal temperatures",
        "Crop yield fluctuations",
        "Localized dry spells"
    ],

    "Low": [
        "Minor climate impacts",
        "Near normal rainfall",
        "Low drought risk"
    ]
}


# -----------------------------------
# Load States Data
# -----------------------------------

with open(
    "data/india_states.json",
    "r",
    encoding="utf-8"
) as f:

    states = json.load(f)


# -----------------------------------
# Generate State & City Risks
# -----------------------------------

results = {}

for state, data in states.items():

    state_risk = calculate_risk(
        data["base_risk"],
        forecast_oni
    )

    results[state] = {

        "risk": state_risk,

        "forecast_oni": forecast_oni,

        "effects": risk_effects[state_risk],

        "cities": {}
    }

    for city in data["cities"]:

        results[state]["cities"][city] = {

            "risk": state_risk,

            "forecast_oni": forecast_oni,

            "effects": risk_effects[state_risk]
        }


# -----------------------------------
# Save JSON
# -----------------------------------

os.makedirs(
    "data",
    exist_ok=True
)

with open(
    "data/india_risk.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=4
    )


print("✅ India Risk Data Generated Successfully")
print("Saved: data/india_risk.json")