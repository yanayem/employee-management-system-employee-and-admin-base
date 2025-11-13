from django.contrib import admin
from django.urls import path, include
from . import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Home page (role selection)
    path('accounts/', include('accounts.urls')), 
    path('employees/', include('employees.urls'))
]
