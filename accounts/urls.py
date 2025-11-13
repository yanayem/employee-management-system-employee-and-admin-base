from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login-page/", views.employee_login_page, name="employee_login_page"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password-first-login/", views.change_password_first_login, name="change_password_first_login"),
]
