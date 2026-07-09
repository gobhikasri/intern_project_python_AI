import json
import os
import folium


# -----------------------------
# Load India Risk Data
# -----------------------------

with open(
    "data/india_risk.json",
    "r",
    encoding="utf-8"
) as f:

    india_data = json.load(f)


# -----------------------------
# State Coordinates
# -----------------------------

state_coords = {

    "Andhra Pradesh":[15.9129,79.7400],
    "Arunachal Pradesh":[28.2180,94.7278],
    "Assam":[26.2006,92.9376],
    "Bihar":[25.0961,85.3131],
    "Chhattisgarh":[21.2787,81.8661],
    "Goa":[15.2993,74.1240],
    "Gujarat":[22.2587,71.1924],
    "Haryana":[29.0588,76.0856],
    "Himachal Pradesh":[31.1048,77.1734],
    "Jharkhand":[23.6102,85.2799],
    "Karnataka":[15.3173,75.7139],
    "Kerala":[10.8505,76.2711],
    "Madhya Pradesh":[22.9734,78.6569],
    "Maharashtra":[19.7515,75.7139],
    "Manipur":[24.6637,93.9063],
    "Meghalaya":[25.4670,91.3662],
    "Mizoram":[23.1645,92.9376],
    "Nagaland":[26.1584,94.5624],
    "Odisha":[20.9517,85.0985],
    "Punjab":[31.1471,75.3412],
    "Rajasthan":[27.0238,74.2179],
    "Sikkim":[27.5330,88.5122],
    "Tamil Nadu":[11.1271,78.6569],
    "Telangana":[18.1124,79.0193],
    "Tripura":[23.9408,91.9882],
    "Uttar Pradesh":[26.8467,80.9462],
    "Uttarakhand":[30.0668,79.0193],
    "West Bengal":[22.9868,87.8550],
    "Andaman and Nicobar Islands":[11.7401,92.6586],
    "Chandigarh":[30.7333,76.7794],
    "Dadra and Nagar Haveli and Daman and Diu":[20.1809,73.0169],
    "Delhi":[28.7041,77.1025],
    "Jammu and Kashmir":[33.7782,76.5762],
    "Ladakh":[34.1526,77.5771],
    "Lakshadweep":[10.5667,72.6417],
    "Puducherry":[11.9416,79.8083]
}


# -----------------------------
# Map Setup
# -----------------------------

india_map = folium.Map(
    location=[22.5, 80],
    zoom_start=5,
    tiles="OpenStreetMap"
)


# -----------------------------
# Risk Color Function
# -----------------------------

def get_color(risk):

    if risk == "High":
        return "red"

    elif risk == "Medium":
        return "orange"

    return "green"


# -----------------------------
# Add State Markers
# -----------------------------

for state, info in india_data.items():

    if state not in state_coords:
        continue

    cities = list(info["cities"].keys())

    effects_html = ""

    for effect in info["effects"]:

        effects_html += f"<li>{effect}</li>"

    popup_html = f"""
    <div style="width:300px">

    <h3>🇮🇳 {state}</h3>

    <b>Risk Level:</b>
    {info['risk']}

    <br><br>

    <b>Forecast ONI:</b>
    {info['forecast_oni']}

    <br><br>

    <b>Expected Effects:</b>

    <ul>
    {effects_html}
    </ul>

    <b>Major Cities:</b>

    <ul>
    """

    for city in cities:

        popup_html += f"<li>{city}</li>"

    popup_html += """
    </ul>

    </div>
    """

    folium.CircleMarker(

        location=state_coords[state],

        radius=10,

        color=get_color(info["risk"]),

        fill=True,

        fill_color=get_color(info["risk"]),

        fill_opacity=0.8,

        tooltip=state,

        popup=folium.Popup(
            popup_html,
            max_width=350
        )

    ).add_to(india_map)


# -----------------------------
# Add Legend
# -----------------------------

legend_html = """
<div style="
position: fixed;
bottom: 50px;
left: 50px;
z-index:9999;
background:white;
padding:10px;
border:2px solid grey;
border-radius:8px;
font-size:14px;
">

<b>Risk Levels</b><br>

🔴 High Risk<br>
🟠 Medium Risk<br>
🟢 Low Risk

</div>
"""

india_map.get_root().html.add_child(
    folium.Element(legend_html)
)


# -----------------------------
# Save Map
# -----------------------------

os.makedirs(
    "static/maps",
    exist_ok=True
)

india_map.save(
    "static/maps/india_map.html"
)

print("✅ India Risk Map Created Successfully")
print("Saved: static/maps/india_map.html")