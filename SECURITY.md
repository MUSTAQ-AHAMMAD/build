# BUILD+ Enterprise Security Policy & Production Hardening Guide

Security is a foundational pillar of the BUILD+ Operations Hub. This document outlines the security controls, authentication safeguards, data protection standards, and deployment checklist enforced across the system.

---

## 1. Authentication & Access Governance

### Role-Based Access Control (RBAC)
The platform enforces strict role separation across five distinct tiers:
1. **Super Administrators:** Full Django system management, user group permissions, system settings.
2. **Operations & Finance Managers:** CRM access, commercial proposal approval, payment gateway configurations, refund settlements.
3. **Civil Engineers & Site Staff:** Assigned project updates, milestone logs, site visit inspection reports.
4. **Sales & CRM Estimators:** Lead management, follow-ups, BOQ estimate drafting.
5. **Authenticated Clients (Portal Users):** Scoped strictly to their own projects, proposals, invoices, and support tickets via `request.user` query filtering.

### Password Security Policy
- Passwords are encrypted using Django's default PBKDF2 with SHA-256 hash algorithm (600,000+ iterations).
- Minimum password length: 10 characters with complexity validation rules enabled.

---

## 2. HTTP & Session Security

The application includes production security middleware configured in `portal_config/settings.py`:

```python
# Production Cookie & Session Hardening
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400 * 7  # 7 days

# Security Headers
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

---

## 3. Financial & Payment Transaction Integrity

- **PCI-DSS Compliance:** The BUILD+ server never stores full credit card numbers, CVVs, or cardholder banking credentials. All card interactions are tokenized directly within payment gateway SDKs (Razorpay, Cashfree).
- **Cryptographic Webhook Verification:** Incoming gateway completion callbacks must have their cryptographic HMAC-SHA256 signature verified against the gateway secret before transactions are settled.
- **Idempotency:** Payment callbacks use database transactions (`transaction.atomic()`) and check for unique transaction references to prevent duplicate billing.
- **Manual Verification Audit Trail:** Manual bank transfer (NEFT/RTGS/UPI) approvals record the timestamp and user ID of the staff member approving the transaction.

---

## 4. Input Sanitization & Anti-XSS Protection

- **Django Template Auto-Escaping:** All user-supplied data in templates is auto-escaped by default to prevent Cross-Site Scripting (XSS).
- **Rich Text Content:** Blog and article content created in CMS uses sanitized HTML parsing before rendering.
- **SQL Injection Prevention:** 100% of database queries utilize the Django ORM parameterized query builder. Raw SQL string concatenation is strictly prohibited.

---

## 5. Media & File Upload Safety

- **Allowed Extensions:** Uploads are validated against strict whitelist extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.pdf`).
- **File Size Caps:** Uploads are limited to 10MB per file to mitigate Denial of Service (DoS) risks.
- **Execution Prevention:** The web server (Nginx/Apache) must be configured never to execute PHP, Python, or CGI scripts located inside the `/media/` directory.

### Nginx Media Hardening:
```nginx
location /media/ {
    alias /var/www/construction_portal/media/;
    # Disable script execution
    location ~* \.(php|pl|py|jsp|asp|sh|cgi)$ {
        deny all;
    }
}
```

---

## 6. Pre-Flight Production Checklist

Before launching into production:
- [ ] Set `DEBUG = False` in `.env`
- [ ] Set a unique, high-entropy `SECRET_KEY` in `.env`
- [ ] Verify `ALLOWED_HOSTS` matches only your production domain(s)
- [ ] Verify `CSRF_TRUSTED_ORIGINS` includes `https://yourdomain.com`
- [ ] Run `python manage.py check --deploy` and resolve any warnings
- [ ] Verify SSL certificate is installed and auto-renewing (`certbot`)
- [ ] Ensure `.env` is listed in `.gitignore` and has file permissions `600`
- [ ] Verify database backups (`mysqldump`) run automatically on a cron schedule
