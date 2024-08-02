import datetime
from http import HTTPStatus
from unittest import skip
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from weather_app.models import City


class TestContent(TestCase):
    MOCK_DATA = {
        "current": {
            "time": "2024-07-20T07:00",
            "interval": 900,
            "temperature_2m": 18.7,
            "relative_humidity_2m": 81,
            "apparent_temperature": 19.7,
            "precipitation": 0.0,
            "cloud_cover": 40,
            "wind_speed_10m": 5.6,
            "wind_direction_10m": 297,
        },
        "weather_by_day": {
            datetime.date(2024, 7, 26): {
                "time": [
                    datetime.datetime(2024, 7, 26, 0, 0),
                    datetime.datetime(2024, 7, 26, 1, 0),
                    datetime.datetime(2024, 7, 26, 2, 0),
                    datetime.datetime(2024, 7, 26, 3, 0),
                    datetime.datetime(2024, 7, 26, 4, 0),
                    datetime.datetime(2024, 7, 26, 5, 0),
                    datetime.datetime(2024, 7, 26, 6, 0),
                    datetime.datetime(2024, 7, 26, 7, 0),
                    datetime.datetime(2024, 7, 26, 8, 0),
                    datetime.datetime(2024, 7, 26, 9, 0),
                    datetime.datetime(2024, 7, 26, 10, 0),
                    datetime.datetime(2024, 7, 26, 11, 0),
                    datetime.datetime(2024, 7, 26, 12, 0),
                    datetime.datetime(2024, 7, 26, 13, 0),
                    datetime.datetime(2024, 7, 26, 14, 0),
                    datetime.datetime(2024, 7, 26, 15, 0),
                    datetime.datetime(2024, 7, 26, 16, 0),
                    datetime.datetime(2024, 7, 26, 17, 0),
                    datetime.datetime(2024, 7, 26, 18, 0),
                    datetime.datetime(2024, 7, 26, 19, 0),
                    datetime.datetime(2024, 7, 26, 20, 0),
                    datetime.datetime(2024, 7, 26, 21, 0),
                    datetime.datetime(2024, 7, 26, 22, 0),
                    datetime.datetime(2024, 7, 26, 23, 0),
                ],
                "temperature_2m": [
                    17.6,
                    16.8,
                    16.0,
                    15.5,
                    15.1,
                    15.0,
                    15.5,
                    17.1,
                    19.3,
                    21.2,
                    22.4,
                    23.2,
                    23.9,
                    24.5,
                    25.1,
                    25.3,
                    25.3,
                    25.0,
                    24.4,
                    23.6,
                    22.4,
                    21.3,
                    20.0,
                    18.7,
                ],
                "cloud_cover": [
                    74,
                    61,
                    48,
                    35,
                    38,
                    41,
                    44,
                    29,
                    15,
                    0,
                    22,
                    45,
                    67,
                    69,
                    71,
                    73,
                    65,
                    58,
                    50,
                    41,
                    33,
                    24,
                    43,
                    62,
                ],
            }
        },
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
                "timezone": "Europe/Moscow",
            },
            {
                "ru_name": "Лондон",
                "en_name": "London",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "timezone": "Europe/London",
            },
            {
                "ru_name": "Париж",
                "en_name": "Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "timezone": "Europe/Paris",
            },
        )
        cls.cities = City.objects.bulk_create(
            City(**city) for city in cls.data
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
            "wind_direction_10m",
        ]
        response = self.client.post(
            reverse("weather_app:home"),
            data={"city": self.data[0].get("ru_name")},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "weather_app/home.html")
        context = response.context
        self.assertIn("forecast", context)
        self.assertIn("current", context.get("forecast"))
        self.assertIn("weather_by_day", context.get("forecast"))
        weather_by_day = context.get("forecast").get("weather_by_day")
        self.assertEqual(self.MOCK_DATA["weather_by_day"], weather_by_day)
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, context.get("forecast").get("current"))

    @skip
    @patch("weather_app.views.get_weather")  # TODO:Изменить под сессии
    def test_last_cities_tag(self, mock_get_weather):
        """
        Тестируем отображение шаблоном последних
        запрошенных городов пользователем.
        """

        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = self.ip_address
        request.user = AnonymousUser()
        context = Context({"request": request})
        template = Template("{% load custom_tags %} {% last_cities %}")
        rendered = template.render(context)
        self.assertIn(self.cities[0].ru_name, rendered)
        self.assertIn(self.cities[1].ru_name, rendered)
        self.assertIn(self.cities[2].ru_name, rendered)

    @skip
    @patch("weather_app.views.get_weather")  # TODO:Изменить под сессии
    def test_last_cities_tag_order(self, mock_get_weather):
        """
        Тестируем отображение истории запрошенных городов пользователей
        от последних к более ранним.
        """

        now = timezone.now()
        for index, history in enumerate(self.histories):
            history.created = now - timezone.timedelta(days=index)
            history.save()
        histories = None
        request = self.factory.get("/")
        request.user = AnonymousUser()
        context = Context({"request": request})
        template = Template("{% load custom_tags %} {% last_cities %}")
        rendered = template.render(context)
        first_obj = rendered.find(histories[0].city.ru_name)
        second_obj = rendered.find(histories[1].city.ru_name)
        third_obj = rendered.find(histories[2].city.ru_name)
        self.assertTrue(first_obj < second_obj < third_obj)
