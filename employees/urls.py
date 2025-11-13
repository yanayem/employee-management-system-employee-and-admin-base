from django.urls import path
from . import views
app_name = 'employees'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance_view, name='attendance'),
    path("leave/", views.leave_view, name="leave"),
    path("leave/apply/", views.apply_leave_view, name="apply_leave"),
    path('payroll/', views.payroll_view, name='payroll'),
    path('performance/', views.performance_view, name='performance'),
    path('projects/', views.performance_view, name='projects'),
    path('documents/', views.documents, name='documents'),
    path('profile/', views.profile, name='profile'),
    path('support/', views.support, name='support'),
]
