from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.utils import timezone

from .models import City, RequestHistory
from .utils import get_weather, get_client_ip


class HomeView(View):
    """Главная страница."""
    def get(self, request):
        ip_address = get_client_ip(request)
        histories = RequestHistory.objects.filter(ip_address=ip_address)[:5]
        return render(
            request, "weather_app/home.html", {"histories": histories}
        )

    def post(self, request):
        city_name = request.POST.get("city")
        city = City.objects.get(ru_name=city_name)
        forecast = get_weather(city.latitude, city.longitude, "Europe/Moscow")
        forecast |= {
            "name": city.ru_name,
            "country": city.timezone
        }
        ip_address = get_client_ip(request)
        request_history, created = RequestHistory.objects.get_or_create(
            ip_address=ip_address, city=city
        )
        if not created:
            request_history.created = timezone.now()
            request_history.save()
        histories = RequestHistory.objects.filter(ip_address=ip_address)[:5]
        return render(
            request, "weather_app/home.html",
            {"forecast": forecast, "histories": histories}
        )


def city_autocomplete(request):
    if "term" in request.GET:
        qs = (
            City.objects.filter(en_name__icontains=request.GET.get("term"))
            | City.objects.filter(ru_name__icontains=request.GET.get("term"))
        )
        cities = list(qs.values('ru_name', 'en_name', 'latitude', 'longitude', 'timezone'))
        return JsonResponse(cities, safe=False)


def page_not_found(request, exception):
    return render(request, "core/404.html", {"path": request.path}, status=404)
