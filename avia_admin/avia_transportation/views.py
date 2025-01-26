from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import Contract
from .serializers import ContractSerializer


@extend_schema(tags=["Авиаперевозки"])
class ContractViewSet(CreateModelMixin, GenericViewSet):
    """Представление контракта."""

    serializer_class = ContractSerializer
    queryset = Contract.objects.all()

    @transaction.atomic()
    def create(self, request: Request, *args, **kwargs) -> Response:
        return super().create(request, *args, **kwargs)


class ContractView(APIView):
    """Представление контракта."""

    @extend_schema(tags=["Авиаперевозки"], request=ContractSerializer)
    def post(self, request, *args, **kwargs):
        """Создание контракта"""
        serializer = ContractSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                contract = serializer.save()
            return Response(ContractSerializer(contract).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
