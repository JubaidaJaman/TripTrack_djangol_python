# organizer_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='organizer_dashboard'),
    path('tour/create/', views.create_tour, name='organizer_create_tour'),
    path('tour/<int:pk>/edit/', views.edit_tour, name='organizer_edit_tour'),
    path('tour/<int:pk>/delete/', views.delete_tour, name='organizer_delete_tour'),
]
