import requests

WEATHER_CODES = {
    0: "☀ Clear Sky",
    1: "🌤 Mainly Clear",
    2: "⛅ Partly Cloudy",
    3: "☁ Overcast",
    45: "🌫 Fog",
    48: "🌫 Depositing Fog",
    51: "🌦 Light Drizzle",
    53: "🌦 Moderate Drizzle",
    55: "🌧 Heavy Drizzle",
    61: "🌦 Light Rain",
    63: "🌧 Moderate Rain",
    65: "🌧 Heavy Rain",
    71: "❄ Light Snow",
    80: "🌦 Rain Showers",
    81: "🌧 Heavy Showers",
    95: "⛈ Thunderstorm"
}

def execute(data):
    location = data.get("location", "Mangalore")

    try:
        # Step 1: Convert city name to latitude & longitude
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search?"
            f"name={location}"
            f"&count=1"
            f"&countryCode=IN"
            f"&language=en"
            f"&format=json"
        )

        geo = requests.get(geo_url).json()
        #print(geo)


        if "results" not in geo:
            return {
                "success": False,
                "reply": f"Couldn't find {location}."
            }

        latitude = geo["results"][0]["latitude"]
        longitude = geo["results"][0]["longitude"]

        # Step 2: Fetch live weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,relative_humidity_2m,"
            f"wind_speed_10m,weather_code"
        )

        weather = requests.get(weather_url).json()

        current = weather["current"]
        condition = WEATHER_CODES.get(
            current["weather_code"],
            "Unknown"
        )

        return {
            "success": True,
            "reply":
                f"Weather in {location}\n\n"
                f"🌡 Temperature : {current['temperature_2m']}°C\n"
                f"💧 Humidity : {current['relative_humidity_2m']}%\n"
                f"💨 Wind Speed : {current['wind_speed_10m']} km/h"
        }

    except Exception as e:
        return {
            "success": False,
            "reply": str(e)
        }