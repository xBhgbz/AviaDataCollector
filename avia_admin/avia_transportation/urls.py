from django.urls import path
from .views import ContractView

urlpatterns = [
    path('contracts/', ContractView.as_view(), name='contract-create'),
]