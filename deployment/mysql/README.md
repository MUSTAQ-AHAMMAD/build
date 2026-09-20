# BUILD+ Enterprise — MySQL Production Database Setup & Maintenance

This guide explains how to set up, configure, and maintain the MySQL/MariaDB database for BUILD+ on production servers (cPanel, Plesk, Linux VPS, or Cloud DB).

---

## 1. Prerequisites & Specifications

| Parameter | Recommended Production Value |
| :--- | :--- |
| **Database Engine** | MySQL 8.0+ or MariaDB 10.5+ |
| **Storage Engine** | InnoDB (ACID compliant, row-level locking) |
| **Character Set** | `utf8mb4` |
| **Collation** | `utf8mb4_unicode_ci` |
| **Default Port** | `3306` |
| **Host** | `localhost` or `127.0.0.1` |

---

## 2. Setup via cPanel MySQL® Database Wizard (Recommended for Shared/cPanel)

1. Log into your **cPanel** dashboard.
2. Under the **Databases** section, click **MySQL® Database Wizard**.
3. **Step 1 — Create Database:**
   - Enter your database name (e.g., `cpaneluser_buildplus`). Click **Next Step**.
4. **Step 2 — Create Database User:**
   - Enter username (e.g., `cpaneluser_dbuser`).
   - Use the **Password Generator** to create a strong 24+ character password.
   - Save this password securely. Click **Create User**.
5. **Step 3 — Add User to Database:**
   - Check **ALL PRIVILEGES**. Click **Make Changes**.
6. Note your exact **Database Name**, **Username**, and **Password** for your `.env` configuration.

---

## 3. Setup via CLI / phpMyAdmin

### CLI (Linux VPS / Terminal):
```bash
mysql -u root -p < deployment/mysql/create_database.sql
```
*(Make sure you replace `DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASSWORD` before running).*

### phpMyAdmin Import:
1. Open **phpMyAdmin** from cPanel.
2. Select your newly created database.
3. Click the **Import** tab.
4. Choose `deployment/mysql/schema_export.sql` and click **Import**.

---

## 4. Applying Migrations via Django

Once the database credentials are added to your `.env` file, apply all Django migrations:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 5. Automated Backup & Recovery Procedures

### Nightly Automated CLI Backup (`mysqldump`):
```bash
mysqldump --single-transaction --quick --lock-tables=false     -u DATABASE_USER -p'DATABASE_PASSWORD' DATABASE_NAME     | gzip > "/var/backups/buildplus_$(date +%Y%m%d_%H%M%S).sql.gz"
```

### Restoration Command:
```bash
gunzip < /var/backups/buildplus_20260905_000000.sql.gz | mysql -u DATABASE_USER -p DATABASE_NAME
```
