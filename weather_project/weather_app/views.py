from datetime import datetime as dt
import requests
from django.shortcuts import render
from django.views.generic import View

from .forms import CityForm


class HomeView(View):
    def get(self, request):
        form = CityForm()
        return render(request, "weather_app/index.html", {"form": form})

    def post(self, request):
        city = request.POST.get("city")
        print(city)
        form = CityForm(request.POST)
        get_weather()
        return render(request, "weather_app/index.html", {"form": form})


def get_weather():
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "hourly": "temperature_2m",
        "timezone": "Europe/Moscow",
        "forecast_days": 1,
    }
    api_url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        hourly = data.get("hourly")
        current = data.get("current")
        forecast = [
            {hourly["time"][hour]: hourly["temperature_2m"][hour]}
            for hour in range(len(hourly["time"]))
        ]
        forecast2 = [
            {
                dt.strptime(hourly["time"][hour], "%Y-%m-%dT%H:%M").time(): hourly[
                    "temperature_2m"
                ][hour]
            }
            for hour in range(len(hourly["time"]))
        ]
        print(forecast)
        print(forecast2)
        print(len(hourly["time"]))
        print(current)
