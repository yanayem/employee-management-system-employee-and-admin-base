from django.contrib import admin
from .models import EmployeeProfile

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'phone', 'department', 'first_login')
    readonly_fields = ('employee_id', 'temp_password')
    search_fields = ('employee_id', 'phone')
