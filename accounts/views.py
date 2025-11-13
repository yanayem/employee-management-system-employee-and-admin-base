from django.shortcuts import render, redirect
from .models import EmployeeProfile
from django.contrib import messages

def employee_login_page(request):
    """
    Render the unified login/change-password page.
    """
    return render(request, "employee_login.html")


def login_view(request):
    """
    Handle employee login via standard POST form.
    """
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        if not employee_id or not password:
            messages.error(request, "Employee ID and password are required.")
            return redirect('accounts:employee_login_page')

        try:
            profile = EmployeeProfile.objects.get(employee_id=employee_id)
            if profile.check_password(password):
                # Store employee_id in session
                request.session['employee_id'] = profile.employee_id

                # Redirect to change-password page if first login
                if profile.first_login:
                    return redirect('accounts:change_password_first_login')
                
                return redirect('employees:attendance')  # redirect to attendance page
            else:
                messages.error(request, "Invalid password.")
                return redirect('accounts:employee_login_page')

        except EmployeeProfile.DoesNotExist:
            messages.error(request, "Employee ID not found.")
            return redirect('accounts:employee_login_page')

    # GET request
    return render(request, "employee_login.html")


def change_password_first_login(request):
    """
    Handle password change for first login via POST form.
    """
    employee_id = request.session.get('employee_id')
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

        # Set new password
        profile.set_password(new_pass)
        profile.first_login = False
        profile.save()

        messages.success(request, "Password changed successfully. Please login.")
        return redirect('accounts:employee_login_page')

    return render(request, "change_password_first_login.html")


def logout_view(request):
    """
    Logout employee and clear session.
    """
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('accounts:employee_login_page')
