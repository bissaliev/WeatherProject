from django.db.models import Subquery
from django.template import Library
from weather_app.models import City, RequestHistory
from weather_app.utils import get_client_ip

register = Library()


@register.inclusion_tag("tags/last_cities.html", takes_context=True)
def last_cities1(context, count=5):
    """Получение последних городов, которые запросил пользователь."""
    request = context.get("request")
    ip_address = get_client_ip(request)
    city_ids = RequestHistory.objects.filter(
        ip_address=ip_address
    ).values_list("city__id", flat=True)[:count]
    cities = City.objects.filter(id__in=Subquery(city_ids)).order_by(
        "-history__created"
    )
    return {"cities": cities}


@register.inclusion_tag("tags/last_cities.html", takes_context=True)
def last_cities(context, count=5):
    """Получение последних городов, которые запросил пользователь."""
    request = context.get("request")
    cities_names = list(request.session.get("previous_cities"))
    print(cities_names)
    return {"cities": cities_names}


@register.filter
def index(lst, i):
    """Фильтр для получения элемента списка по индексу."""
    return lst[i]
