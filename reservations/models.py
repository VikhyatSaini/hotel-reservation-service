import uuid

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (
    DateRangeField,
    RangeOperators,
)
from django.db import models
from django.db.models import F, Q


class Reservation(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"

    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    guest_name = models.CharField(max_length=100)
    room = models.ForeignKey(
        "rooms.Room", on_delete=models.PROTECT, related_name="reservations"
    )
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CONFIRMED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(check_out__gt=models.F("check_in")),
                name="valid_reservation_date_range",
            ),
            ExclusionConstraint(
                name="prevent_overlapping_confirmed_reservations",
                expressions=[
                    (F("room"), RangeOperators.EQUAL),
                    (
                        models.Func(
                            F("check_in"),
                            F("check_out"),
                            function="DATERANGE",
                            template="%(function)s(%(expressions)s, '[)')",
                            output_field=DateRangeField(),
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(status="CONFIRMED"),
            ),
        ]

    def __str__(self):
        return f"{self.reference} - {self.guest_name}"
