# NGiT FastAPI Backend — Execution Plan

**Project:** NGiT Program Registration, Payment & Access Platform
**Focus:** FastAPI Backend (excludes Streamlit admin portal)
**Status:** Not Started
**Created:** 2026-08-15

---

## Architecture Overview

```
Paystack → FastAPI Backend → Google Sheets (data) + Gmail (email)
                ↑
          Streamlit Admin (separate project, consumes REST APIs)
```

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Pydantic, HTTPX, Google Sheets API, Gmail API, Paystack REST API

**Core Principle:** Programs/cohorts are configuration data, not hard-coded logic. Adding a new program must not require code changes.

---

## Phase 1 — Backend Foundation

**Goal:** FastAPI app boots, health endpoint responds, configuration loaded from environment.

**Depends on:** Nothing

**Milestone:** `GET /health` returns `{"status": "ok"}` with env config loaded.

### Tasks

| # | Task | Details |
|---|------|---------|
| 1.1 | Create project structure | Create all directories per PRD §51: `backend/`, `backend/api/`, `backend/models/`, `backend/schemas/`, `backend/services/`, `backend/repositories/`, `backend/utils/` |
| 1.2 | Create `requirements.txt` | `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `httpx`, `python-dotenv`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` |
| 1.3 | Create `backend/config.py` | Pydantic `BaseSettings` loading: `APP_ENV`, `PAYSTACK_SECRET_KEY`, `PAYSTACK_WEBHOOK_SECRET`, `GOOGLE_SHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GMAIL_SENDER`, `ADMIN_API_KEY`, `LOG_LEVEL` |
| 1.4 | Create `backend/main.py` | FastAPI app with lifespan, CORS middleware, router includes, exception handlers |
| 1.5 | Create health endpoint | `GET /health` in `backend/api/v1/health.py` |
| 1.6 | Create `.env.example` | Template with all env vars (no real secrets) |
| 1.7 | Add `.env` to `.gitignore` | Confirm already present |
| 1.8 | Add structured logging | `backend/utils/logging.py` — JSON-formatted logs with request ID, timestamp |
| 1.9 | Verify app starts | Run `uvicorn backend.main:app` and confirm health endpoint |

### Acceptance Criteria

- [ ] `GET /health` returns 200 with `{"status": "ok"}`
- [ ] Config loads from environment variables
- [ ] No secrets hard-coded in source
- [ ] Structured logs output to console

---

## Phase 2 — Google Integration

**Goal:** Backend can read/write Google Sheets and send emails via Gmail.

**Depends on:** Phase 1

**Milestone:** Can read program config from Sheets, read registrations, and send a test email.

### Tasks

| # | Task | Details |
|---|------|---------|
| 2.1 | Google auth service | `backend/services/google_auth.py` — service account credential loading, scoped to Sheets + Gmail + Drive |
| 2.2 | Sheets repository | `backend/repositories/google_sheets.py` — read/write abstraction. Methods: `read_sheet()`, `find_row()`, `update_row()`, `append_row()` |
| 2.3 | Program repository | `backend/repositories/programs.py` — `get_all_programs()`, `get_program(program_id)`, `get_cohorts(program_id)`, `get_cohort(cohort_id)`. Reads from Sheets "Programs" and "Cohorts" tabs |
| 2.4 | Registration repository | `backend/repositories/registrations.py` — `find_by_email()`, `find_by_id()`, `find_by_reference()`, `update_payment_status()`, `create_registration()`. Reads from "Registrations" tab |
| 2.5 | Payment repository | `backend/repositories/payments.py` — `create_payment()`, `update_payment()`, `find_by_reference()`, `get_payments()`. Reads from "Payments" tab |
| 2.6 | Fulfillment repository | `backend/repositories/fulfillments.py` — `create_fulfillment()`, `update_fulfillment()`, `find_by_registration()`. Reads from "Fulfillments" tab |
| 2.7 | Gmail service | `backend/services/gmail.py` — `send_email(to, subject, body)`, `send_html_email(to, subject, html_body)`. Uses Gmail API with service account |
| 2.8 | Google Sheets tab schema | Define expected Sheets structure: `Programs`, `Cohorts`, `Registrations`, `Payments`, `Fulfillments`, `EmailLogs`, `WebhookEvents`, `AuditLogs` tabs with column headers |
| 2.9 | Write Sheets schema doc | Document expected tab names and columns in a comment or README section |

