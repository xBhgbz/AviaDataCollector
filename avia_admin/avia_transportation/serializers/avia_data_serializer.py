from rest_framework import serializers

from .locality_serializer import LocalitySerializer
from ..models import AviaData, Locality, Contract


class AviaDataSerializer(serializers.ModelSerializer):
    """Сериализатор модели AviaData"""
    departure = LocalitySerializer(required=False, allow_null=True)
    arrival = LocalitySerializer(required=False, allow_null=True)

    class Meta:
        model = AviaData
        fields = (
            "departure",
            "arrival",
            "cargo",
            "distance",
            "flight_hours_number",
            "aircraft_examples",
            "aircraft_number",
            "cargo_volume",
            "aircraft_type",
            "drone_type",
            "drone_payload",
            "drone_service_type",
            "regularity_type",
            "work_type",
            "number_flies"
        )

    def create(self, validated_data):
        
        contract: Contract = self.context.get('contract')
        departure = validated_data.pop("departure", None)
        arrival = validated_data.pop("arrival", None)

        if departure:
            departure = LocalitySerializer(data=departure)
            if departure.is_valid():
                departure = departure.save()

        if arrival:
            arrival = LocalitySerializer(data=arrival)
            if arrival.is_valid():
                arrival = arrival.save()

        avia_data = AviaData.objects.create(
            contract=contract,
            departure=departure,
            arrival=arrival,
            **validated_data
        )

        return avia_data


