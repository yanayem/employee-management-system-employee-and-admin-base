from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta  # <-- correct import
from django.db.models import Sum, Q, Count
from accounts.models import EmployeeProfile
from .models import (
    Attendance, LeaveRequest, Payroll, Performance, Project, EmployeeData, Document
)
from .forms import LeaveRequestForm
from django.utils.timezone import make_aware

# -------------------------------
# Helper function
# -------------------------------
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
# DASHBOARD VIEW
# ===============================

# employees/views.py
from .models import Document, Payroll
from django.urls import reverse

def dashboard_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:employee_login_page")

    today = timezone.localdate()

    # -----------------------------
    # Today Attendance
    # -----------------------------
    today_record, _ = Attendance.objects.get_or_create(employee=employee, date=today)

    # -----------------------------
    # Monthly Attendance %
    # -----------------------------
    month_records = Attendance.objects.filter(employee=employee, date__month=today.month).order_by('date')
    total_present = month_records.filter(status="Present").count()
    total_absent = month_records.filter(status="Absent").count()
    late_days = month_records.filter(status="Late").count()
    attendance_percent = round((total_present / month_records.count()) * 100, 1) if month_records.exists() else 0

    # -----------------------------
    # Weekly Attendance % (Last 4 Weeks)
    # -----------------------------
    weekly_percentages = []
    week_labels = []
    for i in range(3, -1, -1):
        start_of_week = today - timedelta(days=today.weekday() + i*7)
        end_of_week = start_of_week + timedelta(days=6)
        week_records = Attendance.objects.filter(employee=employee, date__gte=start_of_week, date__lte=end_of_week)
        total_days = week_records.count()
        present_days = week_records.filter(status="Present").count()
        percent = round((present_days / total_days) * 100, 1) if total_days else 0
        weekly_percentages.append(percent)
        week_labels.append(f"{start_of_week.strftime('%d %b')}")

    # This week % (for card)
    this_week_records = Attendance.objects.filter(employee=employee, date__gte=today - timedelta(days=today.weekday()))
    week_present = this_week_records.filter(status="Present").count()
    week_total_days = this_week_records.count()
    this_week_percent = round((week_present / week_total_days) * 100, 1) if week_total_days else 0

    # -----------------------------
    # Weekly Hours
    # -----------------------------
    week_records = Attendance.objects.filter(employee=employee, date__gte=today - timedelta(days=7))
    total_week_hours = sum(
        ((timezone.datetime.combine(r.date, r.check_out) - timezone.datetime.combine(r.date, r.check_in)).total_seconds() / 3600)
        for r in week_records if r.check_in and r.check_out
    )
    total_week_hours_formatted = f"{int(total_week_hours)}h {int((total_week_hours*60)%60)}m"

    # -----------------------------
    # Leave Balances
    # -----------------------------
    leave_requests = LeaveRequest.objects.filter(employee=employee, status="Approved")
    balances = {
        "Annual": 18 - sum(l.total_days() for l in leave_requests.filter(leave_type="Annual")),
        "Sick": 8 - sum(l.total_days() for l in leave_requests.filter(leave_type="Sick")),
        "Personal": 5 - sum(l.total_days() for l in leave_requests.filter(leave_type="Personal")),
        "Maternity": 90 - sum(l.total_days() for l in leave_requests.filter(leave_type="Maternity")),
        "Emergency": 5 - sum(l.total_days() for l in leave_requests.filter(leave_type="Emergency")),
    }

    # -----------------------------
    # Payrolls
    # -----------------------------
    payrolls = Payroll.objects.filter(employee=employee).order_by("-month")
    ytd_earnings = payrolls.aggregate(total_gross=Sum("gross_salary"))["total_gross"] or 0

    # -----------------------------
    # Projects
    # -----------------------------
    projects = Project.objects.filter(assigned_to=employee)
    active_projects = projects.filter(status="In Progress").count()

    # -----------------------------
    # Performance
    # -----------------------------
    performance = Performance.objects.filter(employee=employee).first()
    skill_labels = []
    skill_values = []
    if performance:
        for ps in performance.skills.all():
            skill_labels.append(ps.skill.name)
            skill_values.append(ps.value)

    # -----------------------------
    # Recent Activity (Leave, Project, Payslip)
    # -----------------------------
    recent_activity = []

        # Leaves (created_at should already be aware)
    for l in leave_requests.order_by("-created_at")[:3]:
        recent_activity.append({
            "type": "Leave",
            "icon": "fa-calendar-check",
            "title": f"{l.leave_type} Leave",
            "desc": f"{l.start_date} to {l.end_date}",
            "status": l.status,
            "date": timezone.localtime(l.created_at),  # ensure aware
            "link": None,
        })

    # Projects (use aware now)
    for p in projects.order_by("-id")[:3]:
        recent_activity.append({
            "type": "Project",
            "icon": "fa-tasks",
            "title": p.title,
            "desc": f"{p.progress}%",
            "status": p.status,
            "date": timezone.now(),  # already aware
            "link": None,
        })

    # Payslips (convert date to aware datetime)
    for pay in payrolls[:3]:
        pay_naive = datetime.combine(pay.month, datetime.min.time())  # naive datetime
        pay_aware = make_aware(pay_naive)  # convert to aware
        recent_activity.append({
            "type": "Payslip",
            "icon": "fa-file-invoice-dollar",
            "title": pay.month.strftime("%B %Y"),
            "desc": "Download Payslip",
            "status": "Ready",
            "date": pay_aware,  # aware datetime
            "link": pay.payslip_file.url if pay.payslip_file else None,
        })

    # Sort all activities safely
    recent_activity.sort(key=lambda x: x["date"], reverse=True)


    # -----------------------------
    # Context
    # -----------------------------
    context = {
        "employee": employee,
        "today_record": today_record,
        "attendance_percent": attendance_percent,
        "this_week_percent": this_week_percent,
        "week_labels": week_labels,
        "weekly_percentages": weekly_percentages,
        "total_week_hours": total_week_hours_formatted,
        "balances": balances,
        "ytd_earnings": ytd_earnings,
        "projects": projects,
        "active_projects": active_projects,
        "skill_labels": skill_labels,
        "skill_values": skill_values,
        "recent_activity": recent_activity,
    }

    return render(request, "employee_dashboard.html", context)