### Acceptance Criteria

- [ ] Can authenticate to Google APIs with service account
- [ ] Can read program/cohort configuration from Sheets
- [ ] Can read/write registration records
- [ ] Can read/write payment records
- [ ] Can send an email via Gmail API
- [ ] Repository layer abstracts Sheets from business logic

---

## Phase 3 — Paystack Integration

**Goal:** Backend receives webhooks, validates signatures, and verifies transactions with Paystack.

**Depends on:** Phase 1

**Milestone:** `POST /webhooks/paystack` receives events, validates signature, verifies transaction via Paystack API.

### Tasks

| # | Task | Details |
|---|------|---------|
| 3.1 | Paystack client service | `backend/services/paystack.py` — `verify_transaction(reference)`, `initialize_transaction()`, `fetch_transaction()`. Uses `httpx` with Paystack base URL and secret key |
| 3.2 | Webhook endpoint | `POST /webhooks/paystack` in `backend/api/v1/webhooks.py`. Accepts raw body, extracts signature header |
| 3.3 | Signature verification | `backend/utils/security.py` — `verify_paystack_signature(payload, signature, secret)`. HMAC-SHA512 comparison |
| 3.4 | Webhook event logging | Log every received event to WebhookEvents tab: event_id, event_type, reference, received_at, payload hash |
| 3.5 | Event type filtering | Only process `charge.success` events initially. Log others but don't process |
| 3.6 | Transaction verification flow | After receiving reference → call Paystack verify API → check status, amount, currency, reference |
| 3.7 | Idempotency check | Before processing: check if transaction reference already exists in Payments tab |
| 3.8 | Raw payload handling | Store raw webhook payload securely. Never expose in API responses |

### Acceptance Criteria

- [ ] Webhook endpoint accepts POST requests
- [ ] Paystack signature is validated before processing
- [ ] Transaction is verified with Paystack API (not just webhook)
- [ ] Event type is checked (`charge.success`)
- [ ] Duplicate webhook events are rejected
- [ ] Raw payload is logged but not exposed

---

## Phase 4 — Payment Business Logic

**Goal:** Payments are matched to registrations, validated, and status is correctly updated.

**Depends on:** Phases 2, 3

**Milestone:** A verified payment correctly updates the registration's payment status to PAID, with amount/currency validation.

### Tasks

| # | Task | Details |
|---|------|---------|
| 4.1 | Registration matching | `backend/services/payment.py` — match payment to registration using: (1) metadata reference, (2) transaction reference, (3) email, (4) program/cohort + amount |
| 4.2 | Amount validation | Compare Paystack transaction amount against cohort's `expected_amount`. Both in same denomination (kobo for NGN) |
| 4.3 | Currency validation | Compare Paystack transaction currency against cohort's `expected_currency` |
| 4.4 | Payment status updates | State machine: `PENDING → PROCESSING → PAID` or `FAILED` or `MANUAL_REVIEW` |
| 4.5 | MANUAL_REVIEW handling | Set status to `MANUAL_REVIEW` if: amount mismatch, currency mismatch, registration not found, insufficient matching data. Do NOT auto-fulfill |
| 4.6 | Program/cohort resolution | From webhook data or email, resolve which program/cohort the payment belongs to |
| 4.7 | Audit logging | Record every payment state transition in AuditLogs tab |
| 4.8 | Payment service orchestration | `backend/services/payment.py` — full flow: receive reference → verify → validate → match → update status |

### Acceptance Criteria

- [ ] Correct registration is found for each payment
- [ ] Amount mismatch results in MANUAL_REVIEW
- [ ] Currency mismatch results in MANUAL_REVIEW
- [ ] Unknown registration results in MANUAL_REVIEW
- [ ] Payment status correctly transitions
- [ ] Audit log records all transitions
- [ ] No duplicate processing

---

## Phase 5 — Fulfillment

**Goal:** Paid participants receive confirmation email with correct WhatsApp group link.

**Depends on:** Phases 2, 4

**Milestone:** After verified payment, participant receives email with program-specific WhatsApp link. Fulfillment record is created.

### Tasks

