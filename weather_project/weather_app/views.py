from typing import Any, Dict, Optional

from django.core.cache import cache
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView

from .models import City, RequestHistory
from .utils import get_client_ip, get_weather


class HomeView(TemplateView):
    """Главная страница."""

    template_name = "weather_app/home.html"
    extra_context = {"title": "Погода"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_name = self.request.POST.get("city")
        if city_name:
            city = self.get_city(city_name)
            if not city:
                context["error_msg"] = (
                    f"Город {city_name} не найдет в базе данных!"
                )
            else:
                forecast = self.get_forecast(city)
                context["forecast"] = forecast
                self.update_history(city)
        return context

    def get_city(self, city_name: str) -> Optional[City]:
        """
        Получаем город из базы данных или из кеша, обновляющийся каждые 15 минут.
        """

        cache_key = f"city_{city_name}"
        city = cache.get(cache_key)
        if not city:
            try:
                city = City.objects.get(ru_name=city_name)
            except City.DoesNotExist:
                return None
            cache.set(cache_key, city, 15 * 60)  # 15 минут
        return city

    def get_forecast(self, city: City) -> Dict[str, Any]:
        """
        Получаем прогноз погоды по городу из сервера погоды или из кеша,
        обновляющийся каждые 15 минут.
        """

        cache_key = f"forecast_{city.ru_name}"
        forecast = cache.get(cache_key)
        if not forecast:
            forecast = get_weather(
                city.latitude, city.longitude, city.timezone
            )
            forecast |= {"name": city.ru_name}
            cache.set(cache_key, forecast, 15 * 60)  # 15 минут
        return forecast

    def update_history(self, city: City) -> None:
        """Сохраняем или обновляем информацию о запросе в базу данных."""

        ip_address = get_client_ip(self.request)
        RequestHistory.objects.update_or_create(
            ip_address=ip_address,
            city=city,
            defaults={"created": timezone.now()},
        )

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
