# BUILD+ Construction Portal & CRM — Production Server Deployment Guide

This guide provides step-by-step instructions to deploy the BUILD+ Django application on a production server (Ubuntu/Linux VPS, Windows Server, or Cloud VM).

---

## 1. Production Architecture Overview

```text
       [ Clients / Browsers ]
                 │ (HTTPS : 443)
                 ▼
        [ Nginx Web Server ]
         │ (Reverse Proxy)
         ├── /static/  ──────► Serves static assets directly (/staticfiles)
         ├── /media/   ──────► Serves uploaded media (/media)
         └── / (all other) ──► Proxy pass to Gunicorn WSGI (127.0.0.1:8000)
                                     │
                                     ▼
                           [ Django Application ]
                                     │
                                     ▼
                             [ MySQL Database ]
```

---

## 2. Server Prerequisites (Ubuntu 22.04 / 24.04 LTS)

### Step 1: Update Server Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv python3-dev default-libmysqlclient-dev build-essential libssl-dev libffi-dev libjpeg-dev zlib1g-dev nginx mysql-server certbot python3-certbot-nginx git
```

### Step 2: Configure MySQL Database
```bash
sudo mysql
```
In the MySQL prompt:
```sql
CREATE DATABASE construction_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'construction_user'@'localhost' IDENTIFIED BY 'YOUR_STRONG_DATABASE_PASSWORD';
GRANT ALL PRIVILEGES ON construction_db.* TO 'construction_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 3. Application Deployment & Virtualenv Setup

### Step 1: Clone Repository
```bash
cd /var/www
sudo git clone <YOUR_GIT_REPOSITORY_URL> construction_portal
sudo chown -R $USER:$USER /var/www/construction_portal
cd /var/www/construction_portal
```

### Step 2: Create Python Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Production `.env`
```bash
cp .env.example .env
nano .env
```
Fill in your production details:
```ini
SECRET_KEY=generate-a-strong-random-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

DB_ENGINE=mysql
DB_NAME=construction_db
DB_USER=construction_user
DB_PASSWORD=YOUR_STRONG_DATABASE_PASSWORD
DB_HOST=127.0.0.1
DB_PORT=3306

GEMINI_API_KEY=your_google_ai_studio_api_key_here
```

### Step 4: Run Database Migrations & Static Files
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_blogs
python manage.py seed_crm
```

### Step 5: Create Superuser (or use default seed login)
```bash
python manage.py createsuperuser
```

---

## 4. Gunicorn Systemd Service Configuration

Create a systemd service file:
```bash
sudo nano /etc/systemd/system/construction.service
```

Paste the following configuration:
```ini
[Unit]
Description=BUILD+ Construction Portal & CRM Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/construction_portal
ExecStart=/var/www/construction_portal/venv/bin/gunicorn \
          --access-logfile - \
          --error-logfile /var/log/gunicorn/construction_error.log \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          portal_config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Create log directory and set permissions:
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/gunicorn
sudo chown -R www-data:www-data /var/www/construction_portal/media
sudo chown -R www-data:www-data /var/www/construction_portal/staticfiles

