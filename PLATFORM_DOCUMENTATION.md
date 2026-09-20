# COMPLETE PLATFORM DOCUMENTATION & ARCHITECTURAL REFERENCE
## Construction, Renovation, Demolition, Reconstruction, Redevelopment, Property & NRI Services Platform

**Platform Classification:** Full-Stack Enterprise Construction & Property Services Portal + Dynamic CMS + Operational CRM + Google Gemini AI Consultant + Gateway-Agnostic Payment & UPI Platform + Client Project Portal  
**Framework Stack:** Python 3.14 / Django 5.x / MySQL & SQLite / HTML5 & CSS3 / Bootstrap 5.3 / Vanilla JavaScript / Google Gemini Generative AI  
**Deployment Model:** Linux (Gunicorn + Nginx) / Windows IIS / Reverse-Proxy Architecture  

---

## 1. Master System Overview & Ecosystem Map

The platform is designed as an integrated business engine linking public acquisition, AI qualification, operational lead tracking, stage-wise estimation, secure online billing, turnkey project engineering, and post-handover client ticketing into a single lifecycle:

```
                                  PUBLIC WEBSITE & CHANNELS
                  (Home, 6 Service Pillars, Portfolio, Blog, Dynamic FAQs, AI Chatbot)
                                              │
                                              ▼
                                 ENQUIRY & AI LEAD DISCOVERY
                    (Intent Classification, Budget, Timeline, Property Condition)
                                              │
                                              ▼
                                 CENTRAL CRM SALES ENGINE
               (Lead Assignment, Priority Matrix, Activity Logs, Site Inspections)
                                              │
                                              ▼
                                 COMMERCIAL BOQ & PROPOSALS
                    (Line-by-line Cost Breakdown, 1-Click Client Acceptance)
                                              │
                                              ▼
                             GATEWAY-AGNOSTIC PAYMENT HUB (/pay/)
              (Razorpay, Stripe, Direct UPI Intent, Dynamic QR, NEFT/RTGS Verification)
                                              │
                                              ▼
                             CLIENT PROJECT EXECUTION & TRACKER
                 (Milestone Schedules, Work Packages, Engineering Docs, Snag Lists)
                                              │
                                              ▼
                                 POST-HANDOVER CLIENT PORTAL
                 (Tax Receipts, Document Repository, Support Tickets & Helpdesk)
```

---

## 2. Django Application Architecture

The platform is structured into modular Django applications, ensuring clear separation of concerns, high maintainability, and zero circular dependencies:

```
construction/
├── portal_config/        # Core Django settings, WSGI, ASGI, Root URL routing
├── core/                 # Website Settings, Testimonials, Team, FAQs, Customer Portal
├── services/             # Dynamic Service CMS, Scope, Process, FAQs, Per-service Pricing
├── projects/             # Portfolio CMS, Engineering Tasks, Document Repository, Support Desk
├── blog/                 # Content Management, Categories, Tags, SEO Metadata
├── enquiries/            # Public Enquiry Forms, Site Visit Booking Desk
├── crm/                  # Lead Pipeline, Follow-ups, Site Visits, Estimates, Proposals, Activity Logs
├── ai_assistant/         # Gemini 2.5/Pro Integration, AI Lead Extraction, Staff Chat Console
├── payments/             # Gateway Adapters, Razorpay, Stripe, Dynamic UPI QR, Invoices, Receipts
├── static/ & templates/  # Bootstrap 5 frontend assets and modular template hierarchy
```

---

## 3. Core Database Models & Relationships

| App | Key Models | Key Purpose & Fields |
|---|---|---|
| **`core`** | `WebsiteSettings`, `Testimonial`, `FAQ`, `TeamMember` | Singleton business profile (GSTIN, phones, cities, social), client reviews, category-filtered FAQs. |
| **`services`** | `ServiceCategory`, `Service` | 6 Primary pillars (Construction, Renovation, Demolition & Reconstruction, Redevelopment, Property & Land, NRI Services), full scope, FAQs, SEO. |
| **`projects`** | `Project`, `ProjectTask`, `ProjectDocument`, `SupportTicket`, `SupportTicketMessage` | 360° Construction tracking: milestone %, contract value, tasks (foundation, MEP, finishes), document vault (drawings, NOCs), client ticket desk. |
| **`enquiries`**| `Enquiry` | Universal web contact capture (service type, city, property details, budget, timeline, source). |
| **`crm`** | `Lead`, `LeadSource`, `FollowUp`, `SiteVisit`, `Estimate`, `LeadNote`, `LeadActivity` | End-to-end sales pipeline: lead scoring (`URGENT`, `HIGH`), site inspection audits, itemized BOQ estimates, status transitions. |
| **`ai_assistant`**| `AIChatSession`, `AIChatMessage`, `AIKnowledgeDocument`, `AIHandoffRequest` | AI conversation telemetry, extracted JSON parameters, prompt knowledge base, human staff handoff desk. |
| **`payments`** | `PaymentGateway`, `PaymentSettings`, `UPIConfiguration`, `ServicePaymentConfiguration`, `PaymentRequest`, `PaymentTransaction`, `PaymentReceipt`, `ManualPaymentProof`, `PaymentRefund`, `PaymentAuditLog` | Gateway-agnostic engine, dynamic NPCI `upi://pay` URI, base64 dynamic QR generator, GST tax receipts (`REC-YYYY-XXXXXX`), staff bank proof desk. |

