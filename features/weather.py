"""Current, model-based weather from Open-Meteo."""

from urllib.parse import urlencode

from network import read_json


def current_weather(city):
    matches = read_json(
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urlencode({"name": city, "count": 1, "language": "en"})
    ).get("results")
    if not matches:
        return {"text": f"I couldn't find {city}. Try a city and country, such as Paris, France."}
    place = matches[0]
    query = urlencode({
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    })
    current = read_json("https://api.open-meteo.com/v1/forecast?" + query)["current"]
    location = ", ".join(part for part in (place["name"], place.get("admin1"), place.get("country")) if part)
    return {
        "text": (
            f"Current weather in {location}\n"
            f"Temperature {current['temperature_2m']} °C · Feels like {current['apparent_temperature']} °C\n"
            f"Humidity {current['relative_humidity_2m']}% · Wind {current['wind_speed_10m']} km/h"
        ),
        "links": [{"label": "Weather data by Open-Meteo", "url": "https://open-meteo.com/"}],
    }
