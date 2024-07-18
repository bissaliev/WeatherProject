from django.shortcuts import render
from django.views.generic import View
from .utils import get_coordinates_of_city, get_weather


class HomeView(View):
    def get(self, request):
        hours = list(range(24))
        return render(request, "weather_app/home.html", {"hours": hours})

    def post(self, request):
        city = request.POST.get("city")
        coordinates = get_coordinates_of_city(city)
        forecast = get_weather()
        forecast |= {
            "name": coordinates.get("name"),
            "country": coordinates.get("country")
        }
        return render(
            request, "weather_app/home.html",
            {"forecast": forecast}
        )
