from django.urls import path
from weather_app import views

app_name = "weather_app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("city-autocomplete/", views.city_autocomplete, name="city_autocomplete")
]
