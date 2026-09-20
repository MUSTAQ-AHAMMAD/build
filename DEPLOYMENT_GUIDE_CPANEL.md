# BUILD+ Enterprise — Complete cPanel Zero-to-Production Deployment Guide

This guide provides the complete, authoritative, zero-to-production deployment procedure for the **BUILD+ Corporate Operations Hub** on cPanel shared or dedicated hosting environments using **Setup Python App (Phusion Passenger)** and **MySQL® Database Wizard**.

---

## 1. System Requirements & Hosting Prerequisites

- **cPanel Version:** 108+ with CloudLinux or standard cPanel Python Selector.
- **Python Version:** Python `3.10`, `3.11`, or `3.12`.
- **Database Engine:** MySQL 8.0+ or MariaDB 10.5+ with InnoDB support.
- **SSL Certificate:** Active AutoSSL / Let's Encrypt certificate on the target domain.
- **Access Tools:** cPanel File Manager, cPanel Terminal (or SSH), phpMyAdmin.

---

## 2. Step-by-Step 25-Point Production Deployment Procedure

### PHASE 1: MySQL Database Provisioning
1. Log into your **cPanel** dashboard.
2. Navigate to **Databases > MySQL® Database Wizard**.
3. **Step 1:** Enter your database name (e.g. `cpuser_buildplus`). Click **Next Step**.
4. **Step 2:** Enter your database username (e.g. `cpuser_dbadmin`). Generate a secure 24+ character password. Save this password securely. Click **Create User**.
5. **Step 3:** Check the **ALL PRIVILEGES** checkbox. Click **Make Changes**.
6. Note down the full Database Name, Username, and Password.

### PHASE 2: Schema Import (Optional Alternative to Migrations)
7. In cPanel, open **phpMyAdmin**.
8. Select `cpuser_buildplus` from the left sidebar.
9. Click the **Import** tab.
10. Click **Choose File** and select `deployment/mysql/schema_export.sql`. Click **Import**.

### PHASE 3: Project Upload & Python Application Setup
11. Compress your local project folder into a `.zip` file (*excluding `venv/`, `.git/`, and `__pycache__`*).
12. In cPanel **File Manager**, upload and extract the archive into `/home/cpuser/construction_portal/`.
13. In cPanel, navigate to **Software > Setup Python App**.
14. Click **Create Application** and configure:
    - **Python Version:** Select `3.11` (or `3.10` / `3.12`).
    - **Application Root:** `construction_portal`
    - **Application URL:** Select your domain (e.g. `yourdomain.com`).
    - **Application Startup File:** `passenger_wsgi.py`
    - **Application Entry Point:** `application`
15. Click **Create**.

### PHASE 4: Virtual Environment & Dependency Installation
16. In cPanel **Setup Python App**, copy the virtual environment activation command at the top of the page.
17. Open **cPanel > Terminal** and run the copied command:
    ```bash
    source /home/cpuser/virtualenv/construction_portal/3.11/bin/activate && cd /home/cpuser/construction_portal
    ```
18. Upgrade pip and install all required production dependencies:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

### PHASE 5: Environment Variables & Database Migration
19. Create the `.env` file in `/home/cpuser/construction_portal/.env`:
    ```ini
    DJANGO_SECRET_KEY=generate-a-secure-50-character-secret-key-here
    DJANGO_DEBUG=False
    DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

    DB_ENGINE=mysql
    DB_NAME=cpuser_buildplus
    DB_USER=cpuser_dbadmin
    DB_PASSWORD=your_actual_db_password
    DB_HOST=localhost
    DB_PORT=3306

    GEMINI_API_KEY=your_google_gemini_api_key_here

    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER=notifications@yourdomain.com
    EMAIL_HOST_PASSWORD=your_smtp_app_password
    DEFAULT_FROM_EMAIL=BUILD+ Notifications <notifications@yourdomain.com>
    ```
20. In the cPanel Terminal, run migrations to ensure all database tables are synchronized:
    ```bash
    python manage.py migrate
    ```

### PHASE 6: Static Assets, Media & Superuser
21. Collect all static files into the deployment directory:
    ```bash
    python manage.py collectstatic --noinput
    ```
22. Create the production administrator account:
    ```bash
    python manage.py createsuperuser
    ```
23. Configure media directory permissions:
    ```bash
    mkdir -p media
    chmod 755 media
    ```

### PHASE 7: Apache Routing & Application Restart
24. Copy `deployment/cpanel/.htaccess` to `/home/cpuser/public_html/.htaccess` and update `CPANEL_USER` with your actual cPanel username.
25. In cPanel **Setup Python App**, click **Restart** on your application.

---

## 3. Post-Deployment Verification Checklist

- [ ] Open `https://yourdomain.com/` &mdash; Public homepage loads in `< 1.2s` with CSS and JS assets.
- [ ] Open `https://yourdomain.com/admin/` &mdash; Master Admin Console loads with live executive KPI metrics.
- [ ] Open `https://yourdomain.com/crm/` &mdash; CRM Sales Pipeline renders leads and site visits.
- [ ] Open `https://yourdomain.com/cms/` &mdash; CMS Content Desk allows editing services and projects.
- [ ] Open `https://yourdomain.com/aichatboat/` &mdash; AI Assistant streams conversations via Google Gemini.
- [ ] Open `https://yourdomain.com/payment/` &mdash; Payment transactions, UPI QR, and tax receipts functional.
- [ ] Open `https://yourdomain.com/portal/` &mdash; Client portal allows project tracking and proposal sign-off.
