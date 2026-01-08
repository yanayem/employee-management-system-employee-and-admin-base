from .models import EmployeeProfile

def global_employee(request):
    employee_id = request.session.get("employee_id")

    if employee_id:
        try:
            profile = EmployeeProfile.objects.get(employee_id=employee_id)
        except EmployeeProfile.DoesNotExist:
            profile = None
        return {
            "global_profile": profile
        }

    return {
        "global_profile": None
    }
