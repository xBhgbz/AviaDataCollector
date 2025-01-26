from django.contrib import admin

from ..models import Locality


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    search_fields = ("name",)
