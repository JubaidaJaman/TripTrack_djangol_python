from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('departments/', views.manage_departments, name='manage_departments'),
]