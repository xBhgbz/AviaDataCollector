from django.db import models


class Locality(models.Model):
    name = models.CharField("Название", max_length=300, db_index=True)

    latitude = models.CharField("Широта: ", max_length=300, null=True, blank=True)
    longitude = models.CharField("Долгота: ", max_length=300, null=True, blank=True)

    created_at = models.DateTimeField("Дата создания в БД", auto_now_add=True)

    class Meta:
        verbose_name = "Населенный пункт"
        verbose_name_plural = "Населенные пункты"

    def __str__(self):
        return self.name