sudo systemctl daemon-reload
sudo systemctl start construction
sudo systemctl enable construction
sudo systemctl status construction
```

---

## 5. Nginx Web Server Configuration

Create an Nginx server block:
```bash
sudo nano /etc/nginx/sites-available/construction
```

Paste the configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    # Static Assets
    location /static/ {
        alias /var/www/construction_portal/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Uploaded Media
    location /media/ {
        alias /var/www/construction_portal/media/;
        expires 30d;
    }

    # Pass all other requests to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and test:
```bash
sudo ln -s /etc/nginx/sites-available/construction /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 6. Enable Free SSL Certificate (Let's Encrypt / Certbot)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
Certbot will automatically configure HTTPS redirection in Nginx and set up automatic renewal cron jobs.

---

## 7. Windows Server Deployment Option (Alternative)

If deploying on a Windows Server with IIS:
1. Install Python 3.12+ and MySQL Server for Windows.
2. Install `pip install -r requirements.txt`.
3. Use **Waitress** production WSGI runner:
   ```powershell
   waitress-serve --listen=127.0.0.1:8000 portal_config.wsgi:application
   ```
4. Configure **IIS** as a reverse proxy using `HttpPlatformHandler` or `URL Rewrite / ARR`.

---

## 8. Post-Deployment Verification Checklist

| Item | Command / Test | Status |
|---|---|---|
| **System Check** | `python manage.py check --deploy` | ✅ Ready |
| **All Automated Tests** | `python manage.py test crm.tests blog.tests core.tests` | ✅ 34/34 Passing |
| **Static Bundling** | `python manage.py collectstatic` | ✅ 132 Assets Copied |
| **Public Website** | Visit `https://yourdomain.com` | ✅ Accessible |
| **Blog & Knowledge Centre** | Visit `https://yourdomain.com/blog/` | ✅ Accessible |
| **CRM Portal** | Visit `https://yourdomain.com/cms/crm/` | ✅ Accessible |
| **Lead Submission** | Submit form on `/contact/` -> Verify in `/cms/crm/leads/` | ✅ Auto-Synced |
| **SSL / HTTPS** | `https://` padlock in browser | ✅ Active |

---

## 9. Administrator & Staff Default Credentials

- **Superuser Admin:** `admin` / `admin123`
- **Sales Representative:** `rajesh_sales` / `sales123`
- **Site Engineer:** `vikram_engineer` / `engineer123`

*(Important: Change default passwords in the CMS immediately after initial server login).*


---

## 7. cPanel / Shared Hosting Deployment Guide (Setup Python App)

Many enterprise hosting providers and shared environments utilize **cPanel** with CloudLinux **Setup Python App (Passenger WSGI)** and **MySQL Database Wizard**. Follow these steps for seamless deployment:

### Step 1: Create MySQL Database in cPanel
1. In cPanel, navigate to **MySQL® Database Wizard**.
2. **Step 1:** Enter database name (e.g. `cpaneluser_construction`).
3. **Step 2:** Create a database user (e.g. `cpaneluser_dbuser`) with a strong password.
4. **Step 3:** Grant **ALL PRIVILEGES** to the user for this database and click **Make Changes**.

### Step 2: Configure Python Application in cPanel
1. In cPanel, navigate to **Setup Python App** (under Software section).
2. Click **Create Application**.
3. Set the configuration:
   - **Python Version:** Select `3.10`, `3.11`, or `3.12`.
   - **Application Root:** `construction_portal` (or your folder name in `/home/username/`).
   - **Application URL:** Select your domain or subdomain.
   - **Application Startup File:** `passenger_wsgi.py`.
   - **Application Entry Point:** `application`.
4. Click **Create**.

### Step 3: Upload Code & Install Requirements
1. Upload the project files to `/home/username/construction_portal/` (via cPanel File Manager, Git Version Control, or SFTP).
2. Ensure your `.env` file is placed in `/home/username/construction_portal/.env` with your cPanel MySQL credentials:
   ```env
   DB_ENGINE=mysql
   DB_NAME=cpaneluser_construction
   DB_USER=cpaneluser_dbuser
   DB_PASSWORD=your_cpanel_db_password
   DB_HOST=localhost
   DB_PORT=3306
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```
3. In cPanel **Setup Python App**, copy the command to enter the virtual environment:
   ```bash
   source /home/username/virtualenv/construction_portal/3.11/bin/activate && cd /home/username/construction_portal
   ```
4. Access **Terminal** in cPanel, paste the command, and install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Step 4: Configure `passenger_wsgi.py`
Ensure the file `passenger_wsgi.py` in your application root has the following code:
```python
import os
import sys

# Add application directory to sys.path
app_dir = os.path.dirname(__file__)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 5: Run Migrations & Collect Static
In the cPanel Terminal:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Step 6: Static & Media Routing in `.htaccess`
In your `public_html/.htaccess` file, ensure static and media requests are served directly by Apache:
```apache
RewriteEngine On

# Serve static assets directly
RewriteRule ^static/(.*)$ /home/username/construction_portal/staticfiles/$1 [L]

# Serve media uploads directly
RewriteRule ^media/(.*)$ /home/username/construction_portal/media/$1 [L]
```

### Step 7: Restart Application
In cPanel **Setup Python App**, click **Restart** on your application card. Your BUILD+ portal is now live!
