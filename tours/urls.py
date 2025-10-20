from django.urls import path
from . import views

app_name = 'tours'
urlpatterns = [
    path('', views.tour_list, name='list'),
    path('create/', views.create_tour, name='create'),
    path('<uuid:pk>/', views.tour_detail, name='detail'),
    path('<uuid:pk>/wishlist/', views.wishlist_add, name='wishlist_add'),
    path('<uuid:pk>/book/', views.book_tour, name='book'),
    path('<uuid:pk>/qr-checkin/', views.checkin_via_qr, name='qr_checkin'),
    # public QR detail route (when scanning without login)
    path('<uuid:pk>/qr-detail/', views.tour_detail, name='qr_detail'),
]
