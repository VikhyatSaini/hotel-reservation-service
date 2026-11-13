from django.db import models

class Room(models.Model):
    class RoomType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        DELUXE = "DELUXE", "Deluxe"
        SUITE = "SUITE", "Suite"
    room_number = models.CharField(
        max_length=10,
        unique=True
    )
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices
    )
    is_active=models.BooleanField(
        default=True
    )
    def __str_(self):
        return f"{self.room_number} - {self.room_type}"