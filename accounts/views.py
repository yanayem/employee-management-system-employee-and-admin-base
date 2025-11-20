from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EmployeeProfile

# ---------------------------
# LOGIN PAGE
# ---------------------------
def employee_login_page(request):
    return render(request, "employee_login.html")


# ---------------------------
# LOGIN SUBMISSION
# ---------------------------
def login_view(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        if not employee_id or not password:
            messages.error(request, "Employee ID and password are required.")
            return redirect('accounts:employee_login_page')

        try:
            profile = EmployeeProfile.objects.get(employee_id=employee_id)
        except EmployeeProfile.DoesNotExist:
            messages.error(request, "Employee ID not found.")
            return redirect('accounts:employee_login_page')

        if not profile.check_password(password):
            messages.error(request, "Invalid password.")
            return redirect('accounts:employee_login_page')

        # Store session
        request.session['employee_id'] = profile.employee_id

        # First login → change password
        if profile.first_login:
            return redirect('accounts:change_password_first_login')

        # Normal login → dashboard
        return redirect('employees:dashboard')

    return render(request, "employee_login.html")


# ---------------------------
# FIRST LOGIN PASSWORD CHANGE
# ---------------------------
def change_password_first_login(request):
    employee_id = request.session.get("employee_id")
    if not employee_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('accounts:employee_login_page')

    try:
        profile = EmployeeProfile.objects.get(employee_id=employee_id)
    except EmployeeProfile.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('accounts:employee_login_page')

    if request.method == "POST":
        new_pass = request.POST.get("new_password")
        confirm_pass = request.POST.get("confirm_password")

        if not new_pass or not confirm_pass:
            messages.error(request, "Both password fields are required.")
            return redirect('accounts:change_password_first_login')

        if new_pass != confirm_pass:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:change_password_first_login')

        # Save new password
        profile.set_password(new_pass)
        profile.first_login = False
        profile.save()

        messages.success(request, "Password changed successfully. Please login again.")
        request.session.flush()  # logout after password change
        return redirect('accounts:employee_login_page')

    return render(request, "change_password_first_login.html")


# ---------------------------
# LOGOUT
# ---------------------------
def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('accounts:employee_login_page')
