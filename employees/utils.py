from django.utils import timezone

def get_project_status(project):
    today = timezone.localdate()

    # Completed
    if project.progress >= 100:
        return {
            "label": "Completed",
            "badge": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
        }

    # Overdue (Past due date but not completed)
    if project.due_date < today:
        return {
            "label": "Overdue",
            "badge": "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
        }

    # Upcoming (Future start date)
    if hasattr(project, "start_date") and project.start_date and project.start_date > today:
        return {
            "label": "Upcoming",
            "badge": "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
        }

    # Active / In Progress
    return {
        "label": "In Progress",
        "badge": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
    }
