from datetime import datetime
from typing import Any

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout


class ForecastWeather:
    """Класс для получения прогноза погоды."""

    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "hourly": ["temperature_2m", "cloud_cover"],
        "daily": [
            "temperature_2m_max",
            "precipitation_hours",
            "wind_direction_10m_dominant",
        ],
        "forecast_days": 7,
    }

    def __init__(self, latitude: float, longitude: float, timezone: str):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.add_coordinates_to_params()

    def add_coordinates_to_params(self) -> None:
        """Добавление координат в параметры запроса."""
        self.params["latitude"] = self.latitude
        self.params["longitude"] = self.longitude
        self.params["timezone"] = self.timezone

    def get_weather(self) -> dict[Any, Any]:
        """Получение прогноза погоды."""
        data = self.request_weather_forecast()
        current = data.get("current")
        forecast = {
            "current": current,
            "weather_by_day": self.process_weather_data_of_days(data),
        }
        return forecast

    def request_weather_forecast(self):
        """Запрос прогноза погоды к OpenMeteo API."""
        try:
            response = requests.get(
                self.api_url, params=self.params, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data
        except Timeout:
            print("Вышло время ожидания!")
        except ConnectionError:
            print("Произошла ошибка подключения")
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        return None

    def process_weather_data_of_days(self, data: dict) -> dict:
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
                    "cloud_cover": [],
                }
            weather_by_day[day]["time"].append(dt)
            weather_by_day[day]["temperature_2m"].append(temperatures[index])
            weather_by_day[day]["cloud_cover"].append(cloud_covers[index])
        return weather_by_day
