import datetime
import json
from http import HTTPStatus
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

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
        cls.ip_address = "127.0.0.1"
        cache.clear()

    @patch("weather_app.views.get_weather")
    def test_home_view_post_city_not_found(self, mock_get_weather):
        """
        Тестируем отображение ошибки, если пользователь запросит
        неизвестный город.
        """

        city = "Неизвестный город"
        response = self.client.post(
            reverse("weather_app:home"),
            {"city": city},
            **{"REMOTE_ADDR": self.ip_address},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "weather_app/home.html")
        self.assertIn("error_msg", response.context)
        self.assertNotIn("forecast", response.context)
        error_msg = f"Город {city} не найдет в базе данных!"
        self.assertEqual(error_msg, response.context["error_msg"])

    @patch("weather_app.views.get_weather")
    def test_last_cities(self, mock_get_weather):
        """
        Тестируем что после запроса о погоде на определенный город,
        этот город появляется в истории запросов.
        """

        mock_get_weather.return_value = self.MOCK_DATA
        self.client.post(
            reverse("weather_app:home"),
            {"city": self.data[0].get("ru_name")},
            **{"REMOTE_ADDR": self.ip_address},
        )

    def test_city_autocomplete_ru_name(self):
        """
        Тестируем работу автокомплита при вводе названия города на русском.
        """

        response = self.client.get(
            reverse("weather_app:city_autocomplete"),
            {"term": self.data[0].get("ru_name")},
        )
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(
            content[0].get("ru_name"), self.data[0].get("ru_name")
        )

    def test_city_autocomplete_en_name(self):
        """
        Тестируем работу автокомплита при вводе названия города на английском.
        """

        response = self.client.get(
            reverse("weather_app:city_autocomplete"),
            {"term": self.data[0].get("en_name")},
        )
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(
            content[0].get("ru_name"), self.data[0].get("ru_name")
        )
