# employees/forms.py
from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "number_of_days", "start_date", "end_date", "reason"]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "w-full p-2 rounded border"}),
            "number_of_days": forms.NumberInput(attrs={"class": "w-full p-2 rounded border"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "w-full p-2 rounded border"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "w-full p-2 rounded border"}),
            "reason": forms.Textarea(attrs={"rows": 3, "class": "w-full p-2 rounded border"}),
        }
