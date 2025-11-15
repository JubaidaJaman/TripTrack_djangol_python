# tours/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tours/', views.tour_list, name='tour_list'),
    path('tours/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tours/create/', views.create_tour, name='create_tour'),
    path('tours/wishlist/toggle/<int:tour_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('tours/wishlist/', views.my_wishlist, name='my_wishlist'),
    path('tours/reviews/', views.my_reviews, name='my_reviews'),
    path('tours/department/<int:department_id>/', views.department_tours, name='department_tours'),
    path('tours/generate-qr/<int:tour_id>/', views.generate_qr_code, name='generate_qr_code'),
    
    # Notification URLs
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notifications/quick-reminder/', views.send_quick_reminder, name='send_quick_reminder'),
    path('notifications/organizer/', views.organizer_notifications, name='organizer_notifications'),
    path('notifications/my/', views.my_notifications, name='my_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('notifications/recent/', views.get_recent_notifications, name='get_recent_notifications'),
]