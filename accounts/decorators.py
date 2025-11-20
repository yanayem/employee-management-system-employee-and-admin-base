from django.shortcuts import redirect

def employee_required(view_func):
    """
    Protect pages by checking if employee is logged in via session.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get("employee_id"):
            return redirect("accounts:employee_login_page")
        return view_func(request, *args, **kwargs)
    return wrapper
