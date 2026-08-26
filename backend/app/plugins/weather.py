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
    95: "⛈ Thunderstorm",
}

LOCATION_ALIASES = {
    "bangalore": "Bengaluru",
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "mysore": "Mysuru",
}


def execute(data):
    location = data.get("location")
    requested_time = data.get("time", "today")

    if not location:
        return {
            "success": False,
            "reply": "Please tell me the city for the weather forecast.",
        }

    lookup_location = LOCATION_ALIASES.get(
        location.lower().strip(),
        location.strip(),
    )

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": lookup_location,
                "count": 1,
                "countryCode": "IN",
                "language": "en",
                "format": "json",
            },
            timeout=10,
        ).json()

        if not geo.get("results"):
            print("Geocoding failed for:", repr(lookup_location))
            print("Geocoding response:", geo)

            return {
                "success": False,
                "reply": f"Couldn't find {location}. Please try the city name again.",
            }

        place = geo["results"][0]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "wind_speed_10m,weather_code"
                ),
                "daily": (
                    "weather_code,temperature_2m_max,"
                    "temperature_2m_min,precipitation_probability_max,"
                    "wind_speed_10m_max"
                ),
                "forecast_days": 2,
                "timezone": "auto",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            },
            timeout=10,
        ).json()

        location_name = place["name"]

        # Tomorrow uses the second daily item: index 1.
        if requested_time == "tomorrow":
            daily = weather["daily"]
            condition = WEATHER_CODES.get(
                daily["weather_code"][1],
                "Unknown",
            )
            minimum = daily["temperature_2m_min"][1]
            maximum = daily["temperature_2m_max"][1]
            rain_chance = daily["precipitation_probability_max"][1]
            wind_speed = daily["wind_speed_10m_max"][1]

            return {
                "success": True,
                "reply": (
                    f"Tomorrow's weather in {location_name}: {condition}. "
                    f"Temperature will range from {minimum} to {maximum} degrees Celsius. "
                    f"Chance of rain is {rain_chance} percent."
                ),
                "weather": {
                    "location": location_name,
                    "period": "Tomorrow",
                    "condition": condition,
                    "temperature": f"{minimum}–{maximum}",
                    "humidity": None,
                    "wind_speed": wind_speed,
                    "rain_chance": rain_chance,
                },
            }

        current = weather["current"]
        condition = WEATHER_CODES.get(
            current["weather_code"],
            "Unknown",
        )

        return {
            "success": True,
            "reply": (
                f"Weather in {location_name}: {condition}. "
                f"Temperature is {current['temperature_2m']} degrees Celsius."
            ),
            "weather": {
                "location": location_name,
                "period": "Now",
                "condition": condition,
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"],
                "wind_speed": current["wind_speed_10m"],
                "rain_chance": None,
            },
        }

    except Exception as e:
        print("Weather error:", e)

        return {
            "success": False,
            "reply": "Sorry, I could not fetch the weather right now.",
        }