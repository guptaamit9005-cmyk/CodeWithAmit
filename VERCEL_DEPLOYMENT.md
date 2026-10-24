# 🚀 Vercel Deployment Guide for CodeWithAmit

This project is fully configured and ready for 1-click or CLI deployment on [Vercel](https://vercel.com/).

---

## 📁 Pre-configured Files for Vercel

1. **`vercel.json`**:
   - Uses `@vercel/python` (Python 3.12) to serve Django through `config/wsgi.py`.
   - Uses `@vercel/static-build` with `build_files.sh` to install dependencies and collect static files into `staticfiles/`.
   - Routes `/static/(.*)` directly to `/staticfiles/$1` for ultra-fast CDN delivery.
   - Routes all other traffic to `config/wsgi.py` (exposed as `app`).

2. **`build_files.sh`**:
   - Detects `python3` / `python` or `uv`.
   - Installs dependencies from `requirements.txt`.
   - Runs `python manage.py collectstatic --no-input --clear`.
   - Automatically runs `python manage.py migrate --no-input` if `DATABASE_URL` is configured.

3. **`config/wsgi.py`**:
   - Exports `application` and aliases `app = application` for Vercel WSGI entry point.

4. **`config/settings.py`**:
   - Automatically configures `ALLOWED_HOSTS = ['*']` or from environment variable.
   - Automatically allows `CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app', ...]`.
   - Uses **WhiteNoise** (`CompressedStaticFilesStorage`) for reliable static asset delivery.
   - Automatically copies the pre-seeded `db.sqlite3` with all courses, questions, notes, and demo accounts into `/tmp/db.sqlite3` if running on Vercel without an external database.
   - Seamlessly supports production PostgreSQL via `DATABASE_URL` (Supabase, Neon, Railway).

---

## 🛠️ How to Deploy on Vercel

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to a GitHub repository**:
   ```bash
   cd "CodeWithAmit-main"
   git init
   git add .
   git commit -m "Ready for Vercel deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Import Project into Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new).
   - Select your GitHub repository.
   - If your repository has a root folder containing the code, ensure the **Root Directory** setting is set to the folder containing `manage.py` and `vercel.json` (or leave as `./` if initialized at root).

3. **Configure Environment Variables** (in Vercel Project Settings > Environment Variables):
   | Variable | Value | Notes |
   | :--- | :--- | :--- |
   | `DEBUG` | `False` | Set to `False` for production security |
   | `SECRET_KEY` | *(your generated secret key)* | e.g. generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
   | `ALLOWED_HOSTS` | `*` or `.vercel.app` | Comma-separated allowed hostnames |
   | `CSRF_TRUSTED_ORIGINS` | `https://*.vercel.app` | Comma-separated trusted origins |
   | `DATABASE_URL` | *(optional)* | e.g., Neon or Supabase PostgreSQL connection string |

4. **Click "Deploy"**:
   - Vercel will run `build_files.sh`, collect all static assets, and launch your serverless Django app.

---

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy directly from the project directory**:
   ```bash
   cd "c:\Users\Amit kumar gupta\Downloads\CodeWithAmit-main\CodeWithAmit-main"
   vercel
   ```

3. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

---

## 🔑 Pre-seeded Demo Logins

When deployed (or running locally), the following accounts are pre-seeded and ready:

| Role | Username | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full Django Admin (`/admin/`), Admin Analytics (`/dashboard/admin-analytics/`) |
| **Instructor** | `instructor` | `instructor123` | Class Scheduling, Course Management, Instructor Portal (`/dashboard/instructor/`) |
| **Student** | `student` | `student123` | Course Enrollment, DSA Practice, Note Downloads, Roadmaps (`/dashboard/`) |

---

## 🌐 Local Development URL

- Website URL: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**
- Server status: **Running**
