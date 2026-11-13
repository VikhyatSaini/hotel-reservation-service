import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import close_old_connections
from rest_framework.test import APIClient

from reservations.models import Reservation
from rooms.models import Room


@pytest.mark.django_db
def test_create_reservation_success():
    client = APIClient()

    room = Room.objects.create(
        room_number="901",
        room_type=Room.RoomType.STANDARD,
    )

    response = client.post(
        "/reservations/",
        {
            "guest_name": "Test Guest",
            "room_id": room.id,
            "check_in": "2027-01-10",
            "check_out": "2027-01-12",
        },
        format="json",
    )

    assert response.status_code == 201
    assert "reference" in response.data


@pytest.mark.django_db
def test_reject_overlapping_reservation():
    client = APIClient()

    room = Room.objects.create(
        room_number="902",
        room_type=Room.RoomType.STANDARD,
    )

    first_response = client.post(
        "/reservations/",
        {
            "guest_name": "Guest One",
            "room_id": room.id,
            "check_in": "2027-01-10",
            "check_out": "2027-01-12",
        },
        format="json",
    )

    second_response = client.post(
        "/reservations/",
        {
            "guest_name": "Guest Two",
            "room_id": room.id,
            "check_in": "2027-01-11",
            "check_out": "2027-01-13",
        },
        format="json",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


@pytest.mark.django_db(transaction=True)
def test_concurrent_reservations_only_one_succeeds():
    room = Room.objects.create(
        room_number="903",
        room_type=Room.RoomType.STANDARD,
    )

    # Both workers wait here until they are ready to send requests.
    barrier = threading.Barrier(2)

    def make_booking(guest_name):
        # Each worker gets its own database connection.
        close_old_connections()

        try:
            client = APIClient()

            barrier.wait(timeout=10)

            response = client.post(
                "/reservations/",
                {
                    "guest_name": guest_name,
                    "room_id": room.id,
                    "check_in": "2027-01-20",
                    "check_out": "2027-01-22",
                },
                format="json",
            )

            return response.status_code

        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(make_booking, "Guest A")
        future_b = executor.submit(make_booking, "Guest B")

        status_a = future_a.result(timeout=30)
        status_b = future_b.result(timeout=30)

    # Exactly one request must succeed.
    assert sorted([status_a, status_b]) == [201, 409]

    # The database must contain exactly one confirmed reservation.
    confirmed_count = Reservation.objects.filter(
        room=room,
        status=Reservation.Status.CONFIRMED,
    ).count()

    assert confirmed_count == 1
