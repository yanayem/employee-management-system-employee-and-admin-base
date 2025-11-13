from django.db import models
from datetime import datetime

def generate_employee_id():
    current_year = datetime.now().year
    last_employee = EmployeeProfile.objects.filter(employee_id__startswith=f"EM{current_year}").order_by('id').last()
    if not last_employee:
        return f"EM{current_year}001"
    last_number = int(last_employee.employee_id[-3:])
    new_number = last_number + 1
    return f"EM{current_year}{new_number:03d}"

class EmployeeProfile(models.Model):
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    password = models.CharField(max_length=128)  # store raw for now
    first_login = models.BooleanField(default=True)
    temp_password = models.CharField(max_length=20, blank=True)  # one-time password

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = generate_employee_id()
        if not self.temp_password and self.phone:
            self.temp_password = self.phone[-6:]
            self.password = self.temp_password
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return self.password == raw_password

    def set_password(self, raw_password):
        self.password = raw_password
        self.first_login = False
        self.save()

    def __str__(self):
        return f"{self.employee_id} ({self.phone})"
