from django.contrib import admin
from .models import (
    Attendance,
    LeaveRequest,
    Payroll,
    Performance,
    PerformanceSkill,
    Feedback,
    Skill
)

# =========================
# Attendance Admin
# =========================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "status", "check_in", "check_out", "working_hours")
    search_fields = ("employee__employee_id", "employee__phone")
    list_filter = ("status", "date")
    ordering = ("-date",)

# =========================
# LeaveRequest Admin
# =========================
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "status", "total_days")
    search_fields = ("employee__employee_id", "employee__phone", "leave_type")
    list_filter = ("status", "leave_type")
    ordering = ("-start_date",)

# =========================
# Payroll Admin
# =========================
@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "gross_salary", "deductions", "net_pay")
    search_fields = ("employee__employee_id", "employee__phone")
    list_filter = ("month",)
    ordering = ("-month",)

# =========================
# Performance Admin
# =========================

# Inline for Skills
class PerformanceSkillInline(admin.TabularInline):
    model = PerformanceSkill
    extra = 0

# Inline for Feedbacks
class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "goals_achieved", "total_goals", "projects_completed", "achievements", "overall_rating")
    search_fields = ("employee__employee_id", "employee__phone")
    list_filter = ("employee__department",)
    inlines = [PerformanceSkillInline, FeedbackInline]

# =========================
# Skill Admin
# =========================
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    search_fields = ("name",)

# =========================
# Feedback Admin (optional standalone)
# =========================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("performance", "author", "created_at")
    search_fields = ("performance__employee__employee_id", "author")
    list_filter = ("created_at",)

# ===============================
# Project Model Admin
# ===============================
from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "due_date", "status", "priority", "progress")
    search_fields = ("title", "assigned_to__employee_id", "assigned_to__phone", "assigned_by")
    list_filter = ("status", "priority", "due_date")
