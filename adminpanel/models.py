from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # --------------------
    # Reverse Relations
    # --------------------
    def employee_count(self):
        # Import here to avoid circular import
        from accounts.models import EmployeeProfile
        return EmployeeProfile.objects.filter(department=self).count()

    def project_count(self):
        from employees.models import Project
        # Assuming Project has assigned_to ForeignKey to EmployeeProfile
        return Project.objects.filter(assigned_to__department=self).count()

    def total_payroll(self):
        from employees.models import Payroll  # or payroll.models if separate app
        return Payroll.objects.filter(employee__department=self).aggregate(
            total=models.Sum('gross_salary')
        )['total'] or 0
