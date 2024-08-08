from typing import Any, Dict

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from .models import City
from .utils import ForecastWeather


class CityAddToSessionMixin:
    """Миксин для добавление названия запрошенного города в сессии."""

    def add_city_to_session(self, city_name: str) -> None:
        """
        Добавление названия запрошенного города в сессии для дальнейшего
        отображения пользователю.
        """
        previous_cities = list(
            dict.fromkeys(
                [city_name] + self.request.session.get("previous_cities", [])
            )
        )
        while previous_cities and len(previous_cities) > 10:
            previous_cities.pop()
        self.request.session["previous_cities"] = previous_cities


class ForecastMixin:
    """
    Миксин для формирования параметров и вызова функции для получения
    прогноза погоды.
    """

    def get_forecast(self, city: City) -> Dict[str, Any]:
        """
        Формирование параметров и вызов функции для получения прогноза погоды.
        """
        forecast_class = ForecastWeather(
            city.latitude, city.longitude, city.timezone
        )
        forecast = forecast_class.get_weather()
        forecast |= {"name": city.ru_name}
        return forecast


class HomeView(ForecastMixin, CityAddToSessionMixin, TemplateView):
    """Класс представления для получения прогноза погоды."""

    template_name = "weather_app/home.html"
    extra_context = {"title": "Погода"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_name = self.request.POST.get("city")
        if city_name:
            city = get_object_or_404(City, ru_name=city_name)
            context["forecast"] = self.get_forecast(city)
            self.add_city_to_session(city_name)
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


def city_autocomplete(request) -> JsonResponse:
    """Функция представления для автокомплита."""

    if "term" in request.GET:
        qs = City.objects.filter(
            Q(en_name__icontains=request.GET.get("term"))
            | Q(ru_name__icontains=request.GET.get("term"))
        )
        cities = list(qs.values("ru_name", "en_name"))
        return JsonResponse(cities, safe=False)


def page_not_found(request, exception):
    return render(request, "weather_app/404.html", status=404)
