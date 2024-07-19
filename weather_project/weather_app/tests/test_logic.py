import json
from django.test import Client, TestCase, RequestFactory
from unittest.mock import patch
from django.urls import reverse
from http import HTTPStatus

from weather_app.models import City, RequestHistory


class TestContent(TestCase):

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
            **{"REMOTE_ADDR": self.ip_address}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'weather_app/home.html')
        self.assertIn('error_msg', response.context)
        self.assertNotIn('forecast', response.context)
        error_msg = f"Город {city} не найдет в базе данных!"
        self.assertEqual(error_msg, response.context["error_msg"])

    @patch("weather_app.views.get_weather")
    def test_last_cities(self, mock_get_weather):
        """
        Тестируем что после запроса о погоде на определенный город,
        этот город появляется в истории запросов.
        """

        self.client.post(
            reverse("weather_app:home"),
            {"city": self.data[0].get("ru_name")},
            **{"REMOTE_ADDR": self.ip_address}
        )
        count = RequestHistory.objects.filter(
            ip_address=self.ip_address
        ).count()
        self.assertEqual(count, 1)

    def test_city_autocomplete_ru_name(self):
        """
        Тестируем работу автокомплита при вводе названия города на русском.
        """

        response = self.client.get(
            reverse("weather_app:city_autocomplete"),
            {"term": self.data[0].get("ru_name")}
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
            {"term": self.data[0].get("en_name")}
        )
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(
            content[0].get("ru_name"), self.data[0].get("ru_name")
        )
