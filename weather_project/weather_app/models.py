from django.db import models


class City(models.Model):
    """Модель городов."""

    ru_name = models.CharField(
        max_length=150, verbose_name="название"
    )
    en_name = models.CharField(
        max_length=150, verbose_name="английское название", null=True
    )
    latitude = models.DecimalField(
        max_digits=7, decimal_places=4, verbose_name="широта"
    )
    longitude = models.DecimalField(
        max_digits=7, decimal_places=4, verbose_name="долгота"
    )
    timezone = models.CharField(
        max_length=100,
        verbose_name="таймзона",
        null=True
    )

    class Meta:
        ordering = ("ru_name",)
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return (
            f"{self.ru_name}: Широта: {self.latitude}, "
            f"Долгота: {self.longitude}"
        )


class RequestHistory(models.Model):
    """Модель истории запросов."""

    ip_address = models.GenericIPAddressField("Ip address")
    city = models.ForeignKey(
        to=City,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Город"
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время запроса"
    )

    class Meta:
        ordering = ("-created",)
        verbose_name = "История запросов"
        verbose_name_plural = "Истории запросов"

    def __str__(self):
        return f"{self.ip_address} - {self.city.ru_name}: {self.created}"