| # | Task | Details |
|---|------|---------|
| 5.1 | Fulfillment service | `backend/services/fulfillment.py` — `fulfill_registration(registration_id, payment_id)` |
| 5.2 | Fulfillment state machine | `PENDING → PROCESSING → COMPLETED` or `FAILED` |
| 5.3 | Email template rendering | Load template from config, inject participant name, program name, cohort name, WhatsApp link |
| 5.4 | Email sending | Call Gmail service with rendered template. Record in EmailLogs tab |
| 5.5 | WhatsApp link from config | Retrieve `whatsapp_link` from cohort configuration — never hard-coded |
| 5.6 | Duplicate fulfillment prevention | Check Fulfillments tab before processing. Skip if already COMPLETED |
| 5.7 | Email failure isolation | If Gmail fails: payment stays PAID, fulfillment stays PENDING/FAILED. Never downgrade payment status |
| 5.8 | Fulfillment record creation | Create Fulfillment record with status, email_status, whatsapp_link_status |
| 5.9 | Resend capability | `resend_confirmation(registration_id)` — admin-triggered, bypasses duplicate check |
| 5.10 | Email log recording | Every email sent (or failed) is logged in EmailLogs tab |

### Acceptance Criteria

- [ ] Paid participant receives confirmation email
- [ ] Email contains correct program name and WhatsApp link
- [ ] Unpaid participant receives no access email
- [ ] Duplicate fulfillment is prevented
- [ ] Gmail failure does not change payment status
- [ ] Fulfillment record is created/updated
- [ ] Admin can trigger resend

---

## Phase 6 — Admin APIs

**Goal:** Full CRUD endpoints for programs, cohorts, registrations, payments. Admin verification and authentication.

**Depends on:** Phases 2, 4

**Milestone:** All `/api/v1/*` endpoints functional with authentication.

### Tasks

| # | Task | Details |
|---|------|---------|
| 6.1 | Program endpoints | CRUD: `GET/POST /programs`, `GET/PUT/DELETE /programs/{id}` |
| 6.2 | Cohort endpoints | CRUD: `GET/POST /cohorts`, `GET/PUT /cohorts/{id}` |
| 6.3 | Registration endpoints | `GET /registrations` (with filters: program_id, cohort_id, payment_status, email), `GET/POST/PUT /registrations/{id}` |
| 6.4 | Payment endpoints | `GET /payments`, `GET /payments/{id}`, `POST /payments/{reference}/verify` |
| 6.5 | Fulfillment endpoints | `POST /registrations/{id}/fulfill`, `POST /registrations/{id}/resend-confirmation` |
| 6.6 | Authentication middleware | API key or JWT validation on all `/api/v1/*` endpoints. `POST /webhooks/paystack` remains public |
| 6.7 | Role-based access | Super Admin, Program Admin (scoped to assigned programs), Viewer (read-only) |
| 6.8 | Standard error responses | `{"success": false, "error": {"code": "...", "message": "..."}}` format |
| 6.9 | Pagination | List endpoints return paginated results with metadata |
| 6.10 | Audit logging for admin actions | Log: `PROGRAM_CREATED`, `PROGRAM_UPDATED`, `PAYMENT_MANUALLY_VERIFIED`, `CONFIRMATION_RESENT`, etc. |

### Acceptance Criteria

- [ ] All CRUD endpoints respond correctly
- [ ] Authentication required on admin endpoints
- [ ] Public webhook endpoint does not require auth
- [ ] Standard error format on all endpoints
- [ ] List endpoints support pagination
- [ ] Admin actions are audit-logged
- [ ] API versioned under `/api/v1/`

---

## Phase 7 — Testing & Polish

**Goal:** All acceptance criteria from PRD §54 are met. Tests pass. Security reviewed.

**Depends on:** All prior phases

**Milestone:** Full test suite passes. No security gaps. Ready for MVP deployment.

### Tasks

