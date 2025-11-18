# employees/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import Attendance, LeaveRequest, Payroll, Performance, Project
from .forms import LeaveRequestForm
from accounts.models import EmployeeProfile


def get_logged_in_employee(request):
    """
    Retrieve the currently logged-in employee using session.
    Returns None if not found.
    """
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return None
    try:
        return EmployeeProfile.objects.get(employee_id=employee_id)
    except EmployeeProfile.DoesNotExist:
        return None


# ===============================
# Dashboard
# ===============================
# employees/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from accounts.models import EmployeeProfile
from .models import Attendance, LeaveRequest, Payroll, Project




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from .models import Attendance, LeaveRequest, Payroll, Project
from accounts.models import EmployeeProfile

@login_required
def dashboard_view(request):
    """
    Employee dashboard with stats, projects, charts, dark mode toggle.
    """
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect('accounts:login')

    today = timezone.localdate()

    # Attendance stats
    month_records = Attendance.objects.filter(employee=employee, date__month=today.month)
    total_present = month_records.filter(status="Present").count()
    late_days = month_records.filter(status="Late").count()
    total_absent = month_records.count() - total_present - late_days
    if total_absent < 0:
        total_absent = 0  # safety check
    attendance_percent = round((total_present / month_records.count()) * 100, 1) if month_records.exists() else 0

    # Week hours
    week_records = Attendance.objects.filter(employee=employee, date__gte=today - timezone.timedelta(days=7))
    total_week_hours = sum(
        ((timezone.datetime.combine(r.date, r.check_out) - timezone.datetime.combine(r.date, r.check_in)).total_seconds() / 3600)
        for r in week_records if r.check_in and r.check_out
    )
    total_week_hours_formatted = f"{int(total_week_hours)}h {int((total_week_hours*60)%60)}m"

    # Leave balances
    leave_requests = LeaveRequest.objects.filter(employee=employee, status="Approved")
    balances = {
        "Annual": 18 - sum(l.total_days() for l in leave_requests.filter(leave_type="Annual")),
        "Sick": 8 - sum(l.total_days() for l in leave_requests.filter(leave_type="Sick")),
        "Personal": 5 - sum(l.total_days() for l in leave_requests.filter(leave_type="Personal")),
        "Maternity": 90 - sum(l.total_days() for l in leave_requests.filter(leave_type="Maternity")),
        "Emergency": 5 - sum(l.total_days() for l in leave_requests.filter(leave_type="Emergency")),
    }

    # Payroll
    payrolls = Payroll.objects.filter(employee=employee).order_by('-month')
    ytd_earnings = payrolls.aggregate(total_gross=Sum('gross_salary'))['total_gross'] or 0

    # Projects
    projects = Project.objects.filter(assigned_to=employee)
    success_rate = round(sum(p.progress for p in projects) / projects.count()) if projects.exists() else 0

    project_stats = [
        {"label": "Active Projects", "value": projects.filter(status="In Progress").count(), "icon": "fas fa-tasks", "icon_color": "text-blue-600"},
        {"label": "Completed", "value": projects.filter(status="Completed").count(), "icon": "fas fa-check-circle", "icon_color": "text-green-600"},
        {"label": "Pending Review", "value": projects.filter(status="Review").count(), "icon": "fas fa-clock", "icon_color": "text-yellow-600"},
        {"label": "Success Rate", "value": success_rate, "icon": "fas fa-percentage", "icon_color": "text-purple-600"},
    ]

    context = {
        "employee": employee,
        "attendance_percent": attendance_percent,
        "total_present": total_present,
        "late_days": late_days,
        "total_absent": total_absent,   # ✅ Added
        "month_records": month_records,
        "total_week_hours": total_week_hours_formatted,
        "balances": balances,
        "ytd_earnings": ytd_earnings,
        "projects": projects,
        "project_stats": project_stats,
    }

    return render(request, 'employee_dashboard.html', context)


