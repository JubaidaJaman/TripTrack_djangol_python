from django.urls import path
from . import views
app_name = 'payments'
urlpatterns = [
    path('checkout/<uuid:booking_id>/', views.checkout, name='checkout'),
]
