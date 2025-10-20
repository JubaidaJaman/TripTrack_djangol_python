# organizer_dashboard/urls.py
from django.urls import path
from . import views

app_name = 'organizer_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-tour/', views.create_tour, name='create_tour'),
]
