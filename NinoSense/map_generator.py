import folium
import json
import os
import requests


# ---------------------------------------
# Load Dynamic Risk Data
# ---------------------------------------

with open("data/dynamic_risk.json", "r") as file:
    country_data = json.load(file)



# ---------------------------------------
# Country Name Corrections
# ---------------------------------------

country_alias = {

    "United States of America": "United States",
    "Republic of India": "India",
    "Russian Federation": "Russia",
    "Korea": "South Korea",
    "Dem. Rep. Congo": "Democratic Republic of the Congo"

}



# ---------------------------------------
# Download World GeoJSON
# ---------------------------------------

geojson_url = (
    "https://raw.githubusercontent.com/"
    "datasets/geo-countries/master/data/"
    "countries.geojson"
)


response = requests.get(
    geojson_url
)

world_geojson = response.json()



# ---------------------------------------
# Create Map
# ---------------------------------------

m = folium.Map(

    location=[20, 0],

    zoom_start=2,

    tiles="OpenStreetMap"

)



# ---------------------------------------
# Risk Color Function
# ---------------------------------------

def get_color(country):

    if country in country_data:

        risk = country_data[country]["risk"]


        if risk == "High":
            return "red"


        elif risk == "Medium":
            return "orange"


        elif risk == "Low":
            return "green"


    return "lightgray"




# ---------------------------------------
# Add Forecast Information Banner
# ---------------------------------------

sample_country = list(country_data.keys())[0]


forecast_oni = country_data[sample_country]["forecast_oni"]

condition = country_data[sample_country]["condition"]



title_html = f"""

<div style="
position: fixed;
top: 10px;
left: 50px;
z-index:9999;
background:white;
padding:10px;
border-radius:10px;
box-shadow:0px 0px 5px grey;
">

<b>🌊 El Niño Prediction</b>

<br>

ONI Forecast: {forecast_oni}

<br>

Condition: {condition}

</div>

"""


m.get_root().html.add_child(
    folium.Element(title_html)
)




# ---------------------------------------
# Add Countries
# ---------------------------------------

for feature in world_geojson["features"]:


    properties = feature["properties"]


    country = (

        properties.get("ADMIN")

        or properties.get("name")

        or properties.get("NAME")

    )


    if not country:
        continue



    mapped_country = country_alias.get(
        country,
        country
    )



    if mapped_country in country_data:


        info = country_data[mapped_country]



        popup_html = f"""

        <div style="width:260px">

        <h3>
        🌎 {mapped_country}
        </h3>


        <b>Region:</b>
        {info['region']}


        <br><br>


        <b>Predicted El Niño Condition:</b>

        <br>

        {info['condition']}


        <br><br>


        <b>Forecast ONI:</b>

        {info['forecast_oni']}


        <br><br>


        <b>Risk Level:</b>

        {info['risk']}


        <br><br>


        <b>Expected Effects:</b>

        <ul>

        """



        for effect in info["effects"]:

            popup_html += f"""

            <li>{effect}</li>

            """



        popup_html += """

        </ul>

        </div>

        """



        folium.GeoJson(

            feature,


            style_function=lambda feature,
            country=mapped_country:
            {

                "fillColor":
                get_color(country),


                "color":
                "black",


                "weight":
                1,


                "fillOpacity":
                0.6

            },


            tooltip=mapped_country,


            popup=folium.Popup(

                popup_html,

                max_width=350

            )

        ).add_to(m)




# ---------------------------------------
# Niño 3.4 Monitoring Region
# ---------------------------------------

folium.Rectangle(

    bounds=[

        [-5, -170],

        [5, -120]

    ],


    color="red",


    fill=True,


    fill_color="red",


    fill_opacity=0.25,


    popup="NOAA Niño 3.4 Monitoring Region"

).add_to(m)




# ---------------------------------------
# Save Map
# ---------------------------------------

os.makedirs(

    "static/maps",

    exist_ok=True

)


m.save(

    "static/maps/elnino_map.html"

)


print(
    "✅ Dynamic El Niño Impact Map Created Successfully!"
)

print(
    "Saved: static/maps/elnino_map.html"
)