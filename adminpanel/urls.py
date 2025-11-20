from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Custom admin login at /admin/
    path('login/', auth_views.LoginView.as_view(
        template_name='adminlogin.html',
        redirect_authenticated_user=True,
        next_page='/adminportal/dashboard/'  # fix the redirect URL
    ), name='admin_login'),
    # Dashboard
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    # payroll management
    path("payroll/", views.payroll_list, name="admin_payroll"),
    path("payroll/add/", views.payroll_add, name="admin_payroll_add"),
    path("payroll/edit/<int:pk>/", views.payroll_edit, name="admin_payroll_edit"),
    path("payroll/delete/<int:pk>/", views.payroll_delete,
         name="admin_payroll_delete"),
    path("payroll/slip/<int:pk>/", views.payroll_slip, name="admin_payroll_slip"),

    path('employees/', views.admin_employee_list, name='admin_employee_list'),
    path('employees/add/', views.admin_employee_add, name='admin_employee_add'),
    path('employees/message/<int:pk>/', views.admin_employee_message,
         name='admin_employee_message'),

    # Add this line for "View Employee" page
    path('employees/view/<int:pk>/', views.admin_employee_view,
         name='admin_employee_view'),

    path('employees/edit/<int:pk>/', views.admin_employee_edit,
         name='admin_employee_edit'),
    path('employees/deactivate/<int:pk>/',
         views.admin_employee_deactivate, name='admin_employee_deactivate'),
    path('employees/activate/<int:pk>/', views.admin_employee_activate,
         name='admin_employee_activate'),  # you need this view

    path('departments/', views.admin_department_list,
         name='admin_department_list'),
    path('attendance/', views.admin_attendance_view,
         name='admin_attendance_list'),
    path("leaves/", views.admin_leave_list, name="admin_leave_list"),
    path("leaves/<int:pk>/<str:action>/",
         views.admin_leave_update, name="admin_leave_update"),

    path("performance/", views.admin_performance_list,
         name="admin_performance_list"),
    path("performance/<int:pk>/", views.admin_performance_detail,
         name="admin_performance_detail"),
    path("performance/<int:employee_id>/edit/",
         views.admin_performance_edit, name="admin_performance_edit"),
    path("performance/skill/<int:performance_id>/add/",
         views.admin_performance_skill_edit, name="admin_performance_skill_add"),
    path("performance/skill/<int:performance_id>/edit/<int:skill_id>/",
         views.admin_performance_skill_edit, name="admin_performance_skill_edit"),
    path("performance/skill/delete/<int:skill_id>/",
         views.admin_performance_skill_delete, name="admin_performance_skill_delete"),
    path("performance/feedback/<int:performance_id>/add/",
         views.admin_performance_feedback_add, name="admin_performance_feedback_add"),
    path("performance/feedback/delete/<int:feedback_id>/",
         views.admin_performance_feedback_delete, name="admin_performance_feedback_delete"),


    # ===============================
    # Projects
    # ===============================
    path("projects/", views.admin_project_list, name="admin_project_list"),
    path("projects/add/", views.admin_project_edit, name="admin_project_add"),
    path("projects/<int:pk>/", views.admin_project_detail,
         name="admin_project_detail"),
    path("projects/<int:pk>/edit/", views.admin_project_edit,
         name="admin_project_edit"),
    path("projects/<int:pk>/delete/", views.admin_project_delete,
         name="admin_project_delete"),

    path('settings/', views.admin_settings, name='admin_settings'),
    path('profile/', views.admin_profile, name='admin_profile'),

    # Logout
    path('logout/', views.admin_logout, name='admin_logout'),
]
