# BUILD+ Enterprise — cPanel Production Deployment Master Guide

This guide walks you through the step-by-step production deployment of BUILD+ on cPanel hosting with **Setup Python App (Passenger WSGI)** and **MySQL Database Wizard**.

---

## 📋 Pre-Deployment Checklist

- [ ] Domain is active and DNS A-record points to the cPanel server IP.
- [ ] Free Let's Encrypt / AutoSSL certificate is installed and active on the domain.
- [ ] Python 3.10, 3.11, or 3.12 is available in cPanel **Setup Python App**.
- [ ] MySQL database and user created in cPanel **MySQL® Database Wizard**.

---

## 🚀 22-Step Deployment Walkthrough

### STEP 1: Create MySQL Database in cPanel
Open **cPanel > MySQL® Database Wizard**. Enter database name (e.g., `cpuser_buildplus`).

### STEP 2: Create MySQL Database User
Enter username (e.g., `cpuser_dbuser`) and generate a secure 24+ character password.

### STEP 3: Assign User Privileges
Select **ALL PRIVILEGES** and click **Make Changes**.

### STEP 4: Upload Django Project Files
Upload the project folder to `/home/cpuser/construction_portal/` (via cPanel File Manager, SFTP, or Git).
*Do not upload your local `venv/` or `.git/` folder.*

### STEP 5: Create Python Application in cPanel
1. Navigate to **cPanel > Setup Python App** (under Software).
2. Click **Create Application**.
3. Fill in:
   - **Python Version:** `3.11` (or `3.10` / `3.12`)
   - **Application Root:** `construction_portal`
   - **Application URL:** your domain (e.g., `yourdomain.com`)
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application Entry Point:** `application`
4. Click **Create**.

### STEP 6: Enter Virtual Environment
Copy the command shown at the top of the Setup Python App page:
```bash
source /home/cpuser/virtualenv/construction_portal/3.11/bin/activate && cd /home/cpuser/construction_portal
```
Open **cPanel Terminal** and run the copied command.

### STEP 7: Install Production Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### STEP 8: Configure Environment Variables (`.env`)
Create `/home/cpuser/construction_portal/.env`:
```ini
DJANGO_SECRET_KEY=generate-a-secure-50-character-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=mysql
DB_NAME=cpuser_buildplus
DB_USER=cpuser_dbuser
DB_PASSWORD=your_mysql_password_here
DB_HOST=localhost
DB_PORT=3306

GEMINI_API_KEY=your_gemini_api_key_here

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=notifications@yourdomain.com
EMAIL_HOST_PASSWORD=your_smtp_app_password
```

### STEP 9: Configure `passenger_wsgi.py`
Ensure `passenger_wsgi.py` in your application root has:
```python
import os, sys
app_dir = os.path.dirname(__file__)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_config.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### STEP 10: Run Database Migrations
In the cPanel Terminal:
```bash
python manage.py migrate
```

### STEP 11: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### STEP 12: Configure Media Directory
Ensure `/home/cpuser/construction_portal/media/` exists and has permissions `755`:
```bash
mkdir -p media
chmod 755 media
```

### STEP 13: Create Superuser (Master Admin Account)
```bash
python manage.py createsuperuser
```

### STEP 14: Configure HTTPS & `.htaccess`
Copy `deployment/cpanel/.htaccess` to `/home/cpuser/public_html/.htaccess` to serve static and media files directly through Apache and forward dynamic requests to Passenger.

### STEP 15: Test Public Website
Open `https://yourdomain.com/` in your browser. Verify the homepage, navigation, services, projects, and calculator.

### STEP 16: Test Master Admin
Open `https://yourdomain.com/admin/`. Sign in with your superuser credentials. Verify executive KPI metrics, recent leads, and models.

### STEP 17: Test CMS Operations
Open `https://yourdomain.com/cms/`. Test service creation, FAQ publishing, and testimonial updates.

### STEP 18: Test CRM Sales Pipeline
Open `https://yourdomain.com/crm/`. Test lead creation, status updates, follow-up scheduling, and site visits.

### STEP 19: Test AI Customer Assistant
Open `https://yourdomain.com/aichatboat/`. Test conversation streams, RAG knowledge items, and human handoff toggle.

### STEP 20: Test Payments & Invoicing
Open `https://yourdomain.com/payment/`. Test payment request link generation, UPI QR display, and tax receipt creation.

### STEP 21: Test Client Self-Service Portal
Open `https://yourdomain.com/portal/login/`. Sign in as a test client and verify project milestones and invoices.

### STEP 22: Run Final Production Audit
Run the verification suite to ensure 100% operational readiness:
```bash
python manage.py check --deploy
```
