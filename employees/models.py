from django.db import models
from django.utils import timezone
from accounts.models import EmployeeProfile
from datetime import datetime

# ===============================
# Attendance Model
# ===============================
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')

    def working_hours(self):
        """Return working hours as 'Xh Ym' or '-' if not checked in/out."""
        if self.check_in and self.check_out:
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            diff = check_out_dt - check_in_dt
            hours = int(diff.total_seconds() // 3600)
            minutes = int((diff.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "-"

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"


# ===============================
# LeaveRequest Model
# ===============================
class LeaveRequest(models.Model):
    LEAVE_CHOICES = [
        ("Annual", "Annual"),
        ("Sick", "Sick"),
        ("Personal", "Personal"),
        ("Maternity", "Maternity"),
        ("Emergency", "Emergency"),
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_CHOICES)
    number_of_days = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(default=timezone.now)

    def total_days(self):
        return self.number_of_days


# ===============================
# Payroll Model
# ===============================
class Payroll(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    month = models.DateField()
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    payslip_file = models.FileField(upload_to="payslips/", null=True, blank=True)

    class Meta:
        ordering = ['-month']

    def __str__(self):
        return f"{self.employee.employee_id} - {self.month.strftime('%B %Y')}"


# ===============================
# Performance Model
# ===============================

from django.db import models
from accounts.models import EmployeeProfile

# Skill model (for dynamic skill types)
class Skill(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default="blue")  # Tailwind color for progress bar

    def __str__(self):
        return self.name

# Performance model
class Performance(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name="performance")
    goals_achieved = models.IntegerField(default=0)
    total_goals = models.IntegerField(default=0)
    projects_completed = models.IntegerField(default=0)
    achievements = models.IntegerField(default=0)
    manager_comment = models.TextField(blank=True, null=True)

    def overall_rating(self):
        """
        Calculate overall rating scaled to 5.
        """
        skills = self.skills.all()
        if not skills:
            return 0
        # 0-100 scale skills average
        avg_percent = sum([s.value for s in skills]) / len(skills)
        # scale to 5
        rating = round((avg_percent / 100) * 5, 1)
        return rating
    def __str__(self):
        return f"{self.employee.employee_id} Performance"

# Linking skills to a performance record
class PerformanceSkill(models.Model):
    performance = models.ForeignKey(Performance, related_name="skills", on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)  # 0-100

    def __str__(self):
        return f"{self.performance.employee.employee_id} - {self.skill.name}: {self.value}%"

# Feedback model
class Feedback(models.Model):
    performance = models.ForeignKey(Performance, related_name="feedbacks", on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    text = models.TextField()
    color = models.CharField(max_length=20, default="blue")  # Tailwind color for avatar
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.performance.employee.employee_id} - {self.author}"



# ===============================
# Project Model
# ===============================

from django.db import models
from accounts.models import EmployeeProfile

PRIORITY_CHOICES = [
    ("Low", "Low"),
    ("Medium", "Medium"),
    ("High", "High"),
]

STATUS_CHOICES = [
    ("Planning", "Planning"),
    ("In Progress", "In Progress"),
    ("Review", "Review"),
    ("Completed", "Completed"),
]

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_to = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    assigned_by = models.CharField(max_length=100)
    progress = models.PositiveIntegerField(default=0)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Planning")

    def assigned_by_initials(self):
        return "".join([n[0] for n in self.assigned_by.split()][:2])

    @classmethod
    def aggregate_success_rate(cls):
        projects = cls.objects.all()
        if not projects.exists():
            return 0
        return round(sum([p.progress for p in projects])/projects.count())
