# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Emergency Contact URLs
    path('emergency-contacts/', views.emergency_contacts, name='emergency_contacts'),
    path('emergency-contacts/add/', views.add_emergency_contact, name='add_emergency_contact'),
    path('emergency-contacts/edit/<int:contact_id>/', views.edit_emergency_contact, name='edit_emergency_contact'),
    path('emergency-contacts/delete/<int:contact_id>/', views.delete_emergency_contact, name='delete_emergency_contact'),
    path('emergency-contacts/set-primary/<int:contact_id>/', views.set_primary_contact, name='set_primary_contact'),
]