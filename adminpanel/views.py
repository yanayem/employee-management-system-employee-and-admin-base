from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import EmployeeProfile
from employees.models import Project, LeaveRequest, Attendance, Performance
from datetime import datetime, timedelta
from django.db.models import Count

@login_required(login_url="/admin/")
def dashboard(request):
    # Stats cards
    total_employees = EmployeeProfile.objects.count()
    total_projects = Project.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status="Pending").count()
    today_attendance = Attendance.objects.filter(date=datetime.today().date()).count()

    # Project progress (example)
    projects = Project.objects.all()
    project_labels = [p.title for p in projects[:5]]  # Top 5 projects
    project_progress = [p.progress for p in projects[:5]]
    
    if not project_labels:
        project_labels = ['Project 1', 'Project 2', 'Project 3', 'Project 4', 'Project 5']
        project_progress = [10, 40, 70, 20, 90]

    # Leave status counts
    leave_status_counts = LeaveRequest.objects.values('status').annotate(count=Count('status'))
    leave_status_dict = {"Pending": 0, "Approved": 0, "Rejected": 0}
    for item in leave_status_counts:
        leave_status_dict[item['status']] = item['count']

    # Monthly attendance (last 6 months)
    monthly_labels = []
    monthly_attendance = []
    today = datetime.today()
    for i in range(5, -1, -1):
        month = today - timedelta(days=i*30)
        label = month.strftime('%b %Y')
        monthly_labels.append(label)
        count = Attendance.objects.filter(date__year=month.year, date__month=month.month).count()
        monthly_attendance.append(count)

    # Performance rating (example)
    performance = Performance.objects.all()
    employee_names = [p.employee.full_name for p in performance[:5]]
    performance_scores = [p.overall_rating() for p in performance[:5]] if performance else [50,70,80,60,90]

    context = {
        "total_employees": total_employees,
        "total_projects": total_projects,
        "pending_leaves": pending_leaves,
        "today_attendance": today_attendance,
        "project_labels": project_labels,
        "project_progress": project_progress,
        "leave_status_dict": leave_status_dict,
        "monthly_labels": monthly_labels,
        "monthly_attendance": monthly_attendance,
        "employee_names": employee_names,
        "performance_scores": performance_scores,
    }

    return render(request, "admindashboard.html", context)


#==============
# Payroll View
#==============
#==============
# Payroll View
#==============
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from employees.models import Payroll
from accounts.models import EmployeeProfile
from django.contrib import messages
from datetime import datetime



#----------------------
# LIST PAGE
#----------------------
@login_required
def payroll_list(request):
    payrolls = Payroll.objects.select_related("employee").order_by("-month")
    return render(request, "adminpayroll.html", {"payrolls": payrolls})


#----------------------
# ADD PAYROLL
#----------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employees.models import Payroll
from accounts.models import EmployeeProfile
from datetime import datetime

#----------------------
# PAYROLL LIST
#----------------------
@login_required
def payroll_list(request):
    payrolls = Payroll.objects.select_related("employee").order_by("-month")
    return render(request, "adminpayroll.html", {"payrolls": payrolls})


#----------------------
# ADD PAYROLL
#----------------------
@login_required
def payroll_add(request):
    employees = EmployeeProfile.objects.all()

    if request.method == "POST":
        employee_id = request.POST.get("employee")
        month_value = request.POST.get("month")
        gross_salary = request.POST.get("gross_salary")
        deductions = request.POST.get("deductions")
        net_pay = request.POST.get("net_pay")

        # Validate month format
        try:
            month_clean = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
        except ValueError:
            messages.error(request, "Invalid month format. Please select again.")
            return render(request, "adminpayroll_form.html", {
                "employees": employees,
                "payroll": None
            })

        # Validate numeric inputs
        if not gross_salary or not deductions or not net_pay:
            messages.error(request, "Please fill in all salary fields.")
            return render(request, "adminpayroll_form.html", {
                "employees": employees,
                "payroll": None
            })

        # Create Payroll
        Payroll.objects.create(
            employee_id=employee_id,
            month=month_clean,
            gross_salary=gross_salary,
            deductions=deductions,
            net_pay=net_pay,
        )
        messages.success(request, "Payroll added successfully.")
        return redirect("admin_payroll")

    return render(request, "adminpayroll_form.html", {
        "employees": employees,
        "payroll": None
    })


