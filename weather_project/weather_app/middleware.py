def last_city_middleware(get_response):
    def middleware(request):
        city_name = request.POST.get("city")
        response = get_response(request)
        if city_name:
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