# ===============================
# Attendance
# ===============================
@login_required
def attendance_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect('accounts:login')

    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

    if request.method == "POST":
        action = request.POST.get("action")
        now = timezone.localtime().time()

        if action == "check_in" and not attendance.check_in:
            attendance.check_in = now
            attendance.status = "Present"
            attendance.save()
        elif action == "check_out" and not attendance.check_out:
            attendance.check_out = now
            attendance.save()

        return redirect('employees:attendance')

    week_records = Attendance.objects.filter(
        employee=employee,
        date__gte=today - timezone.timedelta(days=7)
    ).order_by('-date')

    month_records = Attendance.objects.filter(
        employee=employee,
        date__month=today.month
    ).order_by('-date')

    total_present = month_records.filter(status="Present").count()
    late_days = month_records.filter(status="Late").count()
    attendance_percent = round((total_present / month_records.count()) * 100, 1) if month_records.exists() else 0

    # Total hours worked this week
    total_week_hours = sum(
        ((timezone.datetime.combine(r.date, r.check_out) - timezone.datetime.combine(r.date, r.check_in)).total_seconds() / 3600)
        for r in week_records if r.check_in and r.check_out
    )

    context = {
        "attendance": attendance,
        "week_records": week_records,
        "month_records": month_records,
        "attendance_percent": attendance_percent,
        "late_days": late_days,
        "total_week_hours": f"{int(total_week_hours)}h {int((total_week_hours*60)%60)}m",
        "week_days_present": week_records.filter(status="Present").count(),
        "week_total_days": week_records.count(),
    }

    return render(request, "attendance.html", context)


# ===============================
# Leave
# ===============================
@login_required
def leave_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        messages.error(request, "You are not logged in as an employee.")
        return redirect("accounts:login")

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.save()
            messages.success(request, "Leave request submitted successfully!")
            return redirect("employees:leave")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeaveRequestForm()

    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by("-created_at")

    balances = {
        "Annual": 18 - sum(l.total_days() for l in leave_requests.filter(leave_type="Annual", status="Approved")),
        "Sick": 8 - sum(l.total_days() for l in leave_requests.filter(leave_type="Sick", status="Approved")),
        "Personal": 5 - sum(l.total_days() for l in leave_requests.filter(leave_type="Personal", status="Approved")),
        "Maternity": 90 - sum(l.total_days() for l in leave_requests.filter(leave_type="Maternity", status="Approved")),
        "Emergency": 5 - sum(l.total_days() for l in leave_requests.filter(leave_type="Emergency", status="Approved")),
    }

    context = {
        "form": form,
        "leave_requests": leave_requests,
        "balances": balances,
    }
    return render(request, "leave.html", context)


@login_required
def apply_leave_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        messages.error(request, "You are not logged in as an employee.")
        return redirect("accounts:login")

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.save()
            messages.success(request, "Leave request submitted successfully!")
            return redirect("employees:leave")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeaveRequestForm()

    context = {"form": form}
    return render(request, "apply_leave.html", context)


# ===============================
# Payroll
# ===============================
@login_required
def payroll_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:login")

    payrolls = Payroll.objects.filter(employee=employee).order_by('-month')
    current_salary = payrolls.first() if payrolls.exists() else None
    ytd_earnings = payrolls.aggregate(total_gross=Sum('gross_salary'))['total_gross'] or 0

    context = {
        'payrolls': payrolls,
        'current_salary': current_salary,
        'ytd_earnings': ytd_earnings,
    }
    return render(request, 'payroll.html', context)


# ===============================
# Performance
# ===============================
@login_required
def performance_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        return render(request, "performance.html", {"error": "Employee profile not found."})

    performance = Performance.objects.filter(employee=employee).first()
    skill_list = []

    if performance:
        skills = performance.skills.select_related("skill").all()
        skill_list = [{"name": ps.skill.name, "value": ps.value, "color": ps.skill.color} for ps in skills]

    feedbacks = performance.feedbacks.all() if performance else []

    context = {
        "employee": employee,
        "performance": performance,
        "skills": skill_list,
        "feedbacks": feedbacks,
    }
    return render(request, "performance.html", context)