| # | Task | Details |
|---|------|---------|
| 7.1 | Unit tests — validation | Amount validation, currency validation, registration matching, duplicate detection |
| 7.2 | Unit tests — state machines | Payment status transitions, fulfillment status transitions |
| 7.3 | Unit tests — email templates | Template rendering with data injection |
| 7.4 | Integration test — webhook flow | Mock Paystack: webhook → signature verify → transaction verify → payment update → email sent |
| 7.5 | Integration test — wrong amount | Mock Paystack: correct verify but wrong amount → MANUAL_REVIEW, no email |
| 7.6 | Integration test — unknown registration | Payment with no matching registration → MANUAL_REVIEW |
| 7.7 | Integration test — duplicate webhook | Same reference twice → second ignored, no duplicate email |
| 7.8 | Integration test — Gmail failure | Mock Gmail failure → payment stays PAID, fulfillment PENDING |
| 7.9 | Security audit | No secrets in code, no secrets in logs, no secrets in API responses, webhook signature validated |
| 7.10 | Error handling audit | All failure scenarios from PRD §45 are handled gracefully |
| 7.11 | Logging audit | Structured logs include request ID, reference, registration ID. No secrets logged |

### Acceptance Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass (with mocked external APIs)
- [ ] Scenario 1 (successful payment) works end-to-end
- [ ] Scenario 2 (failed payment) — no access granted
- [ ] Scenario 3 (wrong amount) — MANUAL_REVIEW
- [ ] Scenario 4 (unknown registration) — MANUAL_REVIEW
- [ ] Scenario 5 (duplicate webhook) — no duplicate fulfillment
- [ ] Scenario 6 (Gmail failure) — payment not downgraded
- [ ] Secrets never appear in code, logs, or API responses

---

## Dependency Graph

```
Phase 1 (Foundation)
    ├──→ Phase 2 (Google Integration)
    └──→ Phase 3 (Paystack Integration)
              │
              ├──→ Phase 4 (Payment Business Logic)  ← requires Phase 2
              │         │
              │         └──→ Phase 5 (Fulfillment)  ← requires Phase 2
              │
              └──→ Phase 6 (Admin APIs)  ← requires Phase 2
                        │
                        └──→ Phase 7 (Testing)  ← requires all
```

**Parallelizable:** Phases 2 and 3 can run in parallel after Phase 1.
**Critical Path:** Phase 1 → Phase 2 → Phase 4 → Phase 5 → Phase 7

---

## Google Sheets Tab Structure

| Tab Name | Key Columns |
|----------|-------------|
| Programs | program_id, program_name, description, status, currency, created_at, updated_at |
| Cohorts | cohort_id, program_id, cohort_name, start_date, end_date, registration_deadline, capacity, status, paystack_page, expected_amount, currency, whatsapp_link, email_template, payment_deadline |
| Registrations | registration_id, full_name, email, phone, program_id, cohort_id, registration_status, payment_status, payment_reference, payment_date, fulfillment_status, created_at, updated_at |
| Payments | payment_id, registration_id, program_id, cohort_id, transaction_reference, amount, currency, status, gateway, paid_at, verified_at, created_at, updated_at |
| Fulfillments | fulfillment_id, registration_id, payment_id, email_status, whatsapp_link_status, status, fulfilled_at, error_message |
| EmailLogs | email_id, registration_id, email_type, recipient, subject, status, sent_at, error_message |
| WebhookEvents | event_id, event_type, transaction_reference, received_at, processed_at, status, error_message |
| AuditLogs | log_id, admin_id, action, target_id, details, created_at |

---

## Environment Variables

```bash
APP_ENV=development
LOG_LEVEL=INFO

PAYSTACK_SECRET_KEY=
PAYSTACK_WEBHOOK_SECRET=

GOOGLE_SHEET_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=
GMAIL_SENDER=

ADMIN_API_KEY=

# Future
DATABASE_URL=
JWT_SECRET=
```

---

## Key Design Decisions

1. **Repository pattern** — All Google Sheets access goes through repositories. Business logic never touches Sheets directly. This enables future PostgreSQL migration by swapping repositories only.

2. **No program-specific logic** — Programs and cohorts are configuration data. Adding a new program = adding rows to Sheets, not code changes.

3. **Fail-safe fulfillment** — Email/Gmail failure never downgrades a successful payment. Payment status is independent of fulfillment status.

4. **Manual review over auto-reject** — Uncertain payments go to MANUAL_REVIEW, not FAILED. Humans decide edge cases.

5. **Webhook ≠ payment proof** — Webhooks trigger verification. The Paystack API call is the source of truth.

6. **Idempotency everywhere** — Duplicate webhooks, duplicate emails, duplicate fulfillments are all prevented.
