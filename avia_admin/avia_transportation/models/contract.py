from django.db import models


class Contract(models.Model):

    tender_number = models.CharField("Идентификатор тендера", max_length=255)
    site_url = models.CharField("Ссылка на сайт", max_length=300)

    customer = models.ForeignKey(
        "Company",
        verbose_name="Заказчик",
        on_delete=models.SET_NULL,
        related_name="customer_contracts",
        null=True,
        blank=True
    )
    contractor = models.ForeignKey(
        "Company",
        verbose_name="Исполнитель",
        on_delete=models.SET_NULL,
        related_name="contractor_contracts",
        null=True,
        blank=True
    )

    tender_info_link = models.CharField("Ссылка на тендер", max_length=1000)

    price = models.FloatField("Цена ₽", blank=True, null=True)
    conditions = models.JSONField("Особые условия", blank=True, null=True)
    additional_services = models.JSONField("Доп. улуги", blank=True, null=True)

    date_start = models.DateField("Дата начала", blank=True, null=True)
    date_finish = models.DateField("Дата окончания", blank=True, null=True)
    created_at = models.DateTimeField("Дата создания в БД", auto_now_add=True)

    class Meta:
        verbose_name = "Контракт"
        verbose_name_plural = "Контракты"
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(fields=['tender_number', 'site_url'], name='unique_tender_site')
        ]

    def __str__(self):
        return f"{self.tender_number} {self.site_url}"




