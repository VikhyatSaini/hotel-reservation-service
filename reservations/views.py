import logging

from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reservations.models import Reservation
from reservations.serializers import ReservationCreateSerializer
from rooms.models import Room

logger = logging.getLogger(__name__)


@api_view(["POST"])
def create_reservation(request):
    serializer = ReservationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    requested_room = serializer.validated_data["room"]
    check_in = serializer.validated_data["check_in"]
    check_out = serializer.validated_data["check_out"]

    try:
        with transaction.atomic():
            # Lock this physical room until the transaction finishes.
            room = Room.objects.select_for_update().get(
                pk=requested_room.pk,
                is_active=True,
            )

            overlapping_reservations = Reservation.objects.filter(
                room=room,
                status=Reservation.Status.CONFIRMED,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )

            if overlapping_reservations.exists():
                logger.warning(
                    "Reservation rejected: room unavailable",
                    extra={
                        "event": "reservation_conflict",
                        "room_id": room.id,
                    },
                )
                return Response(
                    {"error": "Room is not available for these dates."},
                    status=status.HTTP_409_CONFLICT,
                )

            reservation = serializer.save(room=room)

    except Room.DoesNotExist:
        return Response(
            {"error": "Room is not available."},
            status=status.HTTP_409_CONFLICT,
        )

    except IntegrityError:
        return Response(
            {"error": "Room is not available for these dates."},
            status=status.HTTP_409_CONFLICT,
        )

    logger.info(
        "Reservation created successfully",
        extra={
            "event": "reservation_created",
            "room_id": reservation.room_id,
            "reservation_reference": str(reservation.reference),
        },
    )
    return Response(
        {
            "reference": str(reservation.reference),
            "guest_name": reservation.guest_name,
            "room_id": reservation.room_id,
            "check_in": reservation.check_in,
            "check_out": reservation.check_out,
            "status": reservation.status,
        },
        status=status.HTTP_201_CREATED,
    )
