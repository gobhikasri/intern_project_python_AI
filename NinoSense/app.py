from flask import Flask, render_template
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from dateutil.relativedelta import relativedelta
from weather_api import get_weather

app = Flask(__name__)


# Risk classification
def classify_risk(oni):
    if oni < 0.5:
        return "LOW RISK"
    elif oni <= 1.5:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"


def get_dashboard_context(city="Chennai"):
    df = pd.read_csv("dataset/noaa_data.csv")
    current_oni = round(df["Value"].iloc[-1], 2)

    model = ARIMA(df["Value"], order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=6)

    forecast_data = []
    high_risk_found = False
    current_date = datetime.now()

    for i, value in enumerate(forecast, start=1):
        future_date = current_date + relativedelta(months=i)
        risk = classify_risk(value)
        if risk == "HIGH RISK":
            high_risk_found = True
        forecast_data.append({
            "date": future_date.strftime("%b %Y"),
            "oni": round(float(value), 2),
            "risk": risk,
        })

    overall_alert = (
        "⚠️ EL NIÑO WARNING DETECTED"
        if high_risk_found
        else "✅ NO MAJOR EL NIÑO WARNING"
    )

    weather = get_weather(city)

    return {
        "weather": weather,
        "current_oni": current_oni,
        "forecast_data": forecast_data,
        "overall_alert": overall_alert,
    }


@app.route("/")
@app.route("/dashboard")
def dashboard():
    context = get_dashboard_context()

    return render_template(
        "dashboard.html",
        weather=context["weather"],
        current_oni=context["current_oni"],
        forecast_data=context["forecast_data"],
        overall_alert=context["overall_alert"],
    )


@app.route("/map")
def climate_map():
    return render_template("map.html")


@app.route("/india-map")
def india_map():
    return render_template("india_map.html")


@app.route("/weather/<city>")
def weather(city):
    weather_data = get_weather(city)

    return render_template(
        "weather.html",
        weather=weather_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
