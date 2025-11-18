from django.contrib import admin
from .models import (
    Attendance,
    LeaveRequest,
    Payroll,
    Performance,
    PerformanceSkill,
    Feedback,
    Skill;
)
from acco.models import (EmployeeData)

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


# ===============================
# Document Model Admin
# ===============================

# employees/admin.py
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "employee", "category", "view_only", "uploaded_at")
    list_filter = ("category", "view_only", "uploaded_at")
    search_fields = ("title", "employee__employee_id", "employee__name")


# ===============================
# Profile Model Admin
# ===============================

@admin.register(EmployeeData)
class EmployeeDataAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "designation",
        "department",
        "joining_date",
        "tenure_years",
    )

    list_filter = ("department", "designation")
    search_fields = (
        "employee__full_name",
        "employee__employee_id",
        "designation",
    )

    readonly_fields = ("avatar_preview",)

    fieldsets = (
        ("Employee Info", {
            "fields": (
                "employee",
                "designation",
                "department",
                "role",
            )
        }),

        ("Additional Details", {
            "fields": (
                "joining_date",
                "address",
                "emergency_contact",
            )
        }),

        ("Avatar", {
            "fields": (
                "avatar",
                "avatar_preview",
            )
        }),
    )

    # ===== Avatar Preview =====
    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="80" style="border-radius:8px;" />'
        return "No image"

    avatar_preview.allow_tags = True
    avatar_preview.short_description = "Avatar Preview"
