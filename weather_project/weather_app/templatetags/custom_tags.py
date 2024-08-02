from django.template import Library

register = Library()


@register.inclusion_tag("tags/last_cities.html", takes_context=True)
def last_cities(context, count=5):
    """Получение последних городов, которые запросил пользователь."""
    request = context.get("request")
    previous_cities = request.session.get("previous_cities")
    if previous_cities:
        return {"cities": previous_cities}


@register.filter
def index(lst, i):
    """Фильтр для получения элемента списка по индексу."""
    return lst[i]
