# 🏢 Employee Management System (EMS)

A powerful, feature-rich Employee Management System built with **Django 4.2**. This platform streamlines HR operations, automates attendance tracking, manages payroll, and provides a collaborative environment for project oversight and performance evaluation.

---

## 🌟 Key Features

### 👤 Employee Self-Service
*   **Smart Dashboard:** Real-time summary of active projects, attendance percentages, and recent activities.
*   **Attendance System:** 
    *   One-click Check-In/Check-Out.
    *   **Auto-Status:** Marks "Present" if checked in before 09:30 AM, otherwise marked as "Late".
    *   Weekly & Monthly hours calculation.
*   **Leave Management:**
    *   Dedicated balances: **Annual (18), Sick (8), Personal (5), Emergency (5)**.
    *   **Maternity Leave:** Specifically available for female employees (90 days).
    *   Status tracking (Pending/Approved/Rejected).
*   **Project Tracking:** Update progress (%), view deadlines, and receive manager feedback.
*   **Performance Metrics:** Visual skill charts, achievement counters, and manager testimonials.
*   **Document Vault:** Secure access to personal payslips, certificates, and company policies.
*   **Profile Control:** Manage personal details, emergency contacts, and profile pictures (Avatars).

### 🛡️ Administrative Power
*   **Full Employee Lifecycle:** From onboarding (automatic ID generation) to access management.
*   **Departmental Analytics:** Monitor total headcount and payroll expenditure per department.
*   **Advanced Payroll:** Generate monthly records, manage gross salary/deductions, and upload payslip PDFs.
*   **Project Management:** Assign tasks, set priorities (Low/Medium/High), and track overall team success rates.
*   **Mass Notifications:** Broadcast announcements to the entire team via a real-time notification system.
*   **Admin UI:** Enhanced with **Django Jazzmin** for a modern, responsive management experience.

---

## 📈 Business Requirements & Objectives

This system was designed to address core HR and operational challenges within a mid-sized organization:

1.  **Automated Time & Attendance:** Eliminate manual logbooks by providing a digital check-in/out system that automatically flags tardiness and calculates weekly/monthly effort hours.
2.  **Centralized Employee Data:** A single source of truth for employee records, including personal details, emergency contacts, and professional history, replacing fragmented spreadsheets.
3.  **Standardized Leave Policy:** Enforce company-wide leave quotas (Annual, Sick, Personal) and specialized policies (Maternity) with an automated approval workflow to ensure staffing stability.
4.  **Performance Transparency:** Implement a data-driven performance review system where skill growth and goal completion are visible to both managers and employees, fostering professional development.
5.  **Secure Payroll Distribution:** Automate the generation and secure distribution of monthly payslips, reducing administrative overhead and ensuring privacy.
6.  **Project Alignment:** Connect individual tasks to broader company goals by allowing managers to assign projects, set priorities, and monitor real-time progress through employee updates.
7.  **Data-Driven Decision Making:** Provide administrators with analytics on department headcounts and payroll expenditures to assist in budgetary planning.

---

## 🎨 UI Design & Color Palette

The system features a clean, professional "Enterprise Pulse" design language, optimized for both light and dark environments.

### 🍱 UI Components
*   **Responsive Sidebar:** Collapsible navigation with active state highlighting and hover transitions.
*   **Dynamic Dashboards:** Card-based layouts with `card-hover` effects and data visualizations.
*   **Glassmorphism Modals:** Interactive dialogs with `backdrop-filter: blur(8px)` for focused user actions.
*   **Visual Feedback:**
    *   **Progress Bars:** Smooth gradient transitions for project tracking and skill metrics.
    *   **Pulse Indicators:** Real-time status dots for active notifications or attendance tracking.
    *   **Animated Transitions:** `Fade-in` and `Slide-in` animations for a fluid page-load experience.

### 🌈 Color Palette
| Category | Light Mode | Dark Mode | Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | `#3b82f6` → `#1d4ed8` | `#3b82f6` → `#1d4ed8` | Buttons, Active States, Gradients |
| **Background** | `#ffffff` / `#f8fafc` | `#1e293b` / `#334155` | Primary & Secondary surfaces |
| **Text (Primary)** | `#1e293b` | `#f1f5f9` | Headings and Main content |
| **Text (Secondary)**| `#64748b` | `#cbd5e1` | Subtitles and Metadata |
| **Success** | `#d1fae5` (BG) | `#065f46` (Text) | Present, Approved, Completed |
| **Warning** | `#fef3c7` (BG) | `#92400e` (Text) | Late, Pending, In Progress |
| **Danger** | `#fee2e2` (BG) | `#991b1b` (Text) | Absent, Rejected, Overdue |

---

## 🛠️ Technical Stack

*   **Framework:** Django 4.2.16
*   **Frontend:** HTML5, CSS3, JavaScript, Tailwind CSS (via templates)
*   **Database:** SQLite (Development) / PostgreSQL (Production ready)
*   **UI Components:** Django Jazzmin, FontAwesome Icons
*   **File Storage:** Cloudinary (for Avatars & Documents)
*   **Static Assets:** WhiteNoise
*   **Tools:** ReportLab (PDF Generation), HTMX (Interactive UI)

---

## 🚀 Installation & Setup

### 1. Prerequisites
*   Python 3.10+
*   pip & virtualenv

### 2. Clone & Install
```bash
git clone https://github.com/your-username/ems-project.git
cd ems-project

# Setup Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file or update `settings.py` with:
```python
# Email Settings (for notifications)
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Cloudinary (for media hosting)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'your_name',
    'API_KEY': 'your_key',
    'API_SECRET': 'your_secret'
}
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser  # Create Admin access
```

### 5. Run Server
```bash
python manage.py runserver
```
Visit: `http://127.0.0.1:8000/`

---

## 📂 Project Architecture

*   `accounts/`: Custom authentication, `EmployeeProfile` model, and ID generation logic.
*   `employees/`: Core logic for `Attendance`, `LeaveRequest`, `Payroll`, `Performance`, and `Project`.
*   `adminpanel/`: Custom dashboard views for administrators and `Department` management.
*   `templates/`: Modular HTML structures with Tailwind integration.
*   `static/`: Global CSS themes and assets.

---

## 🔐 Security & Access
*   **Employee Login:** Employee ID + Password (Default: last 6 digits of phone).
*   **First Login:** Enforces a mandatory password change for new users.
*   **Session-based:** Custom session handling for non-standard Django User models.

---

## ⚙️ Support
For technical issues, please contact the IT Support team or raise a GitHub issue.
- **Email:** it-support@example.com
- **Docs:** [Internal Wiki Link]
