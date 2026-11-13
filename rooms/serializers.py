from rest_framework import serializers

from rooms.models import Room


class AvailabilityQuerySerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    room_type = serializers.ChoiceField(choices=Room.RoomType.choices)

    def validate(self, attrs):
        if attrs["check_out"] <= attrs["check_in"]:
            raise serializers.ValidationError("Check-out must be after check-in")
        return attrs
