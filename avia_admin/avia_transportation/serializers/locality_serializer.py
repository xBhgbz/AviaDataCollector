from rest_framework import serializers

from ..models import Locality


class LocalitySerializer(serializers.ModelSerializer):
    """Сериализатор модели Locality"""

    class Meta:
        model = Locality
        fields = (
            "name",
            "latitude",
            "longitude"
        )
        extra_kwargs = {
            "name": {"validators": []},
        }

    def create(self, validated_data):
        name = validated_data.get("name")
        try:
            existing_locality = Locality.objects.get(name=name)
        except Locality.DoesNotExist:
            return super().create(validated_data)

        if validated_data["latitude"]:
            existing_locality.latitude = validated_data["latitude"]
        if validated_data["longitude"]:
            existing_locality.longitude = validated_data["longitude"]

        existing_locality.save()
        return existing_locality
