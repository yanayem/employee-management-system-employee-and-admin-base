from django import forms
from employees.models import Payroll
from .models import Department

# ----------------------------
# Payroll Form
# ----------------------------
class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = "__all__"
        widgets = {
            "month": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full p-2 border rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                }
            ),
            "employee": forms.Select(
                attrs={
                    "class": "w-full p-2 border rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                }
            ),
            "gross_salary": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                }
            ),
            "bonus": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                }
            ),
        }


# ----------------------------
# Department Form
# ----------------------------
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'w-full p-2 border rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 transition',
                    'placeholder': 'Enter Department Name'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'w-full p-2 border rounded dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 transition',
                    'rows': 3,
                    'placeholder': 'Enter Department Description'
                }
            ),
        }
