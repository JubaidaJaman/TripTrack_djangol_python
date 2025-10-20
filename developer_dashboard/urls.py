from django.urls import path
from . import views

app_name = 'developer'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tour-toggle/<int:pk>/', views.tour_toggle_active, name='tour_toggle'),
    path('tour-delete/<int:pk>/', views.tour_delete, name='tour_delete'),
    path('logout/', views.developer_logout, name='logout'), 
]
