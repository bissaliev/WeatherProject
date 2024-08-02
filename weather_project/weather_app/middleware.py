def last_city_middleware(get_response):
    """Middleware для добавления запрошенных городов в сессии."""

    def middleware(request):
        response = get_response(request)
        city_name = request.POST.get("city")
        if city_name and ("error_msg" not in response.context_data):
            previous_cities = list(
                dict.fromkeys(
                    [city_name] + request.session.get("previous_cities", [])
                )
            )
            while previous_cities and len(previous_cities) > 10:
                previous_cities.pop()
            request.session["previous_cities"] = previous_cities
        return response

    return middleware
