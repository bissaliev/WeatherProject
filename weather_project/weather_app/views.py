from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q

from .models import City, RequestHistory
from .utils import get_weather, get_client_ip


from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Главная страница."""
    template_name = "weather_app/home.html"
    extra_context = {"title": "Погода"}

    def post(self, request):
        city_name = request.POST.get("city")
        try:
            city = City.objects.get(ru_name=city_name)
        except City.DoesNotExist:
            error_msg = f"Город {city_name} не найдет в базе данных!"
            return self.render_to_response({"error_msg": error_msg})
        forecast = get_weather(city.latitude, city.longitude, city.timezone)
        forecast |= {"name": city.ru_name,}
        ip_address = get_client_ip(request)
        request_history, created = RequestHistory.objects.get_or_create(
            ip_address=ip_address, city=city
        )
        if not created:
            request_history.created = timezone.now()
            request_history.save()
        return self.render_to_response({"forecast": forecast})


def city_autocomplete(request):
    if "term" in request.GET:
        qs = City.objects.filter(
            Q(en_name__icontains=request.GET.get("term"))
            | Q(ru_name__icontains=request.GET.get("term"))
        )
        cities = list(qs.values('ru_name', 'en_name'))
        return JsonResponse(cities, safe=False)


def page_not_found(request, exception):
    return render(request, "core/404.html", {"path": request.path}, status=404)
