from django.urls import path
from . import views

urlpatterns = [
    path("", views.tour_list, name="tour_list"),
]
