from pathlib import Path
import json
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATASET_PATH = BASE_DIR / "dataset" / "noaa_data.csv"
COUNTRY_IMPACTS_PATH = DATA_DIR / "country_impacts.json"
OUTPUT_PATH = DATA_DIR / "india_risk.json"


STATE_BASE_RISKS = {
    "Andhra Pradesh": "Medium",
    "Arunachal Pradesh": "Low",
    "Assam": "Medium",
    "Bihar": "High",
    "Chhattisgarh": "Medium",
    "Goa": "Low",
    "Gujarat": "High",
    "Haryana": "Medium",
    "Himachal Pradesh": "Low",
    "Jharkhand": "Medium",
    "Karnataka": "Medium",
    "Kerala": "High",
    "Madhya Pradesh": "Medium",
    "Maharashtra": "High",
    "Manipur": "Low",
    "Meghalaya": "Low",
    "Mizoram": "Low",
    "Nagaland": "Low",
    "Odisha": "Medium",
    "Punjab": "Medium",
    "Rajasthan": "High",
    "Sikkim": "Low",
    "Tamil Nadu": "High",
    "Telangana": "Medium",
    "Tripura": "Medium",
    "Uttar Pradesh": "High",
    "Uttarakhand": "Medium",
    "West Bengal": "High",
    "Andaman and Nicobar Islands": "Medium",
    "Chandigarh": "Low",
    "Dadra and Nagar Haveli and Daman and Diu": "Medium",
    "Delhi": "High",
    "Jammu and Kashmir": "Medium",
    "Ladakh": "Low",
    "Lakshadweep": "Medium",
    "Puducherry": "Medium",
}


STATE_CITIES = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur"],
    "Arunachal Pradesh": ["Itanagar", "Pasighat", "Tawang"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Chhattisgarh": ["Raipur", "Bilaspur", "Bhilai"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Haryana": ["Gurugram", "Faridabad", "Chandigarh"],
    "Himachal Pradesh": ["Shimla", "Dharamshala", "Manali"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Manipur": ["Imphal", "Bishnupur", "Thoubal"],
    "Meghalaya": ["Shillong", "Tura", "Jowai"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
    "Sikkim": ["Gangtok", "Namchi", "Mangan"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Nainital"],
    "West Bengal": ["Kolkata", "Durgapur", "Howrah"],
    "Andaman and Nicobar Islands": ["Port Blair"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Silvassa"],
    "Delhi": ["Delhi"],
    "Jammu and Kashmir": ["Srinagar", "Jammu"],
    "Ladakh": ["Leh", "Kargil"],
    "Lakshadweep": ["Kavaratti"],
    "Puducherry": ["Pondicherry"],
}


def el_nino_strength(oni: float) -> str:
    if oni < 0.5:
        return "Neutral"
    if oni < 1.0:
        return "Weak El Niño"
    if oni < 1.5:
        return "Moderate El Niño"
    if oni < 2.0:
        return "Strong El Niño"
    return "Very Strong El Niño"


def calculate_risk(base_risk: str, oni: float) -> str:
    if oni >= 2.0:
        return "High"
    if oni >= 1.5:
        return "High" if base_risk != "Low" else "Medium"
    if oni >= 1.0:
        return "Medium" if base_risk == "High" else "Low"
    return "Low"


def main() -> None:
    df = pd.read_csv(DATASET_PATH)
    oni_values = df["Value"]

    model = ARIMA(oni_values, order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=6)
    future_oni = float(max(forecast))

    strength = el_nino_strength(future_oni)

    with open(COUNTRY_IMPACTS_PATH, "r", encoding="utf-8") as file:
        country_impacts = json.load(file)

    india_info = country_impacts.get("India", {})

    state_results = {}
    for state, base_risk in STATE_BASE_RISKS.items():
        state_results[state] = {
            "cities": STATE_CITIES.get(state, [state]),
            "effects": [
                f"{state} is affected by El Niño driven rainfall shifts",
                f"Agricultural stress may increase under {strength.lower()}",
                "Water resource planning should be strengthened",
            ],
            "risk": calculate_risk(base_risk, future_oni),
            "forecast_oni": round(future_oni, 2),
            "condition": strength,
            "national_context": india_info.get("effects", []),
        }

    DATA_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(state_results, file, indent=4)

    print("✅ India risk data generated successfully")
    print(f"Saved: {OUTPUT_PATH}")
    print(f"Forecast ONI: {future_oni:.2f}")
    print(f"Condition: {strength}")


if __name__ == "__main__":
    main()
