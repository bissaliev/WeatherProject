from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from weather_app.models import City


class TestCityRouting(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.city = City.objects.create(
            ru_name="Москва",
            en_name="Moscow",
            latitude=55.7558,
            longitude=37.6176,
            timezone="Europe/Moscow"
        )

    def test_pages_availability(self):
        """Тестирование доступности страницы home."""

        response = self.client.get(reverse("weather_app:home"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_city_autocomplete_match(self):
        """Тестирование корректной работы роута автокомплита."""

        response = self.client.get(
            reverse("weather_app:city_autocomplete"),
            {'term': self.city.ru_name}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