#----------------------
# EDIT PAYROLL
#----------------------
@login_required
def payroll_edit(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    employees = EmployeeProfile.objects.all()

    if request.method == "POST":
        employee_id = request.POST.get("employee")
        month_value = request.POST.get("month")
        gross_salary = request.POST.get("gross_salary")
        deductions = request.POST.get("deductions")
        net_pay = request.POST.get("net_pay")

        # Validate month format
        try:
            month_clean = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
        except ValueError:
            messages.error(request, "Invalid month format. Please select again.")
            return render(request, "adminpayroll_form.html", {
                "employees": employees,
                "payroll": payroll
            })

        # Validate numeric inputs
        if not gross_salary or not deductions or not net_pay:
            messages.error(request, "Please fill in all salary fields.")
            return render(request, "adminpayroll_form.html", {
                "employees": employees,
                "payroll": payroll
            })

        # Save edits
        payroll.employee_id = employee_id
        payroll.month = month_clean
        payroll.gross_salary = gross_salary
        payroll.deductions = deductions
        payroll.net_pay = net_pay
        payroll.save()

        messages.success(request, "Payroll updated successfully.")
        return redirect("admin_payroll")

    return render(request, "adminpayroll_form.html", {
        "payroll": payroll,
        "employees": employees
    })


#----------------------
# DELETE PAYROLL
#----------------------
@login_required
def payroll_delete(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    payroll.delete()
    messages.success(request, "Payroll deleted successfully.")
    return redirect("admin_payroll")


#----------------------
# GENERATE PDF SALARY SLIP
#----------------------
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from employees.models import Payroll

@login_required
def payroll_slip(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="slip_{payroll.id}.pdf"'

    width, height = A4
    p = canvas.Canvas(response, pagesize=A4)

    # BACKGROUND COLOR HEADER
    p.setFillColorRGB(0.1, 0.3, 0.7)  # dark blue
    p.rect(0, height-80, width, 80, fill=True, stroke=False)

    # HEADER TEXT
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.white)
    p.drawCentredString(width/2, height-50, "Salary Slip")

    # LINE UNDER HEADER
    p.setStrokeColor(colors.darkblue)
    p.setLineWidth(2)
    p.line(30, height-85, width-30, height-85)

    # EMPLOYEE DETAILS BOX
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.darkblue)
    p.drawString(50, height-120, "Employee Details")
    
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    p.drawString(60, height-140, f"Name       : {payroll.employee.full_name}")
    p.drawString(60, height-160, f"Employee ID: {payroll.employee.employee_id}")
    p.drawString(60, height-180, f"Month      : {payroll.month.strftime('%B %Y')}")

    # SALARY DETAILS BOX
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.darkblue)
    p.drawString(50, height-220, "Salary Details")
    
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    p.drawString(60, height-240, f"Gross Salary : ${payroll.gross_salary}")
    p.drawString(60, height-260, f"Deductions   : ${payroll.deductions}")
    p.drawString(60, height-280, f"Net Pay      : ${payroll.net_pay}")

    # FOOTER
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.gray)
    p.drawCentredString(width/2, 30, "Generated by Managely HR System")

    p.showPage()
    p.save()

    return response

#----------------------
# ADMIN EMPLOYEE LIST
#----------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.models import EmployeeProfile
from django.contrib.auth.decorators import login_required