---

## 4. Key Subsystem Workflows

### 4.1. AI Construction Consultant & Lead Qualification
- **Public Entry:** Floating, mobile-optimized chatbot widget on all public pages.
- **Intent Recognition:** Understands queries across building new homes, flat renovations, building demolition, land due diligence, NRI property supervision, and payment instructions.
- **Controlled Lead Creation:** Incrementally collects customer name, phone, email, location, property condition, budget, and timeline without overwhelming the user.
- **Automatic CRM Ingestion:** Creates a `Lead` tagged with `source="AI CHATBOT"`, attaches an AI executive summary, assigns suggested priority (`HIGH`/`URGENT`), and logs activity in `LeadActivity`.
- **Human Handoff:** Instantly shifts conversation to `HUMAN AGENT ACTIVE` upon detecting complex disputes, structural safety concerns, or user request.

### 4.2. Gateway-Agnostic Payment & Dynamic UPI Engine
- **Adapter Hierarchy:** `BasePaymentGateway` abstract class implemented by `RazorpayAdapter`, `StripeAdapter`, `UPIAdapter`, `CustomHTMLEmbedAdapter`, and `ManualPaymentAdapter`.
- **Security Boundaries:** Zero API secrets exposed in public HTML. Client-side amounts are never trusted; status changes to `SUCCESS` strictly require HMAC-SHA256 signature checks, webhook events, or authorized staff bank verification.
- **Dynamic UPI & QR:** Generates NPCI-compliant `upi://pay?pa=...&pn=...&am=...&cu=INR&tn=...&tr=...` URIs and dynamic server-side base64 QR codes using `qrcode` (Pillow).
- **Offline / Bank Transfer Desk:** Allows customers to upload NEFT/RTGS UTR numbers and counterfoil payment slips. Staff review via `/cms/payments/manual-verification/` with 1-click **Approve** (marks paid, issues receipt, updates CRM) or **Reject**.
- **Automated Tax Receipts:** Auto-generates computer-generated, print-ready official receipts (`REC-YYYY-XXXXXX`) with itemized subtotal, 18% GST calculation, and corporate branding.

### 4.3. Client Portal (`/portal/`)
- **Authentication:** Dedicated client login (`/portal/login/`) and registration (`/portal/register/`). Automatically associates portal users with existing CRM leads and construction projects by email and phone number.
- **Executive Dashboard (`/portal/`)**: Real-time overview of active projects, upcoming site visits, pending estimates, active proposals, and cleared tax receipts.
- **Live Project Tracker (`/portal/projects/<slug>/`)**: Visual execution progress bar, milestone payment status, work package breakdown (site prep, RCC structure, MEP, flooring, finishes), and shared document vault.
- **Proposal Acceptance (`/portal/proposals/`)**: Clients can review commercial terms and click **✓ Accept Proposal Online** or **Decline**.
- **Support Desk (`/portal/support/`)**: Threaded discussion desk allowing clients to raise queries with category tags (`project_progress`, `billing_payment`, `site_inspection`, `quality_materials`) and attachments.

---

## 5. Security & Production Deployment Standards

1. **Zero Secret Leaks:** All API keys, database credentials, and webhook secrets reside in `.env`.
2. **CSRF & XSS Protection:** Native Django CSRF tokens on all forms; output sanitization across template contexts.
3. **Database Transactions:** Atomic database transactions (`transaction.atomic()`) for financial settlements, milestone updates, and lead status changes.
4. **Static & Media Asset Delivery:** Configured for `collectstatic` with dedicated `media/` uploads directory for blueprints, photos, and payment proofs.
5. **Automated Test Coverage:** 52 comprehensive unit and integration tests verifying views, adapters, services, permissions, and models with 100% pass rate.

---

## 6. Local Quickstart & Verification

```powershell
# 1. Navigate to project root
cd "D:\Web design\construction"

# 2. Apply database migrations
python manage.py migrate

# 3. Seed payment gateways and sample data
python manage.py seed_payment_gateways

# 4. Run automated test suite
python manage.py test projects.tests payments.tests ai_assistant.tests crm.tests blog.tests core.tests

# 5. Start development server
python manage.py runserver
```

**Key URLs:**
- Public Website: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Client Portal: [http://127.0.0.1:8000/portal/](http://127.0.0.1:8000/portal/)
- CMS Management Hub: [http://127.0.0.1:8000/cms/](http://127.0.0.1:8000/cms/)
- Payments Console: [http://127.0.0.1:8000/cms/payments/](http://127.0.0.1:8000/cms/payments/)
- AI Chat Management: [http://127.0.0.1:8000/cms/ai/](http://127.0.0.1:8000/cms/ai/)
- Django Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
