import requests


def get_coordinates_of_city(city):
    """Получение координат по названию города."""
    params = {
        "name": city,
        "count": 1,
        "language": "ru",
        "format": "json"
    }
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(geocode_url, params=params, timeout=10)
    data = response.json()
    print(data)
    results = {
        "name": data.get("name"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timezone": data.get("timezone"),
        "country": data.get("country"),
    }
    return results


def get_weather(latitude=52.52, longitude=13.41, timezone="Europe/Berlin"):
    """Получение погоды."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m"
        ],
        "hourly": "temperature_2m",
        "timezone": timezone,
        "forecast_days": 1
    }
    api_url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(api_url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(data)
        hourly = data.get("hourly")
        current = data.get("current")
        forecast = {
            "hourly": hourly.get("temperature_2m"),
            "current": current
        }
        return forecast
