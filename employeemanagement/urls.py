from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Optional: Django default admin at /adminportal/
    path('adminportal/', admin.site.urls),  # <-- NO include(), just admin.site.urls

    # Custom admin dashboard and logout
    path('admin/', include('adminpanel.urls')),

    # Other app URLs
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('employees/', include('employees.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
