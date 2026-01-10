from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import EmployeeProfile


# ---------------------------
# LOGIN PAGE + SUBMISSION
# ---------------------------
def employee_login_page(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        if not employee_id or not password:
            messages.error(request, "Employee ID and password are required.")
            return render(request, "employee_login.html")

        try:
            profile = EmployeeProfile.objects.get(employee_id=employee_id)
        except EmployeeProfile.DoesNotExist:
            messages.error(request, "Employee ID not found.")
            return render(request, "employee_login.html")

        if not profile.check_password(password):
            messages.error(request, "Invalid password.")
            return render(request, "employee_login.html")

        # ✅ Save session
        request.session["employee_id"] = profile.employee_id

        # First login → force password change
        if profile.first_login:
            return redirect("accounts:change_password_first_login")

        # Normal login
        return redirect("employees:dashboard")

    # GET request → show login page
    return render(request, "employee_login.html")


# ---------------------------
# FIRST LOGIN PASSWORD CHANGE
# ---------------------------
def change_password_first_login(request):
    employee_id = request.session.get("employee_id")
    if not employee_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect("accounts:employee_login_page")

    try:
        profile = EmployeeProfile.objects.get(employee_id=employee_id)
    except EmployeeProfile.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect("accounts:employee_login_page")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            messages.error(request, "Both password fields are required.")
            return render(request, "change_password_first_login.html")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "change_password_first_login.html")

        # Update password & first_login
        profile.set_password(new_password)
        profile.first_login = False
        profile.save(update_fields=["password", "first_login"])

        messages.success(request, "Password changed successfully. Please login again.")
        request.session.flush()  # logout after password change
        return redirect("accounts:employee_login_page")

    return render(request, "change_password_first_login.html")


# ---------------------------
# LOGOUT (SESSION FLUSH + NO CACHE)
# ---------------------------
@never_cache
def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    response = redirect("accounts:employee_login_page")
    # Prevent caching previous pages after logout
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
