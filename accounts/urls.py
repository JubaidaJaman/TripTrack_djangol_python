from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('developer-login/', views.developer_login_view, name='developer_login'),
    path('developer-dashboard/', views.developer_dashboard_view, name='developer_dashboard'),
]

