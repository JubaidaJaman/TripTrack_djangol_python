# tourist_dashboard/urls.py
from django.urls import path
from . import views

app_name = 'tourist_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('saved-tours/', views.saved_tours, name='saved_tours'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
