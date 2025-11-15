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
]