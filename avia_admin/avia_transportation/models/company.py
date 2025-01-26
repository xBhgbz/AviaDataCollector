from django.db import models


class Company(models.Model):
    name = models.CharField("Название", max_length=300, unique=True)
    created_at = models.DateTimeField("Дата создания в БД", auto_now_add=True)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name[:50]
