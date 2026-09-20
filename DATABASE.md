# BUILD+ Enterprise Database Architecture & Schema Specification

This document provides a comprehensive overview of the relational database architecture, tables, schemas, relationships, indexing strategies, and maintenance procedures for the **BUILD+ Corporate Operations Hub**.

---

## 1. Engine Compatibility & Production Recommendations

The BUILD+ platform is engineered for production deployment on **MySQL 8.0+ / MariaDB 10.5+** (standard in cPanel, Plesk, and Linux VPS environments) with seamless fallback support for **PostgreSQL 14+** and **SQLite 3** for local development.

### Recommended MySQL Server Configuration (`my.cnf`):
```ini
[mysqld]
character-set-server = utf8mb4
collation-server     = utf8mb4_unicode_ci
default-storage-engine = InnoDB
innodb_file_per_table = 1
innodb_buffer_pool_size = 512M # Adjust to 50-70% of available RAM
max_connections = 150
```

---

## 2. Core Modules & Table Architecture

```text
┌────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   AUTH_USER    │◄──────┤   CRM_LEAD      │◄──────┤  CRM_FOLLOWUP   │
└───────┬────────┘       └────────┬────────┘       └─────────────────┘
        │                         │
        │                         ├────────────────► CRM_SITEVISIT
        │                         │
        │                         ├────────────────► CRM_ESTIMATE
        │                         │
        │                         └────────────────► CRM_PROPOSAL
        ▼                                                  ▲
┌────────────────┐                                         │
│ PROJECTS_PROJ  │◄────────────────────────────────────────┘
└───────┬────────┘
        │
        ├────────────────► PROJECTS_MILESTONE
        ├────────────────► PROJECTS_IMAGE
        └────────────────► PROJECTS_UPDATE
```

### Module 1: CRM & Sales Pipeline (`crm`)
| Table Name | Model | Description | Primary Key | Key Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| `crm_lead` | `Lead` | Central customer prospect record, status, budget, intent | `id` (BigAuto) | `assigned_to` -> `auth_user` |
| `crm_leadfollowup` | `LeadFollowUp` | Sales interactions, calls, WhatsApp touchpoints | `id` (BigAuto) | `lead_id` -> `crm_lead`, `created_by` -> `auth_user` |
| `crm_sitevisit` | `SiteVisit` | Civil engineer on-site inspection bookings & GPS data | `id` (BigAuto) | `lead_id` -> `crm_lead`, `engineer` -> `auth_user` |
| `crm_estimate` | `Estimate` | Bill of Quantities (BOQ), itemized costs, margins | `id` (BigAuto) | `lead_id` -> `crm_lead` |
| `crm_proposal` | `Proposal` | Formal commercial contract, validity period, sign-off | `id` (BigAuto) | `lead_id` -> `crm_lead` |

### Module 2: Projects & Execution Tracker (`projects`)
| Table Name | Model | Description | Primary Key | Key Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| `projects_projectcategory` | `ProjectCategory` | Residential, Commercial, Renovation, Interior | `id` (BigAuto) | None |
| `projects_project` | `Project` | Master construction project, budget, timeline, progress % | `id` (BigAuto) | `category_id`, `client_id` -> `auth_user`, `lead_id` -> `crm_lead` |
| `projects_projectmilestone` | `ProjectMilestone` | Foundation, Framing, MEP, Finishing completion stages | `id` (BigAuto) | `project_id` -> `projects_project` |
| `projects_projectimage` | `ProjectImage` | Site photo documentation, before/after showcases | `id` (BigAuto) | `project_id` -> `projects_project` |
| `projects_projectupdate` | `ProjectUpdate` | Weekly client construction log & site manager notes | `id` (BigAuto) | `project_id` -> `projects_project` |

