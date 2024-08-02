from django.db import models


class City(models.Model):
    """Модель городов."""

    ru_name = models.CharField(max_length=150, verbose_name="название")
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
        max_length=100, verbose_name="таймзона", null=True
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
