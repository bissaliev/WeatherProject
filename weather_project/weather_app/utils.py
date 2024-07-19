import requests
from datetime import datetime


def process_weather_data_of_days(data):
    """Обработка данных о погоде по дням."""

    hourly = data.get("hourly")
    times = hourly.get("time")
    temperatures = hourly.get("temperature_2m")
    cloud_covers = hourly.get("cloud_cover")
    weather_by_day = {}
    for index, time_str in enumerate(times):
        dt = datetime.fromisoformat(time_str)
        day = dt.date()
        if day not in weather_by_day:
            weather_by_day[day] = {
                "time": [],
                "temperature_2m": [],
                "cloud_cover": []
            }
        weather_by_day[day]["time"].append(dt)
        weather_by_day[day]["temperature_2m"].append(temperatures[index])
        weather_by_day[day]["cloud_cover"].append(cloud_covers[index])
    return weather_by_day


def get_weather(latitude, longitude, timezone):
    """Получение данных о погоде."""

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
        "forecast_days": 7
    }
    api_url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(api_url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        current = data.get("current")
        forecast = {
            "current": current,
            "weather_by_day": process_weather_data_of_days(data)
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
