# BUILD+ Enterprise REST & AJAX API Specification

The BUILD+ platform exposes clean JSON endpoints for administrative dashboard operations, real-time AJAX interactions, client portal communications, and payment gateway webhooks.

---

## 1. Authentication & Security Headers

| Mechanism | Usage | Header Format |
| :--- | :--- | :--- |
| **Session Authentication** | Standard for browser UI / AJAX | Cookie: `sessionid=...` |
| **CSRF Protection** | Required for all `POST`, `PUT`, `DELETE` requests | `X-CSRFToken: <token_value>` |
| **Staff Permission Check** | Administrative / CMS endpoints | Handled via `@staff_member_required` |

---

## 2. CRM & Sales Pipeline Endpoints

### 1. Update Lead Status
Updates the pipeline status of an active lead.

- **URL:** `/crm/api/leads/<lead_id>/update-status/`
- **Method:** `POST`
- **Permissions:** Staff / Estimator
- **Request Body (JSON):**
  ```json
  {
    "status": "QUALIFIED",
    "notes": "Spoke to client. Site visit arranged for Monday."
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "status": "success",
    "lead_id": 42,
    "new_status": "QUALIFIED",
    "updated_at": "2026-09-05T02:30:00Z"
  }
  ```

### 2. Schedule Site Visit
Books an on-site civil inspection.

- **URL:** `/crm/api/site-visits/create/`
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "lead_id": 42,
    "visit_date": "2026-09-10",
    "visit_time": "14:30:00",
    "engineer_id": 3,
    "site_address": "Plot 14B, Royal Enclave, Bengaluru",
    "notes": "Bring foundation moisture meter"
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "status": "success",
    "visit_id": 18,
    "scheduled_at": "2026-09-10 14:30:00"
  }
  ```

---

## 3. Payments & Invoicing Endpoints

### 1. Initiate Online Transaction
Initiates an order for client checkout via Razorpay or Cashfree.

- **URL:** `/pay/api/initiate/`
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "payment_request_uuid": "e3a8904b-7419-4b47-8a62-736025d5d852",
    "gateway_id": 1,
    "customer_name": "Vikram Malhotra",
    "customer_email": "vikram@example.com",
    "customer_phone": "+919876543210"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "status": "success",
    "transaction_id": "TXN20260905001",
    "gateway_order_id": "order_P19xABC123",
    "amount": 25000.00,
    "currency": "INR",
    "key_id": "rzp_live_abc123"
  }
  ```

### 2. Verify Payment Callback / Webhook
Confirms cryptographic signature of completed transaction.

- **URL:** `/pay/api/verify/`
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "transaction_id": "TXN20260905001",
    "razorpay_payment_id": "pay_98xyz456",
    "razorpay_order_id": "order_P19xABC123",
    "razorpay_signature": "a1b2c3d4e5f6..."
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "status": "verified",
    "receipt_number": "REC-2026-0042",
    "receipt_url": "/pay/receipt/REC-2026-0042/"
  }
  ```

### 3. Submit Manual Payment Proof (UTR / Bank Slip)
Allows clients to upload NEFT/RTGS transaction screenshots.

- **URL:** `/pay/api/submit-proof/`
- **Method:** `POST` (Multipart Form Data)
- **Parameters:**
  - `request_uuid`: UUID of payment request
  - `utr_number`: Bank reference / UTR number
  - `proof_image`: File upload (JPG, PNG, PDF <= 5MB)
- **Response (`200 OK`):**
  ```json
  {
    "status": "submitted",
    "message": "Payment proof submitted for manual verification. Our accounts team will verify within 2-4 business hours."
  }
  ```

---

## 4. AI Customer Assistant & RAG Endpoints

### 1. Initialize Conversation
Starts a new conversational session for visitor inquiries.

- **URL:** `/ai/api/init/`
- **Method:** `POST`
- **Response (`200 OK`):**
  ```json
  {
    "session_id": "sess_8892f3a",
    "welcome_message": "Hello! Welcome to BUILD+. How can our civil engineering and architectural team assist your project today?",
    "suggested_prompts": [
      "Cost estimate for 3BHK construction",
      "Book a site inspection",
      "Turnkey interior renovation"
    ]
  }
  ```

### 2. Send Message & Receive AI Reply
Processes user message through Google Gemini with RAG domain context.

- **URL:** `/ai/api/chat/`
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "session_id": "sess_8892f3a",
    "message": "I want to build a 2500 sq ft duplex villa in Bangalore. What would be the approximate cost?"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "reply": "For a premium turnkey 2,500 sq ft duplex villa in Bangalore, construction costs typically range from ₹2,100 to ₹2,650 per sq ft including civil structure, premium finishes, and electrical/plumbing works...",
    "detected_intent": "ESTIMATE_INQUIRY",
    "lead_created": true,
    "lead_id": 43
  }
  ```

### 3. CMS Live Agent Takeover
Allows human operator in the CMS to take over an AI conversation.

- **URL:** `/cms/ai/conversations/<conv_id>/takeover/`
- **Method:** `POST`
- **Permissions:** Staff
- **Response (`200 OK`):**
  ```json
  {
    "status": "takeover_active",
    "conversation_id": 14,
    "agent": "admin"
  }
  ```

---

## 5. Standard Error Responses

All API endpoints return standard HTTP error status codes with JSON error payloads:

```json
{
  "status": "error",
  "error_code": "VALIDATION_FAILED",
  "message": "The phone number provided is invalid.",
  "errors": {
    "phone_number": ["Enter a valid 10-digit mobile number."]
  }
}
```
