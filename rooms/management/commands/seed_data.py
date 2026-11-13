from django.core.management.base import BaseCommand

from rooms.models import Room


class Command(BaseCommand):
    help = "Create sample hotel rooms"

    def handle(self, *args, **options):
        rooms = [
            ("101", Room.RoomType.STANDARD),
            ("102", Room.RoomType.STANDARD),
            ("201", Room.RoomType.DELUXE),
            ("202", Room.RoomType.DELUXE),
            ("301", Room.RoomType.SUITE),
        ]

        for room_number, room_type in rooms:
            room, created = Room.objects.get_or_create(
                room_number=room_number,
                defaults={"room_type": room_type},
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created room {room.room_number}")
                )
            else:
                self.stdout.write(f"Room {room.room_number} already exists")

        self.stdout.write(self.style.SUCCESS("Seed data completed."))