@login_required
def admin_employee_list(request):
    # Admin can see all employees
    employees = EmployeeProfile.objects.all()

    # Search
    q = request.GET.get("q", "")
    if q:
        employees = employees.filter(
            Q(full_name__icontains=q) |
            Q(employee_id__icontains=q) |
            Q(phone__icontains=q)
        )

    # Department filter
    department = request.GET.get("department", "")
    if department:
        employees = employees.filter(department=department)

    # Get distinct departments
    departments = EmployeeProfile.objects.values_list('department', flat=True).distinct()

    # Admin and HR can activate or deactivate employees
    if request.method == "POST":
        if 'action' in request.POST:
            action = request.POST['action']
            employee_ids = request.POST.getlist('employee_ids')

            if action == 'activate':
                EmployeeProfile.objects.filter(id__in=employee_ids).update(is_active=True)
                messages.success(request, "Selected employees have been activated.")
            elif action == 'deactivate':
                EmployeeProfile.objects.filter(id__in=employee_ids).update(is_active=False)
                messages.success(request, "Selected employees have been deactivated.")
        
        return redirect('admin_employee_list')

    return render(request, "admin_employee_list.html", {
        "employees": employees,
        "departments": departments
    })

#----------------------
# SEND MAIL TO EMPLOYEE
#----------------------
@login_required
def admin_employee_message(request, pk):
    employee = get_object_or_404(EmployeeProfile, pk=pk)

    if request.method == "POST":
        subject = request.POST.get("subject")
        message_body = request.POST.get("message")

        if not subject or not message_body:
            messages.error(request, "Subject and message cannot be empty.")
        elif not getattr(employee, 'email', None):
            messages.error(request, f"{employee.full_name} does not have an email address.")
        else:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [employee.email],
                fail_silently=False,
            )
            messages.success(request, f"Mail sent to {employee.full_name}")
            return redirect('admin_employee_list')

    return render(request, "admin_employee_message.html", {"employee": employee})

#======================
# ADD NEW EMPLOYEE VIEW
#======================
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import EmployeeProfile
from datetime import datetime
import re
from django.contrib.auth.decorators import login_required

@login_required
def admin_employee_add(request):
    """
    Admin can add a new employee with only name and phone.
    Employee ID is auto-generated as EMYYYYNNN and shown in form.
    Temporary password is last 6 digits of phone number.
    """
    # Generate auto Employee ID for display
    year = datetime.now().year
    last_employee = EmployeeProfile.objects.order_by('-id').first()
    if last_employee:
        match = re.search(r'EM\d{4}(\d+)$', last_employee.employee_id)
        last_number = int(match.group(1)) if match else 0
        new_number = last_number + 1
    else:
        new_number = 1

    auto_employee_id = f"EM{year}{new_number:03d}"

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")

        if not full_name or not phone or len(phone) < 6:
            messages.error(request, "Please enter a valid name and phone number (at least 6 digits).")
            return redirect('admin_employee_add')

        # Temporary password: last 6 digits of phone
        temp_password = phone[-6:]

        # Create employee
        employee = EmployeeProfile(
            employee_id=auto_employee_id,
            full_name=full_name,
            phone=phone,
            first_login=True
        )
        employee.set_password(temp_password)
        employee.save()

        messages.success(
            request,
            f"Employee {full_name} created with Employee ID {auto_employee_id} and temporary password: {temp_password}"
        )
        return redirect('admin_employee_list')

    return render(request, "admin_employee_add.html", {"employee_id": auto_employee_id})


@login_required
def admin_employee_view(request, pk):
    """
    View to see employee details.
    """
    employee = get_object_or_404(EmployeeProfile, pk=pk)

    return render(request, "admin_employee_view.html", {
        'employee': employee
    })

@login_required
def admin_employee_edit(request, pk):
    employee = get_object_or_404(EmployeeProfile, pk=pk)

    if request.method == 'POST':
        employee.full_name = request.POST.get("full_name")
        employee.phone = request.POST.get("phone")
        employee.email = request.POST.get("email")
        employee.department = request.POST.get("department")
        employee.role = request.POST.get("role")
        employee.save()

        messages.success(request, f"Employee {employee.full_name} has been updated.")
        return redirect('admin_employee_list')

    return render(request, "admin_employee_edit.html", {
        'employee': employee
    })
    

@login_required
def admin_employee_activate(request, pk):
    employee = get_object_or_404(EmployeeProfile, pk=pk)
    employee.is_active = True
    employee.save()
    messages.success(request, f"Employee {employee.full_name} has been activated.")
    return redirect('admin_employee_list')


