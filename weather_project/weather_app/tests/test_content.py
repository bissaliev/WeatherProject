from unittest.mock import patch
from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.template import Template, Context
from http import HTTPStatus

from weather_app.models import City, RequestHistory


class TestContent(TestCase):
    MOCK_DATA = {
        "current": {
            "time": "2024-07-18T05: 30",
            "interval": 900,
            "temperature_2m": 14.9,
            "relative_humidity_2m": 93,
            "apparent_temperature": 15.6,
            "precipitation": 0.0,
            "cloud_cover": 0,
            "wind_speed_10m": 4.1,
            "wind_direction_10m": 285
        },
        "hourly": [
            18.6,
            17.9,
            17.1,
            16.4,
            15.9,
            15.2,
            14.7,
            14.5,
            15.3,
            16.6,
            18.0,
            19.4,
            20.8,
            22.2,
            23.4,
            24.5,
            25.1,
            25.4,
            25.9,
            25.5,
            25.4,
            24.5,
            23.3,
            21.7
        ]
    }

    @classmethod
    def setUpTestData(cls) -> None:
        cls.factory = RequestFactory()
        cls.client = Client()
        cls.data = (
            {
                "ru_name": "Москва",
                "en_name": "Moscow",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "timezone": "Europe/Moscow"
            },
            {
                "ru_name": "Лондон",
                "en_name": "London",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "timezone": "Europe/London"
            },
            {
                "ru_name": "Париж",
                "en_name": "Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "timezone": "Europe/Paris"
            },
        )
        cls.cities = City.objects.bulk_create(
            City(**city) for city in cls.data
        )
        cls.ip_address = '127.0.0.1'
        cls.histories = RequestHistory.objects.bulk_create(
            RequestHistory(ip_address=cls.ip_address, city=city)
            for city in cls.cities
        )

    @patch("weather_app.views.get_weather")
    def test_home_page_gives_correct_context(self, mock_get_weather):
        """Главная страница отдает правильный контекст."""

        mock_get_weather.return_value = self.MOCK_DATA
        fields = [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m"
        ]
        hours_amount = 24
        response = self.client.post(
            reverse("weather_app:home"),
            data={"city": self.data[0].get("ru_name")}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'weather_app/home.html')
        context = response.context
        self.assertIn("forecast", context)
        self.assertIn("hourly", context.get("forecast"))
        self.assertIn("current", context.get("forecast"))
        self.assertEqual(
            len(context.get("forecast").get("hourly")), hours_amount
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, context.get("forecast").get("current"))

    @patch("weather_app.views.get_weather")
    def test_last_cities_tag(self, mock_get_weather):
        """
        Тестируем отображение шаблоном последних
        запрошенных городов пользователем.
        """

        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = self.ip_address
        request.user = AnonymousUser()
        context = Context({"request": request})
        template = Template("{% load history_tag %} {% last_cities %}")
        rendered = template.render(context)
        self.assertIn(self.cities[0].ru_name, rendered)
        self.assertIn(self.cities[1].ru_name, rendered)
        self.assertIn(self.cities[2].ru_name, rendered)

    @patch("weather_app.views.get_weather")
    def test_last_cities_tag_order(self, mock_get_weather):
        """
        Тестируем отображение истории запрошенных городов пользователей
        от последних к более ранним.
        """

        now = timezone.now()
        for index, history in enumerate(self.histories):
            history.created = now - timezone.timedelta(days=index)
            history.save()
        histories = RequestHistory.objects.all()
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = self.ip_address
        request.user = AnonymousUser()
        context = Context({"request": request})
        template = Template("{% load history_tag %} {% last_cities %}")
        rendered = template.render(context)
        first_obj = rendered.find(histories[0].city.ru_name)
        second_obj = rendered.find(histories[1].city.ru_name)
        third_obj = rendered.find(histories[2].city.ru_name)
        self.assertTrue(first_obj < second_obj < third_obj)