### Module 3: Payments, Invoicing & Gateway Engine (`payments`)
| Table Name | Model | Description | Primary Key | Key Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| `payments_paymentsettings` | `PaymentSettings` | Global tax rate, GSTIN, currency symbol, default gateway | `id` (BigAuto) | Singleton |
| `payments_paymentgateway` | `PaymentGateway` | Configured gateways (Razorpay, Cashfree, UPI, Bank Transfer) | `id` (BigAuto) | None |
| `payments_paymentrequest` | `PaymentRequest` | Client payment link requests, invoice milestones | `id` (BigAuto) | `lead_id` -> `crm_lead`, `project_id` -> `projects_project` |
| `payments_paymenttransaction` | `PaymentTransaction` | Immutable transaction ledger, gateway refs, timestamps | `id` (BigAuto) | `payment_request_id`, `service_id` -> `services_service` |
| `payments_taxreceipt` | `TaxReceipt` | Official serial-numbered GST tax invoices | `id` (BigAuto) | `transaction_id` -> `payments_paymenttransaction` |
| `payments_manualpaymentproof`| `ManualPaymentProof` | Bank NEFT/RTGS/UPI screenshot submissions & UTR audits | `id` (BigAuto) | `payment_request_id`, `verified_by` -> `auth_user` |
| `payments_paymentrefund` | `PaymentRefund` | Processed client refunds, credit notes, audit notes | `id` (BigAuto) | `transaction_id`, `initiated_by` -> `auth_user` |

### Module 4: AI Customer Assistant (`ai_assistant`)
| Table Name | Model | Description | Primary Key | Key Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| `ai_assistant_aiconversation` | `AIConversation` | Chat session, lead classification, takeover flag | `id` (BigAuto) | `lead_id` -> `crm_lead` (nullable) |
| `ai_assistant_aimessage` | `AIMessage` | Chat message, sender (user/bot/agent), intent score | `id` (BigAuto) | `conversation_id` -> `ai_assistant_aiconversation` |
| `ai_assistant_aiknowledgeitem`| `AIKnowledgeItem`| Company FAQ, service details, pricing guidelines for RAG | `id` (BigAuto) | None |
| `ai_assistant_aisettings` | `AISettings` | Gemini model selection, temperature, auto-lead trigger | `id` (BigAuto) | Singleton |

### Module 5: Content Management & Blog (`blog`, `services`, `core`)
| Table Name | Model | Description | Primary Key | Key Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| `blog_category` | `Category` | Blog categories (Architecture, Tech, Tips) | `id` (BigAuto) | None |
| `blog_blog` | `Blog` | Articles, slug, SEO tags, reading time, status | `id` (BigAuto) | `category_id`, `author_id` -> `auth_user` |
| `services_service` | `Service` | Offered construction services, rates, brochures | `id` (BigAuto) | `category_id` |
| `enquiries_enquiry` | `Enquiry` | Inbound contact forms, consultation inquiries | `id` (BigAuto) | None |

---

## 3. Database Indexes & Performance Optimization

All foreign keys are indexed automatically by Django InnoDB engine. In addition, composite and high-cardinality indexes are established:

```sql
-- High-frequency lookup indexes
CREATE INDEX idx_crm_lead_status_created ON crm_lead(status, created_at);
CREATE INDEX idx_crm_lead_phone ON crm_lead(phone_number);
CREATE INDEX idx_pay_tx_ref ON payments_paymenttransaction(payment_reference);
CREATE INDEX idx_pay_tx_status_date ON payments_paymenttransaction(status, created_at);
CREATE INDEX idx_ai_conv_session ON ai_assistant_aiconversation(session_key);
CREATE INDEX idx_proj_slug ON projects_project(slug);
```

---

## 4. Backup & Disaster Recovery Procedures

### 1. Automated CLI Backup (`mysqldump`)
Run as a nightly cron job:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/mysql"
mkdir -p $BACKUP_DIR
mysqldump --single-transaction --quick --lock-tables=false     -u construction_user -p'YOUR_PASSWORD' construction_db     | gzip > "$BACKUP_DIR/buildplus_$DATE.sql.gz"

# Retain last 30 days of backups
find $BACKUP_DIR -name "buildplus_*.sql.gz" -mtime +30 -delete
```

### 2. Database Restore from Backup
```bash
gunzip < /var/backups/mysql/buildplus_20260905_000000.sql.gz | mysql -u construction_user -p construction_db
```

### 3. phpMyAdmin GUI Backup
1. Log into your cPanel or server phpMyAdmin.
2. Select `construction_db`.
3. Click the **Export** tab.
4. Select **Quick** export method and **SQL** format, then click **Export**.
