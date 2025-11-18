from django import forms
from employees.models import Payroll

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = "__all__"
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
        }