# ===============================
# Projects
# ===============================
@login_required
def projects_view(request):
    # Get the logged-in employee
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:login")

    # Fetch projects assigned to this employee
    employee_projects = Project.objects.filter(assigned_to=employee)

    # Calculate employee-specific success rate
    if employee_projects.exists():
        success_rate = round(sum(p.progress for p in employee_projects) / employee_projects.count())
    else:
        success_rate = 0

    # Prepare project stats
    project_stats = [
        {
            "label": "Active Projects",
            "value": employee_projects.filter(status="In Progress").count(),
            "icon": "fas fa-tasks",
            "icon_color": "text-blue-600",
            "icon_bg": "bg-blue-100 dark:bg-blue-900"
        },
        {
            "label": "Completed",
            "value": employee_projects.filter(status="Completed").count(),
            "icon": "fas fa-check-circle",
            "icon_color": "text-green-600",
            "icon_bg": "bg-green-100 dark:bg-green-900"
        },
        {
            "label": "Pending Review",
            "value": employee_projects.filter(status="Review").count(),
            "icon": "fas fa-clock",
            "icon_color": "text-yellow-600",
            "icon_bg": "bg-yellow-100 dark:bg-yellow-900"
        },
        {
            "label": "Success Rate",
            "value": success_rate,
            "icon": "fas fa-percentage",
            "icon_color": "text-purple-600",
            "icon_bg": "bg-purple-100 dark:bg-purple-900"
        },
    ]

    context = {
        "projects": employee_projects,
        "project_stats": project_stats,
    }

    return render(request, "projects.html", context)

#--------------------------------
# Project Detail View
#--------------------------------

@login_required
def project_detail_view(request, pk):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:login")

    try:
        project = Project.objects.get(pk=pk, assigned_to=employee)
    except Project.DoesNotExist:
        return redirect("employees:projects")  # redirect if project not found

    context = {
        "project": project,
        "assigned_by_initials": "".join([n[0] for n in project.assigned_by.split()][:2]).upper()
    }

    return render(request, "project_detail.html", context)

# ===============================
# Other Pages
# ===============================
# employees/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import EmployeeProfile
from .models import Document  # Assuming you have a Document model

def get_logged_in_employee(request):
    """
    Retrieve the currently logged-in employee using session.
    Returns None if not found.
    """
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return None
    try:
        return EmployeeProfile.objects.get(employee_id=employee_id)
    except EmployeeProfile.DoesNotExist:
        return None

@login_required
def documents_view(request):
    """
    Display documents page for the logged-in employee.
    """
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect('accounts:login')

    # Fetch documents by category
    # Assuming Document model has fields: category, title, file, view_only (bool)
    personal_docs = Document.objects.filter(employee=employee, category='Personal')
    payroll_docs = Document.objects.filter(employee=employee, category='Payroll')
    company_policies = Document.objects.filter(employee=employee, category='Company Policies')
    certificates = Document.objects.filter(employee=employee, category='Certificates')
    forms = Document.objects.filter(employee=employee, category='Forms')
    it_docs = Document.objects.filter(employee=employee, category='IT')

    context = {
        'personal_docs': personal_docs,
        'payroll_docs': payroll_docs,
        'company_policies': company_policies,
        'certificates': certificates,
        'forms': forms,
        'it_docs': it_docs,
        'employee': employee,
    }

    return render(request, 'documents.html', context)

#===============================
# Profile View
#===============================

# employees/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import EmployeeProfile
from .models import EmployeeData


@login_required
def profile_view(request):
    """
    Display employee profile and allow editing of EmployeeData.
    """
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:login")

    # Try to fetch EmployeeData or create blank if not exist
    profile, created = EmployeeData.objects.get_or_create(employee=employee)

    context = {
        "employee": employee,
        "profile": profile,
    }

    return render(request, "profile.html", context)

#===============================
#Edit Profile View
#===============================

@login_required
def edit_profile(request):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect('accounts:login')

    # Get or create EmployeeData
    profile, _ = EmployeeData.objects.get_or_create(employee=employee)

    if request.method == "POST":
        # update fields
        profile.full_name = request.POST.get("full_name", profile.full_name)
        profile.designation = request.POST.get("designation", profile.designation)
        profile.department = request.POST.get("department", profile.department)
        profile.joining_date = request.POST.get("joining_date", profile.joining_date)
        profile.address = request.POST.get("address", profile.address)
        profile.emergency_contact = request.POST.get("emergency_contact", profile.emergency_contact)
        profile.role = request.POST.get("role", profile.role)
        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("employees:profile")

    context = {"profile": profile, "employee": employee}
    return render(request, "edit_profile.html", context)

@login_required
def support(request):
    return render(request, 'support.html')
