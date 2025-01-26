from django.contrib.postgres.fields import ArrayField
from django.db import models

from ..constants import AirCraftType, DroneType, DroneServiceType, ContractRegularityType, WorkType


class AviaData(models.Model):
    contract = models.ForeignKey(
        "Contract",
        verbose_name="Контракт",
        on_delete=models.CASCADE,
        related_name="contract_avia_datas"
    )

    departure = models.ForeignKey(
        "Locality",
        verbose_name="Место отправления",
        on_delete=models.SET_NULL,
        related_name="departure_avia_datas",
        null=True
    )

    arrival = models.ForeignKey(
        "Locality",
        verbose_name="Место прибытия",
        on_delete=models.SET_NULL,
        related_name="arrival_avia_dats",
        null=True
    )

    cargo = models.CharField(
        "Примечания по грузу",
        max_length=300,
        null=True,
        blank=True
    )

    distance = models.FloatField("Общее расстояние км", null=True, blank=True)
    flight_hours_number = models.FloatField("Количество летных часов", null=True, blank=True)

    aircraft_examples = ArrayField(
        models.CharField(max_length=300),
        blank=True,
        default=list,
        verbose_name="Примеры ВС"
    )

    aircraft_number = models.PositiveSmallIntegerField("Количество ВС", null=True, blank=True)
    cargo_volume = models.FloatField("Объем груза кг, кол-во", null=True, blank=True)
    aircraft_type = models.CharField("Тип ВС", choices=AirCraftType.choices, null=True, blank=True)

    drone_type = models.CharField("Тип БВС", choices=DroneType.choices, null=True, blank=True)
    drone_payload = models.FloatField("Полезная нагрузка БВС кг", null=True, blank=True)

    drone_service_type = models.CharField(
        "Вид авиационного контракта БВС",
        choices=DroneServiceType.choices,
        null=True,
        blank=True
    )
    regularity_type = models.CharField(
        "Тип регулярности авиационного контракта",
        choices=ContractRegularityType.choices,
        null=True,
        blank=True
    )
    work_type = models.CharField(
        "Тип работы",
        choices=WorkType.choices,
        null=True,
        blank=True
    )
    number_flies = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField("Дата создания в БД", auto_now_add=True)

    class Meta:
        verbose_name = "Информация по авиационному контракту"
        verbose_name_plural = "Информация по авиационному контракту"
        indexes = [
            models.Index(fields=['distance'], name='idx_distance'),
            models.Index(fields=['flight_hours_number'], name='idx_flight_hours'),
        ]

    def __str__(self):
        return f"{self.departure} - {self.arrival}"
