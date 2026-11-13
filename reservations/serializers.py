from rest_framework import serializers

from reservations.models import Reservation
from rooms.models import Room


class ReservationCreateSerializer(serializers.ModelSerializer):

    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True),
        source="room"
    )

    class Meta:
        model = Reservation
        fields = [
            "guest_name",
            "room_id",
            "check_in",
            "check_out",
        ]

    def validate(self, attrs):
        if attrs["check_out"] <= attrs["check_in"]:
            raise serializers.ValidationError(
                "Check-out must be after check-in."
            )

        return attrs