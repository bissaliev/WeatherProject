import requests


def get_weather(latitude, longitude, timezone):
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
        "hourly": ["temperature_2m", "cloud_cover"],
        "daily": ["temperature_2m_max", "precipitation_hours", "wind_direction_10m_dominant"],
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
            "hourly": zip(hourly.get("temperature_2m"), hourly.get("cloud_cover")),
            "current": current
        }
        return forecast


def get_client_ip(request):
    """
    Функция для определения IP-адреса пользователя.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[-1].strip()
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )
