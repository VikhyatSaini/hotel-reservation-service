from django.urls import path
from . import views

urlpatterns=[
    path("", views.room_list),
    path("availability/", views.room_availability, name="room-availability",
    ),
]