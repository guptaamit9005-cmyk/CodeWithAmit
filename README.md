# Student Success Hub — All-in-One Learning Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An integrated, professional educational web application designed for computer science and engineering students to master programming languages, explore university notes, attend live classes via Google Meet, solve coding interview challenges, and follow career roadmaps.

---

## 🌟 Key Platform Features

### 1. 🎓 Tutorials & Course Management System
- **Curated Modules**: Structured courses across C/C++, Python, Full-Stack Web Development, Data Structures & Algorithms, and Machine Learning.
- **Rich Lesson Experience**: High-definition video players (YouTube embed support), Markdown lesson descriptions, copyable starter code snippets, and previous/next navigation.
- **Interactive Quizzes**: Multiple-choice quizzes at the end of lessons with instant grading, score percentages, and detailed answer explanations.
- **Enrollment & Reviews**: Track course progress percentages, bookmark favorite courses, and submit student star ratings & reviews.

### 2. 📚 Academic Notes & PDF Document Library
- **Semester & Category Filtering**: Filter notes by semester (Semester 1–8), subject, or programming language.
- **In-Browser Document Preview**: Embedded PDF viewer directly in the browser.
- **Download Tracking**: Download counters increment dynamically.
- **Community Contributions**: Authenticated students and instructors can upload new notes, cheat sheets, and study materials.

### 3. 🎥 Live Classes & Google Meet Integration
- **Live Video Mentorship**: Class schedules with instructor details, agenda, and direct Google Meet room launch buttons.
- **RSVP & Attendance**: Students register for upcoming classes and receive in-app notifications.
- **Class Archives**: Post-class recording links, downloadable slides, and shared code repositories.

### 4. 💻 DSA Coding Practice Arena
- **Interactive Split-Screen**: Problem description, examples, constraints, and hints accordion on the left; multi-language code editor on the right.
- **Multi-Language Selector**: Toggle between Python 3, C++, and Java with auto-updating starter templates.
- **Real-Time Test Runner**: "Run Code" executes against sample test cases and returns runtime latency (ms), memory (MB), and output comparison.
- **Submission & Gamification**: "Submit Code" evaluates the test suite, marks problems as solved, awards XP points, and advances daily learning streaks.
- **Official Editorials**: Detailed intuition breakdown, time/space complexity ($O(N)$ analysis), and complete reference implementations.

### 5. 🗺️ Interactive Career Roadmaps
- **Step-by-Step Milestones**: Chronological learning stages (Beginner, Intermediate, Advanced) for roles like Full-Stack Developer and Systems Architect.
- **AJAX Checkpoints**: Check off topics as you learn with dynamic, real-time progress bar recalculations without full-page reloads.
- **Cross-Platform Deep Links**: Roadmap topics link directly to platform courses, subject notes, and practice challenges.

### 6. 📊 Multi-Role Portals & Dashboards
- **Student Dashboard**: Enrolled course progress bars, upcoming Google Meet countdowns, DSA practice statistics, active roadmap tracking, and bookmarked notes.
- **Instructor Workspace**: Manage scheduled classes, review enrolled student metrics, and upload teaching resources.
- **Admin Analytics**: Platform-wide metrics (users, courses, submissions, notes) and direct links to the Django Admin panel.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Django 6.1
- **Database**: SQLite (Development) / PostgreSQL (Production via `dj-database-url` and `psycopg2-binary`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons
- **Design System**: Handcrafted Dark Navy theme (`#0b132b`, `#1c2541`, `#00b4d8`) with subtle gradients, glassmorphism, responsive navigation, and light/dark theme toggle
- **Static Assets & Media**: WhiteNoise with compressed manifest storage and Django Media Storage
- **Deployment Ready**: Gunicorn WSGI and Render Blueprint (`render.yaml`, `build.sh`)

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+ installed

### 2. Clone or Open Project
```powershell
cd "c:\Users\Amit kumar gupta\Desktop\Codestyle"
```

### 3. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Apply Database Migrations
```powershell
python manage.py migrate
```

### 6. Seed Demo Data & Demo Accounts
```powershell
python manage.py seed_data
```

### 7. Run the Local Development Server
```powershell
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your web browser.

---

## 🔑 Demo Login Accounts

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full Django Admin (`/admin/`), Admin Analytics Dashboard |
| **Instructor** | `instructor` | `instructor123` | Class Scheduling, Course Management, Instructor Portal |
| **Student** | `student` | `student123` | Course Enrollment, DSA Code Runner, Note Downloads, Roadmap Checkpoints |

---

## 🧪 Automated Testing

Run the full automated test suite covering authentication, courses, quizzes, code execution simulation, live classes, and AJAX roadmaps:

```powershell
python manage.py test core
```

---

## ☁️ Production Deployment on Render

This project includes pre-configured deployment artifacts:
- [`render.yaml`](file:///c:/Users/Amit%20kumar%20gupta/Desktop/Codestyle/render.yaml): Declares a free PostgreSQL database and Python web service.
- [`build.sh`](file:///c:/Users/Amit%20kumar%20gupta/Desktop/Codestyle/build.sh): Automatically installs dependencies, collects static files, runs migrations, and seeds initial content.

### Steps to Deploy:
1. Push repository to GitHub or GitLab.
2. In Render, select **New > Blueprint** and connect your repository.
3. Render will read `render.yaml`, provision the PostgreSQL database, and build the application automatically.
4. Set `ALLOWED_HOSTS` to your custom or `.onrender.com` domain.

---

## 📁 Project Architecture

```text
Codestyle/
├── accounts/               # User authentication, profiles, streaks & gamification
├── coding_practice/        # Problem repository, split-screen code editor & test runner
├── config/                 # Django settings, WSGI/ASGI, and root URL routing
├── core/                   # Home page, multi-resource global search, legal & seed command
├── courses/                # Video lessons, curriculum syllabus, quizzes & reviews
├── dashboard/              # Student, Instructor, and Superuser analytics portals
├── live_classes/           # Live Google Meet schedules, RSVP, and class recordings
├── notes/                  # PDF library, upload handler, and download tracking
├── notifications/          # In-app alerts, bell dropdown & read state management
├── roadmaps/               # Step-by-step career tracks & interactive AJAX progress
├── static/
│   ├── css/styles.css      # Dark navy glassmorphism custom design system
│   └── js/main.js          # Theme toggle, AJAX topics, copy button & editor shortcuts
├── templates/              # Responsive Bootstrap 5 Django templates
├── build.sh                # Render deployment build script
├── render.yaml             # Render infrastructure blueprint
└── requirements.txt        # Production dependency manifest
```
