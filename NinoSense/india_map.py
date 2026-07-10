import json
import os
import folium

# -----------------------------
# Load India Risk Data
# -----------------------------
with open("data/india_risk.json", "r", encoding="utf-8") as f:
    india_data = json.load(f)

# -----------------------------
# Coordinates of States / UTs
# -----------------------------
state_coords = {
    "Andhra Pradesh": [15.9129, 79.7400],
    "Arunachal Pradesh": [28.2180, 94.7278],
    "Assam": [26.2006, 92.9376],
    "Bihar": [25.0961, 85.3131],
    "Chhattisgarh": [21.2787, 81.8661],
    "Goa": [15.2993, 74.1240],
    "Gujarat": [22.2587, 71.1924],
    "Haryana": [29.0588, 76.0856],
    "Himachal Pradesh": [31.1048, 77.1734],
    "Jharkhand": [23.6102, 85.2799],
    "Karnataka": [15.3173, 75.7139],
    "Kerala": [10.8505, 76.2711],
    "Madhya Pradesh": [22.9734, 78.6569],
    "Maharashtra": [19.7515, 75.7139],
    "Manipur": [24.6637, 93.9063],
    "Meghalaya": [25.4670, 91.3662],
    "Mizoram": [23.1645, 92.9376],
    "Nagaland": [26.1584, 94.5624],
    "Odisha": [20.9517, 85.0985],
    "Punjab": [31.1471, 75.3412],
    "Rajasthan": [27.0238, 74.2179],
    "Sikkim": [27.5330, 88.5122],
    "Tamil Nadu": [11.1271, 78.6569],
    "Telangana": [18.1124, 79.0193],
    "Tripura": [23.9408, 91.9882],
    "Uttar Pradesh": [26.8467, 80.9462],
    "Uttarakhand": [30.0668, 79.0193],
    "West Bengal": [22.9868, 87.8550],
    "Andaman and Nicobar Islands": [11.7401, 92.6586],
    "Chandigarh": [30.7333, 76.7794],
    "Dadra and Nagar Haveli and Daman and Diu": [20.1809, 73.0169],
    "Delhi": [28.7041, 77.1025],
    "Jammu and Kashmir": [33.7782, 76.5762],
    "Ladakh": [34.1526, 77.5771],
    "Lakshadweep": [10.5667, 72.6417],
    "Puducherry": [11.9416, 79.8083]
}

# -----------------------------
# Create Map
# -----------------------------
india_map = folium.Map(
    location=[22.5, 80],
    zoom_start=5,
    tiles="OpenStreetMap"
)

# -----------------------------
# Risk Color
# -----------------------------
def risk_color(risk):
    if risk == "High":
        return "red"
    elif risk == "Medium":
        return "orange"
    return "green"

# -----------------------------
# Add Markers
# -----------------------------
for state, info in india_data.items():

    if state not in state_coords:
        continue

    cities_data = info.get("cities", [])
    if isinstance(cities_data, dict):
        cities = ", ".join(cities_data.keys())
    elif isinstance(cities_data, list):
        cities = ", ".join(cities_data)
    else:
        cities = "Not available"

    effects = "<br>".join("• " + e for e in info.get("effects", []))

    popup = f"""
    <h3>{state}</h3>

    <b>Risk Level:</b> {info.get("risk", "Unknown")}<br><br>

    <b>Forecast ONI:</b> {info.get("forecast_oni", "N/A")}<br><br>

    <b>Expected Effects:</b><br>
    {effects}

    <br><br>

    <b>Major Cities:</b><br>
    {cities}
    """

    folium.CircleMarker(
        location=state_coords[state],
        radius=10,
        color=risk_color(info["risk"]),
        fill=True,
        fill_color=risk_color(info["risk"]),
        fill_opacity=0.8,
        tooltip=state,
        popup=folium.Popup(popup, max_width=350)
    ).add_to(india_map)

# -----------------------------
# Legend
# -----------------------------
legend = """
<div style="
position: fixed;
bottom: 40px;
left: 40px;
z-index:9999;
background:white;
padding:10px;
border:2px solid black;
border-radius:8px;
">

<b>Risk Levels</b><br>
🔴 High<br>
🟠 Medium<br>
🟢 Low

</div>
"""

india_map.get_root().html.add_child(folium.Element(legend))

# -----------------------------
# Save Map
# -----------------------------
os.makedirs("static/maps", exist_ok=True)

output_file = "static/maps/india_map.html"
india_map.save(output_file)

print("===================================")
print("India Map Generated Successfully")
print(f"Saved to: {output_file}")
print("===================================")