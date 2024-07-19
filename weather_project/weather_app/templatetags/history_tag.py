from django.template import Library
from django.db.models import Subquery

from weather_app.models import RequestHistory, City
from weather_app.utils import get_client_ip

register = Library()


@register.inclusion_tag("tags/last_cities.html", takes_context=True)
def last_cities(context, count=5):
    """Получение последних городов, которые запросил пользователь."""
    request = context.get("request")
    ip_address = get_client_ip(request)
    city_ids = RequestHistory.objects.filter(
        ip_address=ip_address
    ).values_list("city__id", flat=True)[:count]
    cities = City.objects.filter(
        id__in=Subquery(city_ids)).order_by("-history__created")
    return {"cities": cities}
