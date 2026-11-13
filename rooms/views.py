from rest_framework.decorators import api_view
from rest_framework.response import Response

from rooms.models import Room
from reservations.models import Reservation
from rooms.serializers import AvailabilityQuerySerializer


@api_view(["GET"])
def room_availability(request):
    serializer = AvailabilityQuerySerializer(
        data=request.query_params
    )

    serializer.is_valid(raise_exception=True)

    check_in = serializer.validated_data["check_in"]
    check_out = serializer.validated_data["check_out"]
    room_type = serializer.validated_data["room_type"]

    overlapping_reservations = Reservation.objects.filter(
        status=Reservation.Status.CONFIRMED,
        check_in__lt=check_out,
        check_out__gt=check_in,
    )

    booked_room_ids = overlapping_reservations.values_list(
        "room_id",
        flat=True
    )

    available_rooms = Room.objects.filter(
        is_active=True,
        room_type=room_type,
    ).exclude(
        id__in=booked_room_ids
    )

    results = [
        {
            "room_number": room.room_number,
            "room_type": room.room_type,
        }
        for room in available_rooms
    ]

    return Response(results)

@api_view(["GET"])
def room_list(request):
    return Response({
        "message": "Room API is working",
        "rooms": []    
    })

