# BUILD+ Enterprise Construction & Infrastructure Operations Hub

> **A comprehensive, enterprise-grade Django 5 web application and operational management platform for construction, civil engineering, renovation, and property development firms.**

---

## 🌟 Platform Highlights

BUILD+ combines a high-converting public corporate web presence with an all-in-one operational ecosystem:
- **Executive Admin Dashboard:** Unified oversight of construction projects, financial volume, pipeline metrics, and team operations.
- **Full-Featured CRM Suite:** Lead scoring, stage management, automated follow-up reminders, site visit booking, and BOQ estimate generation.
- **Project Tracker & Client Portal:** Real-time milestone progress tracking, civil inspection logs, progress photo galleries, and secure document exchange.
- **Payment & Invoicing Hub:** Multi-gateway payment engine (Razorpay, Cashfree, UPI VPA, Bank NEFT/RTGS), automated GST tax receipts, manual proof audits, and refund handling.
- **AI Customer Assistant:** Context-aware RAG-powered chatbot utilizing Google Gemini to answer prospective client queries and automatically capture qualified leads into CRM.
- **CMS & Engineering Blog:** Complete content management workflow with rich text publishing, category indexing, and SEO meta controls.
- **PWA Mobile-First Experience:** Standalone Progressive Web App support, touch-optimized bottom navigation, 44px+ tap targets, dual desktop/mobile views, and zero cartoon emojis.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Django 5.x (Python 3.10 / 3.11 / 3.12 / 3.14 compatible) |
| **Database** | MySQL 8.0+ / MariaDB 10.5+ (Production) \| PostgreSQL 14+ \| SQLite 3 (Dev) |
| **Frontend Framework** | Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Vanilla JavaScript (ES6+) |
| **Styling & Theme** | Modern Design Token System (`admin_theme.css`), Dual Light/Dark Theme Switcher |
| **Mobile & PWA** | Web App Manifest (`manifest.json`), Network-First Service Worker (`sw.js`) |
| **AI Integration** | Google Gemini API (`gemini-1.5-flash`) via `google-genai` / REST |
| **Payment Gateways** | Razorpay, Cashfree, UPI Deep-Linking, Bank Transfer Verification |

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10 or higher
- Git
- MySQL Server (or use default SQLite for rapid local testing)

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone <repository_url> construction_hub
cd construction_hub

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```
*(On Windows: `copy .env.example .env`)*

### Step 4: Run Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
*(Default test credentials in development: Username: `admin` / Password: `adminpassword123`)*

### Step 6: Collect Static Assets & Run Server
```bash
python manage.py collectstatic --noinput
python manage.py runserver 127.0.0.1:8000
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 🔐 Administrative Access & Key Endpoints

| Portal / Module | URL Path | Description |
| :--- | :--- | :--- |
| **Main Website** | `/` | Public corporate homepage, services, projects, contact |
| **Executive Admin Hub** | `/admin/` | Custom branded executive dashboard and Django admin |
| **CRM Sales Dashboard** | `/crm/` | Leads, follow-ups, site inspections, estimates |
| **CMS Content Desk** | `/cms/` | Service catalogs, company enquiries, pages |
| **CMS Blog Desk** | `/cms/blog/dashboard/` | Blog article creation, category management |
| **Payments Management** | `/cms/payments/` | Live transactions, gateways, manual verification, GST invoices |
| **AI Assistant Control** | `/cms/ai/dashboard/` | Chat session monitoring, human takeover, knowledge base |
| **Client Portal** | `/portal/` | Self-service client project tracker, proposals, receipts |

---

## 🧪 Automated Testing & Verification

Run the comprehensive test suite:
```bash
# Run all unit and integration tests
python manage.py test

# Verify deployment readiness
python manage.py check --deploy

# Run the complete Admin Suite DOM & Route verification audit
python scratch/verify_full_admin_suite.py
```

---

## 📚 Documentation Index

- [Production Deployment Guide (`DEPLOYMENT.md`)](DEPLOYMENT.md) — Step-by-step setup for cPanel, Linux VPS (Nginx + Gunicorn), and Windows Server.
- [Database Schema & Architecture (`DATABASE.md`)](DATABASE.md) — MySQL table diagrams, relationships, indexes, and backup procedures.
- [REST & AJAX API Reference (`API.md`)](API.md) — API endpoints for CRM, Payments, AI Chatbot, and Enquiries.
- [Security Policy & Hardening (`SECURITY.md`)](SECURITY.md) — CSRF, cookie hardening, RBAC, and payment safety.

---

## 📄 License & Intellectual Property

&copy; 2026 BUILD+ Construction & Infrastructure Management Systems. All rights reserved.
