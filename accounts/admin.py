from django.contrib import admin
from .models import EmployeeProfile

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'is_active', 'security_status')
    list_filter = ('is_active', 'first_login', 'department')
    search_fields = ('employee_id', 'full_name', 'phone')
    readonly_fields = ('employee_id', 'temp_password')

    fieldsets = (
        ('Authentication & Status', {
            'fields': (
                'is_active', 
                'first_login', 
                'employee_id', 
                'password', 
                'temp_password'
            ),
            'description': "Enable 'First Login' to force the user to reset their password."
        }),
        ('Employee Information', {
            'fields': (('full_name', 'gender'), 'phone', 'email', 'avatar')
        }),
        ('Work Details', {
            'fields': (('department', 'designation', 'role'), 'joining_date')
        }),
        ('Emergency Info', {
            'classes': ('collapse',),
            'fields': ('emergency_name', 'emergency_relation', 'emergency_contact', 'emergency_address')
        }),
    )

    def security_status(self, obj):
        if obj.first_login:
            return "Force Password Change"
        return "Active"
    security_status.short_description = 'Login Requirement'