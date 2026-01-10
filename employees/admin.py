from django.contrib import admin
from .models import (
    Attendance, LeaveRequest, Payroll, Skill, 
    Performance, PerformanceSkill, Feedback, 
    Project, Document, EmployeeData
)

# --- Inlines for a more cohesive UI ---

class PerformanceSkillInline(admin.TabularInline):
    model = PerformanceSkill
    extra = 1

class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    fields = ('author', 'text', 'color')

# --- Admin Registrations ---

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status', 'working_hours')
    list_filter = ('status', 'date', 'employee__department')
    search_fields = ('employee__full_name', 'employee__employee_id')
    date_hierarchy = 'date'

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'number_of_days', 'status')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__full_name', 'reason')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'gross_salary', 'deductions', 'net_pay')
    list_filter = ('month',)
    search_fields = ('employee__full_name', 'employee__employee_id')

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'goals_achieved', 'total_goals', 'overall_rating')
    inlines = [PerformanceSkillInline, FeedbackInline]
    search_fields = ('employee__full_name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'due_date', 'priority', 'status', 'progress')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'assigned_to__full_name')
    # Simple progress bar logic could be added here for the Zinc look
    
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'employee', 'category', 'view_only', 'uploaded_at')
    list_filter = ('category', 'view_only')
    search_fields = ('title', 'employee__full_name')

@admin.register(EmployeeData)
class EmployeeDataAdmin(admin.ModelAdmin):
    list_display = ('employee', 'designation', 'department', 'joining_date')
    search_fields = ('employee__full_name', 'employee__employee_id')