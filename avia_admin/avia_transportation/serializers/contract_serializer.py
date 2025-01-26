from rest_framework import serializers

from . import AviaDataSerializer, CompanySerializer
from ..models import Contract, Company


class ContractSerializer(serializers.ModelSerializer):
    """Сериализатор модели Contract"""

    contract_avia_datas = AviaDataSerializer(many=True)
    customer = CompanySerializer(required=False, allow_null=True)
    contractor = CompanySerializer(required=False, allow_null=True)

    class Meta:
        model = Contract
        fields = (
            "tender_number",
            "site_url",
            "customer",
            "contractor",
            "tender_info_link",
            "price",
            "conditions",
            "date_start",
            "date_finish",
            "contract_avia_datas"
        )

    def create(self, validated_data):
        avia_data_list = validated_data.pop("contract_avia_datas", [])
        customer = validated_data.pop("customer", None)
        contractor = validated_data.pop("contractor", None)

        if customer:
            customer, _ = Company.objects.get_or_create(**customer)

        if contractor:
            contractor, _ = Company.objects.get_or_create(**contractor)

        contract = Contract.objects.create(
            **validated_data,
            customer=customer,
            contractor=contractor
        )

        for avia_data in avia_data_list:
            serializer = AviaDataSerializer(data=avia_data, context={'contract': contract})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return contract
    