# ===============================
# Attendance
# ===============================
from django.shortcuts import render
from django.utils import timezone
from employees.models import Attendance, EmployeeProfile
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from employees.models import Attendance

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from employees.models import Attendance
from django.contrib import messages

def attendance_view(request):
    today = timezone.localdate()
    employee = get_logged_in_employee(request)
    if not employee:
        messages.error(request, "You must be logged in to mark attendance.")
        return redirect("accounts:employee_login_page")

    # Handle POST for Check In / Check Out
    if request.method == "POST":
        action = request.POST.get("action")
        attendance_record, created = Attendance.objects.get_or_create(employee=employee, date=today)

        now = timezone.localtime()
        current_time = now.time()

        if action == "check_in":
            if not attendance_record.check_in:
                attendance_record.check_in = current_time
                # Set status
                if current_time <= datetime.strptime("09:30:00", "%H:%M:%S").time():
                    attendance_record.status = "Present"
                else:
                    attendance_record.status = "Late"
                attendance_record.save()
                messages.success(request, f"Checked in at {current_time.strftime('%H:%M')}")
            else:
                messages.warning(request, f"You already checked in at {attendance_record.check_in.strftime('%H:%M')}")
        elif action == "check_out":
            if not attendance_record.check_out:
                attendance_record.check_out = current_time
                # if check_in not set yet, mark as Late
                if not attendance_record.check_in:
                    attendance_record.status = "Late"
                attendance_record.save()
                messages.success(request, f"Checked out at {current_time.strftime('%H:%M')}")
            else:
                messages.warning(request, f"You already checked out at {attendance_record.check_out.strftime('%H:%M')}")
        return redirect("employees:attendance")  # redirect to refresh page

    # ==========================
    # GET: Display attendance
    # ==========================
    # Today's record
    today_record = Attendance.objects.filter(employee=employee, date=today).first()

    # Weekly data (current week)
    week_start = today - timedelta(days=today.weekday())
    week_records = Attendance.objects.filter(employee=employee, date__gte=week_start, date__lte=today)
    week_days_present = week_records.filter(status='Present').count()
    week_total_days = week_records.count()
    total_week_hours = sum(
        ((datetime.combine(r.date, r.check_out) - datetime.combine(r.date, r.check_in)).total_seconds() / 3600)
        for r in week_records if r.check_in and r.check_out
    )

    # Monthly data
    month_records = Attendance.objects.filter(employee=employee, date__month=today.month, date__year=today.year)
    late_days = month_records.filter(status='Late').count()
    attendance_percent = round((month_records.filter(status='Present').count() / month_records.count()) * 100, 1) if month_records.exists() else 0

    context = {
        'today_record': today_record,
        'week_days_present': week_days_present,
        'week_total_days': week_total_days,
        'total_week_hours': round(total_week_hours, 2),
        'attendance_percent': attendance_percent,
        'late_days': late_days,
        'month_records': month_records
    }

    return render(request, 'attendance.html', context)

# ===============================
# Leave
# ===============================
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


#=================
#
#=======================

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


from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Project
from .utils import get_project_status  # if in utils.py

