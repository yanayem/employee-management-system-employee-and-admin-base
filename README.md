# Employee Management System

[Live Demo](https://employee-management-system-employee-and.onrender.com/) | [GitHub Repository](https://github.com/yanayem/employee-management-system-employee-and-admin-base/tree/main)

A **Django-based Employee Management System** to manage employees, attendance, payroll, projects, and performance.

---

## Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/yanayem/employee-management-system-employee-and-admin-base.git
cd employee-management-system-employee-and-admin-base
```


3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

---

## Running the Project

```bash
python manage.py runserver
```
- Open in browser: `http://127.0.0.1:8000/`

---

## Usage

- Admin panel: `/admin/`
- Employee portal: `/employee/login/`
- Admins: manage employees, attendance, payroll, projects
- Employees: update profile, track tasks & performance

---

## Dependencies

- Django 4.2, Django REST Framework  
- Channels, Daphne   
- Cloudinary (`django-cloudinary-storage`)  
- Gunicorn, Waitress  
- NumPy, SciPy, scikit-learn  
- Whitenoise, ReportLab  

---

## License

MIT License