@login_required
def admin_employee_deactivate(request, pk):
    employee = get_object_or_404(EmployeeProfile, pk=pk)
    
    employee.is_active = False  # Mark as inactive
    employee.save()

    messages.success(request, f"Employee {employee.full_name} has been deactivated.")
    return redirect('admin_employee_list')

#======================
# DEPARTMENT LIST VIEW
#======================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/')
def admin_department_list(request):
    """
    Render a static frontend-only department page for the admin portal.
    """
    return render(request, "admin_department_list.html")


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import EmployeeProfile
from employees.models import Attendance
from django.utils import timezone
from django.db.models import Q

@login_required(login_url='/admin/')
def admin_attendance_view(request):
    """
    Admin view to check attendance of all employees
    """
    # Optional filters
    employee_id = request.GET.get("employee_id", "")
    date_filter = request.GET.get("date", "")

    attendances = Attendance.objects.select_related('employee').order_by('-date')

    if employee_id:
        attendances = attendances.filter(employee__employee_id__icontains=employee_id)

    if date_filter:
        attendances = attendances.filter(date=date_filter)

    employees = EmployeeProfile.objects.all()  # for dropdown filter

    context = {
        "attendances": attendances,
        "employees": employees,
        "employee_id": employee_id,
        "date_filter": date_filter,
    }
    return render(request, "admin_attendance.html", context)

#----------------------
# ADMIN ATTENDANCE VIEW
#----------------------

@login_required(login_url='/admin/')
def admin_attendance_view(request):
    """
    Admin view to check and update attendance of all employees
    """
    # Filters
    employee_id = request.GET.get("employee_id", "")
    date_filter = request.GET.get("date", "")

    attendances = Attendance.objects.select_related('employee').order_by('-date')

    if employee_id:
        attendances = attendances.filter(employee__employee_id__icontains=employee_id)

    if date_filter:
        attendances = attendances.filter(date=date_filter)

    employees = EmployeeProfile.objects.all()  # for dropdown filter

    # Handle attendance updates
    if request.method == "POST":
        att_id = request.POST.get("attendance_id")
        status = request.POST.get("status")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        attendance = get_object_or_404(Attendance, pk=att_id)

        if status in ['Present', 'Absent', 'Late']:
            attendance.status = status

        if check_in:
            attendance.check_in = check_in

        if check_out:
            attendance.check_out = check_out

        attendance.save()
        return redirect(request.path + f"?employee_id={employee_id}&date={date_filter}")

    context = {
        "attendances": attendances,
        "employees": employees,
        "employee_id": employee_id,
        "date_filter": date_filter,
    }
    return render(request, "admin_attendance.html", context)

#======================
#Manage leave requests
#======================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import EmployeeProfile
from employees.models import LeaveRequest

@login_required
def admin_leave_list(request):
    # Only for admin users
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to view this page.")
        return redirect("dashboard")  # or wherever you want

    leave_requests = LeaveRequest.objects.select_related("employee").order_by("-created_at")

    context = {
        "leave_requests": leave_requests,
    }
    return render(request, "admin_leave_list.html", context)


@login_required
def admin_leave_update(request, pk, action):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("dashboard")

    leave = get_object_or_404(LeaveRequest, pk=pk)
    
    if action.lower() == "approve":
        leave.status = "Approved"
        messages.success(request, f"{leave.employee.full_name}'s leave approved.")
    elif action.lower() == "reject":
        leave.status = "Rejected"
        messages.success(request, f"{leave.employee.full_name}'s leave rejected.")
    else:
        messages.error(request, "Invalid action.")
        return redirect("admin_leave_list")

    leave.save()
    return redirect("admin_leave_list")
  
  
#======================
# Performance Views
#======================

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import EmployeeProfile
from employees.models import Performance