def projects_view(request):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:login")

    projects = Project.objects.filter(assigned_to=employee)

    # Attach dynamic status to each project
    for project in projects:
        status_info = get_project_status(project)
        project.dynamic_status = status_info["label"]
        project.status_badge = status_info["badge"]

    # Success rate
    success_rate = (
        round(sum(p.progress for p in projects) / projects.count())
        if projects.exists()
        else 0
    )

    project_stats = [
        {
            "label": "Active Projects",
            "value": len([p for p in projects if p.dynamic_status == "In Progress"]),
            "icon": "fas fa-tasks",
            "icon_color": "text-blue-600",
            "icon_bg": "bg-blue-100 dark:bg-blue-900"
        },
        {
            "label": "Completed",
            "value": len([p for p in projects if p.dynamic_status == "Completed"]),
            "icon": "fas fa-check-circle",
            "icon_color": "text-green-600",
            "icon_bg": "bg-green-100 dark:bg-green-900"
        },
        {
            "label": "Overdue",
            "value": len([p for p in projects if p.dynamic_status == "Overdue"]),
            "icon": "fas fa-exclamation-circle",
            "icon_color": "text-red-600",
            "icon_bg": "bg-red-100 dark:bg-red-900"
        },
        {
            "label": "Success Rate",
            "value": f"{success_rate}%",
            "icon": "fas fa-percentage",
            "icon_color": "text-purple-600",
            "icon_bg": "bg-purple-100 dark:bg-purple-900"
        },
    ]

    return render(request, "projects.html", {
        "projects": projects,
        "project_stats": project_stats,
    })

#--------------------------------
# Project Detail View
#--------------------------------
from datetime import date
from django.shortcuts import render, redirect
from .models import Project

def project_detail_view(request, pk):
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:login")

    try:
        project = Project.objects.get(pk=pk, assigned_to=employee)
    except Project.DoesNotExist:
        return redirect("employees:projects")

    # Ensure progress is max 100
    project.progress = min(project.progress, 100)

    context = {
        "project": project,
        "assigned_by_initials": "".join([n[0] for n in project.assigned_by.split()][:2]).upper(),
        "today": date.today(),
    }

    return render(request, "project_detail.html", context)

# ===============================
# Other Pages
# ===============================
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EmployeeData
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EmployeeProfile

def profile_view(request):
    # Get the employee profile from session using your helper
    employee = get_logged_in_employee(request)
    if not employee:
        return redirect("accounts:employee_login_page")

    profile = employee

    if request.method == "POST":
        # --- 1. Security / Password Change ---
        if "new_password" in request.POST:
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password and new_password == confirm_password:
                profile.password = new_password  # Note: Use make_password() in production
                profile.save()
                messages.success(request, "Password changed successfully!")
            else:
                messages.error(request, "Passwords do not match!")
            return redirect("employees:profile")

        # --- 2. Emergency Info Update ---
        elif "emergency_name" in request.POST:
            profile.emergency_name = request.POST.get("emergency_name")
            profile.emergency_relation = request.POST.get("emergency_relation")
            profile.emergency_contact = request.POST.get("emergency_contact")
            profile.emergency_address = request.POST.get("emergency_address")
            profile.save()
            messages.success(request, "Emergency info updated!")
            return redirect("employees:profile")

        # --- 3. General Profile & Avatar Update ---
        else:
            # Update text fields
            profile.full_name = request.POST.get("full_name", profile.full_name)
            profile.phone = request.POST.get("phone", profile.phone)
            profile.department = request.POST.get("department", profile.department)
            profile.designation = request.POST.get("designation", profile.designation)
            profile.role = request.POST.get("role", profile.role)
            profile.gender = request.POST.get("gender", profile.gender)
            
            joining_date = request.POST.get("joining_date")
            if joining_date:
                profile.joining_date = joining_date
            profile.address = request.POST.get("address", profile.address)

            # --- Avatar Logic: The "Auto Save" Part ---
            # If a new file is uploaded via the camera button
            if request.FILES.get("avatar"):
                profile.avatar = request.FILES["avatar"]
            
            # If the delete button was clicked (it sends 'on' or '1' via the checkbox)
            elif request.POST.get("remove_avatar") in ["1", "on"]:
                if profile.avatar:
                    profile.avatar.delete(save=False) # Physically delete the old file
                profile.avatar = None

            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("employees:profile")

    return render(request, "profile.html", {"profile": profile})

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required

def base_notifications(request):
    """
    Prepare notifications for the topbar dropdown.
    No separate page is needed.
    """
    # Example: dynamic notifications (replace with your DB queries)
    notifications = [
        {"title": "New Task Assigned", "message": "You have a new task.", "link": "#", "timestamp": timezone.now() - timedelta(minutes=5), "is_read": False},
        {"title": "Leave Approved", "message": "Your leave request approved.", "link": "#", "timestamp": timezone.now() - timedelta(hours=2), "is_read": True},
        {"title": "Payroll Credited", "message": "Salary credited for January.", "link": "#", "timestamp": timezone.now() - timedelta(days=1), "is_read": False},
        # Add more dynamic notifications here...
    ]

    # Keep only latest 20
    notifications = sorted(notifications, key=lambda n: n["timestamp"], reverse=True)[:20]

    # Unread count
    unread_count = sum(1 for n in notifications if not n["is_read"])

    return {
        "notifications": notifications,
        "unread_count": unread_count,
    }
