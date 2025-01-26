from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch

from .tools import get_value_or_default
from ..models import Contract, AviaData


class AviaDataInline(admin.StackedInline):
    model = AviaData
    extra = 0


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "tender_number",
        "customer",
        "contractor",
        "price",
        "date_start",
        "date_finish",
        "display_avia_data",
    )

    list_filter = (
        "contract_avia_datas__aircraft_type",
        "contract_avia_datas__drone_type",
        "contract_avia_datas__drone_service_type",
        "contract_avia_datas__work_type",
    )
    search_fields = (
        "id",
        "customer__name",
        "contractor__name",
        "contract_avia_datas__departure__name",
        "contract_avia_datas__arrival__name",
    )
    
    inlines = [AviaDataInline]

    class Media:
        css = {
            "all": ("css/admin.css",),
        }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.prefetch_related(
            Prefetch(
                "contract_avia_datas",
                AviaData.objects.select_related("departure", "arrival")
            )
        )

    def display_avia_data(self, obj):
        avia_data = obj.contract_avia_datas.all()
        if not avia_data.exists():
            return "Нет данных"
        rows = "<br>".join(
            f"{get_value_or_default(data, 'departure')} → {get_value_or_default(data, 'arrival')} ["
            f"Расстояние: {get_value_or_default(data, 'distance')} км, "
            f"Часы: {get_value_or_default(data, 'flight_hours_number')} ч, "
            f"ВС: {get_value_or_default(data, 'aircraft_number')}, "
            f"Груз: {get_value_or_default(data, 'cargo_volume')} кг, "
            f"Тип ВС: {get_value_or_default(data, 'aircraft_type')}, "
            f"Тип БВС: {get_value_or_default(data, 'drone_type')}, "
            f"Нагрузка БВС: {get_value_or_default(data, 'drone_payload')} кг, "
            f"Вид контракта БВС: {get_value_or_default(data, 'drone_service_type')}, "
            f"Регулярность: {get_value_or_default(data, 'regularity_type')}, "
            f"Тип работы: {get_value_or_default(data, 'work_type')}]"
            for data in avia_data
        )
        return format_html(rows)

    display_avia_data.short_description = "Данные по авиации"