@login_required
def admin_performance_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    employees = EmployeeProfile.objects.all().select_related()

    # Fetch performance for each employee
    performance_list = []
    for emp in employees:
        perf = Performance.objects.filter(employee=emp).first()
        overall = perf.overall_rating() if perf else 0
        performance_list.append({
            "employee": emp,
            "performance": perf,
            "overall_rating": overall
        })

    context = {
        "performance_list": performance_list
    }
    return render(request, "admin_performance_list.html", context)

@login_required
def admin_performance_detail(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')

    employee = get_object_or_404(EmployeeProfile, pk=pk)
    performance = Performance.objects.filter(employee=employee).first()

    if performance:
        skills = performance.skills.select_related("skill").all()  # Keep as queryset of PerformanceSkill
    else:
        skills = []

    feedbacks = performance.feedbacks.all() if performance else []

    context = {
        "employee": employee,
        "performance": performance,
        "skills": skills,   # Pass objects directly
        "feedbacks": feedbacks,
    }
    return render(request, "admin_performance_detail.html", context)

  
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import EmployeeProfile
from employees.models import Performance, PerformanceSkill, Skill, Feedback

# ---------- Add/Edit Performance ----------
@login_required
def admin_performance_edit(request, employee_id):
    if not request.user.is_staff:
        return redirect('dashboard')

    employee = get_object_or_404(EmployeeProfile, id=employee_id)
    performance, created = Performance.objects.get_or_create(employee=employee)

    if request.method == "POST":
        performance.goals_achieved = request.POST.get("goals_achieved", 0)
        performance.total_goals = request.POST.get("total_goals", 0)
        performance.projects_completed = request.POST.get("projects_completed", 0)
        performance.achievements = request.POST.get("achievements", 0)
        performance.manager_comment = request.POST.get("manager_comment", "")
        performance.save()
        messages.success(request, "Performance updated successfully.")
        return redirect("admin_performance_detail", pk=employee.id)

    context = {"employee": employee, "performance": performance}
    return render(request, "admin_performance_edit.html", context)

# ---------- Add/Edit Skills ----------
@login_required
def admin_performance_skill_edit(request, performance_id, skill_id=None):
    if not request.user.is_staff:
        return redirect('dashboard')

    performance = get_object_or_404(Performance, id=performance_id)
    if skill_id:
        ps = get_object_or_404(PerformanceSkill, id=skill_id)
    else:
        ps = None

    if request.method == "POST":
        skill_name = request.POST.get("skill_name")
        value = int(request.POST.get("value", 0))
        color = request.POST.get("color", "blue")

        skill, _ = Skill.objects.get_or_create(name=skill_name, defaults={"color": color})

        if ps:
            ps.skill = skill
            ps.value = value
            ps.save()
            messages.success(request, "Skill updated.")
        else:
            PerformanceSkill.objects.create(performance=performance, skill=skill, value=value)
            messages.success(request, "Skill added.")

        return redirect("admin_performance_detail", pk=performance.employee.id)

    context = {"performance": performance, "ps": ps}
    return render(request, "admin_performance_skill_form.html", context)

# ---------- Delete Skill ----------
@login_required
def admin_performance_skill_delete(request, skill_id):
    ps = get_object_or_404(PerformanceSkill, id=skill_id)
    employee_id = ps.performance.employee.id
    ps.delete()
    messages.success(request, "Skill deleted.")
    return redirect("admin_performance_detail", pk=employee_id)

# ---------- Add Feedback ----------
@login_required
def admin_performance_feedback_add(request, performance_id):
    if not request.user.is_staff:
        return redirect('dashboard')

    performance = get_object_or_404(Performance, id=performance_id)

    if request.method == "POST":
        author = request.POST.get("author")
        text = request.POST.get("text")
        color = request.POST.get("color", "blue")
        if text and author:
            Feedback.objects.create(performance=performance, author=author, text=text, color=color)
            messages.success(request, "Feedback added successfully.")
        return redirect("admin_performance_detail", pk=performance.employee.id)

    return render(request, "admin_performance_feedback_form.html", {"performance": performance})

# ---------- Delete Feedback ----------
@login_required
def admin_performance_feedback_delete(request, feedback_id):
    fb = get_object_or_404(Feedback, id=feedback_id)
    employee_id = fb.performance.employee.id
    fb.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect("admin_performance_detail", pk=employee_id)

#------------------------
#project list view
#------------------------

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import EmployeeProfile
from employees.models import Project

# ===============================
# Project List
# ===============================
@login_required
def admin_project_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    projects = Project.objects.select_related('assigned_to').all()

    context = {
        "projects": projects,
    }
    return render(request, "admin_project_list.html", context)


# ===============================
# Project Detail
# ===============================
@login_required
def admin_project_detail(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')

    project = get_object_or_404(Project, pk=pk)

    context = {
        "project": project,
    }
    return render(request, "admin_project_detail.html", context)


# ===============================
# Add / Edit Project
# ===============================
from datetime import datetime
from django.core.exceptions import ValidationError

@login_required
def admin_project_edit(request, pk=None):
    project = None

    if pk:
        project = Project.objects.filter(id=pk).first()

    employees = EmployeeProfile.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to_id = request.POST.get("assigned_to")
        progress = request.POST.get("progress") or 0
        due_date_str = request.POST.get("due_date")
        priority = request.POST.get("priority")
        status = request.POST.get("status")

        assigned_to = EmployeeProfile.objects.get(id=assigned_to_id)
        assigned_by_name = request.user.get_full_name() or request.user.username

        # Parse due_date only if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

        if project:
            # Update existing project
            project.title = title
            project.description = description
            project.assigned_to = assigned_to
            project.progress = progress
            if due_date:
                project.due_date = due_date
            project.priority = priority
            project.status = status

            if not project.assigned_by:
                project.assigned_by = assigned_by_name
        else:
            # Create new project
            if not due_date:
                raise ValidationError("Due date is required.")
            project = Project(
                title=title,
                description=description,
                assigned_to=assigned_to,
                progress=progress,
                due_date=due_date,
                priority=priority,
                status=status,
                assigned_by=assigned_by_name,
            )

        project.save()
        return redirect("admin_project_list")

    return render(request, "admin_project_form.html", {
        "project": project,
        "employees": employees
    })


# ===============================
# Delete Project
# ===============================
@login_required
def admin_project_delete(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')

    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect("admin_project_list")


#----------------------
# LOGOUT
#----------------------
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

@login_required(login_url='/admin/')
def admin_settings(request):
    """
    Admin settings page: profile, password, notifications.
    """
    user = request.user
    profile = getattr(user, 'profile', None)  # If you have extra fields in a profile model

    if request.method == "POST":
        action = request.POST.get("action")

        # ---------------- Profile Update ----------------
        if action == "profile":
            name = request.POST.get("admin_name", "").strip()
            email = request.POST.get("email", "").strip()

            if not name or not email:
                messages.error(request, "Name and email are required.")
            else:
                user.first_name = name  # or full_name if you have
                user.email = email
                user.save()
                messages.success(request, "Profile updated successfully.")

        # ---------------- Password Change ----------------
        elif action == "password":
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not current_password or not new_password or not confirm_password:
                messages.error(request, "All password fields are required.")
            elif not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New password and confirm password do not match.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, "Password updated successfully.")

        # ---------------- Notification Settings ----------------
        elif action == "notifications":
            email_notifications = request.POST.get("email_notifications", "enabled")
            if profile:
                profile.email_notifications = email_notifications
                profile.save()
                messages.success(request, "Notification settings updated.")
            else:
                messages.warning(request, "No profile found to update notifications.")

        return redirect("admin_settings")  # redirect back to same page

    context = {
        "user": user,
        "profile": profile
    }
    return render(request, "settings.html", context)
#======================
# Admin Profile View
#======================
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required(login_url='/admin/')
def admin_profile(request):
    """
    Unified admin profile page with view and edit tabs.
    """
    user = request.user

    if request.method == "POST":
        # Update profile info
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)

        # Optional password change
        new_password = request.POST.get("password")
        if new_password:
            user.set_password(new_password)

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("admin_profile")

    return render(request, "admin_profile.html", {"user": user})
