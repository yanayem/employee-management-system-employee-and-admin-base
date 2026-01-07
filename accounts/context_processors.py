from .models import EmployeeProfile

def global_employee(request):
    if request.user.is_authenticated:
        try:
            profile = EmployeeProfile.objects.get(id=request.user.id)
        except EmployeeProfile.DoesNotExist:
            profile = None
        return {
            "global_profile": profile
        }
    return {}
