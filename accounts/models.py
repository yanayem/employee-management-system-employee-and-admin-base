from django.db import models
from datetime import datetime
from adminpanel.models import Department

# ===============================
# Employee ID Generator
# ===============================
def generate_employee_id():
    current_year = datetime.now().year
    last_employee = EmployeeProfile.objects.filter(
        employee_id__startswith=f"EM{current_year}"
    ).order_by('id').last()

    if not last_employee:
        return f"EM{current_year}001"

    last_number = int(last_employee.employee_id[-3:])
    new_number = last_number + 1
    return f"EM{current_year}{new_number:03d}"


# ===============================
# Choices
# ===============================
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]


# ===============================
# Employee Model
# ===============================
class EmployeeProfile(models.Model):
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15)
    department = models.ForeignKey(
        'adminpanel.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees"
    )
    designation = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    password = models.CharField(max_length=128)
    temp_password = models.CharField(max_length=20, blank=True)
    first_login = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_relation = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    emergency_address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # ===============================
    # Save Override
    # ===============================
    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = generate_employee_id()
        if not self.temp_password and self.phone:
            self.temp_password = self.phone[-6:]
            self.password = self.temp_password
            self.first_login = True
        super().save(*args, **kwargs)

    # ===============================
    # Authentication Helpers
    # ===============================
    def check_password(self, raw_password):
        return self.password == raw_password

    def set_password(self, raw_password):
        self.password = raw_password
        if self.pk:
            self.save(update_fields=["password"])
        else:
            self.save()

    # ===============================
    # Admin Utilities
    # ===============================
    def reset_first_login(self):
        self.first_login = True
        if self.pk:
            self.save(update_fields=["first_login"])
        else:
            self.save()

    def reset_login_with_temp_password(self):
        self.temp_password = self.phone[-6:] if self.phone else ""
        self.password = self.temp_password
        self.first_login = True
        if self.pk:
            self.save(update_fields=["temp_password", "password", "first_login"])
        else:
            self.save()

    # ===============================
    # Display Helpers
    # ===============================
    @property
    def initials(self):
        names = (self.full_name or "").split()
        return "".join([n[0].upper() for n in names[:2]])

    def __str__(self):
        return f"{self.employee_id} ({self.full_name})"
