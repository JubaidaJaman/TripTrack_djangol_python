from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # DO NOT include Django admin site per your requirement; if you still want it, add it intentionally.
    # path('admin/', admin.site.urls),
    path('', account_views.home, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('tours/', include('tours.urls', namespace='tours')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('developer/', include('developer_dashboard.urls', namespace='developer')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
