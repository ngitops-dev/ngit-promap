# NGiT Streamlit Admin Portal — Execution Plan

**Project:** NGiT Program Registration, Payment & Access Platform
**Focus:** Streamlit Admin Portal (consumes FastAPI REST APIs)
**Status:** Not Started
**Created:** 2026-08-15

---

## Architecture Overview

```
Admin Login (streamlit-authenticator)
        │
        ▼
Streamlit Admin Portal
        │
        ▼
  API Client (HTTPX)
        │
        ├──→ FastAPI Backend → Paystack
        │                → Google Sheets
        │                → Gmail
        │
        └──→ Mock API (during development)
```

**Tech Stack:** Python 3.11+, Streamlit, streamlit-authenticator, Plotly/Altair, HTTPX, Pandas

**Core Principle:** Streamlit is the view layer only. No payment logic, no Paystack calls, no Sheets access. All data flows through FastAPI.

---

## Phase 1 — Streamlit Foundation & Login

**Goal:** App boots, login screen works, basic layout with sidebar navigation.

**Depends on:** Nothing (can run in parallel with backend Phase 1)

**Milestone:** Admin can log in and see the navigation sidebar.

### Tasks

| # | Task | Details |
|---|------|---------|
| 1.1 | Create project structure | `streamlit_app/`, `streamlit_app/pages/`, `streamlit_app/services/`, `streamlit_app/components/`, `streamlit_app/utils/` |
| 1.2 | Create `config.py` | Load: `FASTAPI_BASE_URL`, `APP_ENV`, `LOG_LEVEL` from `.streamlit/secrets.toml` or env |
| 1.3 | Create `app.py` | Main Streamlit entry point. Page config (title, icon, layout), auth check, sidebar navigation |
| 1.4 | Login screen | `streamlit-authenticator` with email/password. Credentials managed via FastAPI admin APIs (hashed passwords stored in Google Sheets "Admins" tab) |
| 1.5 | Auth utility | `utils/auth.py` — `check_auth()`, `get_current_user()`, `require_role(role)`. Store auth state in `st.session_state` |
| 1.6 | Sidebar navigation | Role-based menu: Dashboard, Programs, Cohorts, Registrations, Payments, Pending Payments, Communications, Reports, Settings, Activity Logs |
| 1.7 | Role-based page access | Super Admin sees all. Program Admin sees scoped pages. Viewer sees read-only pages |
| 1.8 | Session management | Handle logout, session timeout, re-authentication on expired sessions |
| 1.9 | Page routing | Multi-page app using Streamlit's native page system or manual routing via `st.session_state` |
| 1.10 | Create `.streamlit/secrets.toml.example` | Template for local development secrets |

### Acceptance Criteria

- [ ] Login screen displays with email/password fields
- [ ] Invalid credentials show error message
- [ ] Successful login shows sidebar navigation
- [ ] Sidebar items respect user roles
- [ ] Logout clears session
- [ ] Unauthenticated users cannot access any page

---

## Phase 2 — API Client & Mock Layer

**Goal:** Streamlit can call FastAPI endpoints. Mock responses available for parallel development.

**Depends on:** Phase 1

**Milestone:** API client returns mock data that renders in pages. Swap to real FastAPI by changing one config value.

### Tasks

| # | Task | Details |
|---|------|---------|
| 2.1 | API client service | `services/api_client.py` — HTTPX-based client. Methods: `get_programs()`, `get_cohorts()`, `get_registrations()`, `get_payments()`, `verify_payment()`, `resend_confirmation()`, `create_program()`, `update_program()`, `create_cohort()`, `update_cohort()`, `get_reports()`, `get_email_logs()`, `get_activity_logs()`, `get_system_health()` |
| 2.2 | Mock API service | `services/mock_api.py` — returns realistic fake data for all endpoints. Used when `APP_ENV=development` |
| 2.3 | API client factory | `services/__init__.py` — returns mock or real client based on `config.APP_ENV` |
| 2.4 | Auth token handling | API client attaches JWT/API key to every request (received from FastAPI login endpoint) |
| 2.5 | Error handling | API client catches connection errors, 4xx, 5xx. Returns structured error to pages |
| 2.6 | Response models | `services/models.py` — Pydantic models for API responses: `Program`, `Cohort`, `Registration`, `Payment`, `Fulfillment`, `EmailLog`, `ActivityLog` |
| 2.7 | Caching layer | Use `@st.cache_data` with TTL for read-heavy endpoints (programs, cohorts). Invalidate on write operations |
| 2.8 | Swap mechanism | Change `APP_ENV=production` to switch from mock to real FastAPI. No code changes needed |

### Acceptance Criteria

- [ ] API client can call all FastAPI endpoints
- [ ] Mock mode returns realistic data
- [ ] Swapping mock/real requires only config change
- [ ] Auth token is attached to all requests
- [ ] Connection errors display user-friendly messages
- [ ] Read-heavy data is cached appropriately

---

## Phase 3 — Dashboard

**Goal:** Main dashboard with KPI cards, charts, filters, and recent activity.

**Depends on:** Phase 2

**Milestone:** Dashboard loads with KPIs, date/program filters, charts, and recent activity feed.

### Tasks

| # | Task | Details |
|---|------|---------|
| 3.1 | Dashboard page | `pages/dashboard.py` — main landing page |
| 3.2 | KPI cards | `components/metrics.py` — render 4 primary cards: Total Registrations, Paid, Pending, Revenue. Use `st.metric` with delta indicators |
| 3.3 | Secondary KPIs | Row 2: Active Programs, Active Cohorts, Failed Payments, Manual Reviews, Payment Conversion Rate |
| 3.4 | Global filters | Date range (Today, Last 7 days, Last 30 days, This month, Custom), Program dropdown, Cohort dropdown (dynamic based on program) |
| 3.5 | Registration trend chart | Line chart using Plotly/Altair — registrations over time, filtered by date range and program |
| 3.6 | Payment trend chart | Stacked/grouped bar chart — Paid, Pending, Failed payments over time |
| 3.7 | Revenue by program chart | Horizontal bar chart — revenue per program |
| 3.8 | Recent activity feed | Last 10-15 events: payments received, registrations, emails sent, manual reviews. Color-coded icons |
| 3.9 | Notification alerts | `st.warning`/`st.success` banners: "X payments require manual review", "Y confirmations failed", "Z payments processed today" |
| 3.10 | Data refresh | "Last updated: [timestamp]" with manual refresh button. Clear cache and refetch |
| 3.11 | Empty states | When no data: show helpful message instead of blank charts |
| 3.12 | Loading states | `st.spinner` for all data fetches: "Loading dashboard..." |

### Acceptance Criteria

- [ ] 4 primary KPI cards display with correct values
- [ ] Secondary KPIs display
- [ ] Date filter updates all charts and KPIs
- [ ] Program filter narrows data to selected program
- [ ] Cohort filter updates dynamically based on program
- [ ] Registration trend chart renders
- [ ] Payment trend chart renders
- [ ] Revenue by program chart renders
- [ ] Recent activity feed shows latest events
- [ ] Notification alerts display for urgent items
- [ ] Refresh button works
- [ ] Empty states display when no data

---

## Phase 4 — Program & Cohort Management

**Goal:** Full CRUD for programs and cohorts. Cohort configuration with payment, email, WhatsApp settings.

**Depends on:** Phase 2

**Milestone:** Admin can create, edit, activate/deactivate programs and cohorts. Cohort activation validates required config.

### Tasks

| # | Task | Details |
|---|------|---------|
| 4.1 | Programs list page | `pages/programs.py` — table with search, status indicator, cohort count, actions |
| 4.2 | Create program form | Program name, description, currency (dropdown), status (Active/Inactive). Calls `POST /api/v1/programs` |
| 4.3 | Program details page | Tabbed view: Overview, Cohorts, Registrations, Payments, Reports. Summary stats at top |
| 4.4 | Edit program | Edit name, description, status. Calls `PUT /api/v1/programs/{id}` |
| 4.5 | Activate/deactivate program | Toggle with confirmation dialog. Programs with active cohorts warn before deactivation |
| 4.6 | Cohorts list page | `pages/cohorts.py` — table with program name, cohort name, status, start date, actions |
| 4.7 | Create cohort form | Program (dropdown), cohort name, dates, capacity, payment page, amount, currency, WhatsApp link, email template, status |
| 4.8 | Cohort activation validation | Before activating: check all required fields (payment page, amount, currency, email template, WhatsApp link, dates). Show checklist with ✅/❌ |
| 4.9 | Edit cohort | Edit all cohort configuration fields. Calls `PUT /api/v1/cohorts/{id}` |
| 4.10 | WhatsApp link security | WhatsApp links only visible to authorized admins. Masked in list views. Never shown in public contexts |
| 4.11 | Confirmation dialogs | All destructive actions (deactivate, delete) require confirmation |
| 4.12 | Success/error messages | After operations: "✓ Program created successfully" or "✗ Unable to create program" |

### Acceptance Criteria

- [ ] Programs list loads with search and filtering
- [ ] Admin can create a program with all required fields
- [ ] Admin can edit program details
- [ ] Admin can activate/deactivate programs
- [ ] Program details show cohort list and stats
- [ ] Cohorts list loads with program context
- [ ] Admin can create a cohort with all configuration
- [ ] Cohort activation validates required fields
- [ ] Admin can edit cohort configuration
- [ ] WhatsApp links are only visible to authorized admins
- [ ] Confirmation dialogs appear for destructive actions
- [ ] Success/error messages display after operations

---

## Phase 5 — Registration & Payment Management

**Goal:** Search, filter, view details for registrations and payments. Manual payment verification. Pending payments view.

**Depends on:** Phase 2

**Milestone:** Admin can search/filter registrations, view participant details with timeline, verify payments manually, and manage pending payments.

### Tasks

| # | Task | Details |
|---|------|---------|
| 5.1 | Registrations list page | `pages/registrations.py` — table with search (name/email/ID), filters (program, cohort, payment status, date) |
| 5.2 | Registration detail page | Participant profile: name, email, phone, program, cohort, registration date, payment status, amount, transaction ref, confirmation status, fulfillment status |
| 5.3 | Participant timeline | Chronological event list: registration submitted → payment email sent → payment received → payment verified → confirmation sent → WhatsApp access. Each event with timestamp |
| 5.4 | Participant actions | Buttons: Verify Payment, Resend Confirmation, View Payment, View Activity. Role-gated |
| 5.5 | Payments list page | `pages/payments.py` — table with search (reference), filters (status, program, cohort). Status indicators (🟢🟡🔴🟠⚪) |
| 5.6 | Payment detail page | Full payment info: reference, participant, program, cohort, amount, currency, status, gateway, paid date, verified date |
| 5.7 | Manual payment verification | Button → confirmation dialog → calls `POST /api/v1/payments/{reference}/verify` → shows result. "Verifying payment with Paystack..." loading state |
| 5.8 | Pending payments page | `pages/pending_payments.py` — registrations without completed payment. Summary table: program, total registrations, pending count, conversion rate |
| 5.9 | Pending payment actions | View participant, view registration, resend payment email, copy payment page link. Filter by age of registration |
| 5.10 | Resend confirmation | Button → confirmation dialog → calls `POST /api/v1/registrations/{id}/resend-confirmation` |
| 5.11 | Status indicators | Consistent across all pages: 🟢 PAID, 🟡 PENDING, 🔴 FAILED, 🟠 REVIEW, ⚪ REFUNDED |
| 5.12 | Empty states | "No pending payments — all participants have completed payment" / "No registrations found" |

### Acceptance Criteria

- [ ] Registrations list loads with search and all filters
- [ ] Registration detail shows complete participant profile
- [ ] Participant timeline displays chronological events
- [ ] Authorized admins see action buttons
- [ ] Payments list loads with search and filters
- [ ] Payment detail shows complete payment info
- [ ] Manual verification triggers confirmation, calls API, shows result
- [ ] Pending payments page shows correct counts and conversion rates
- [ ] Resend confirmation works with confirmation dialog
- [ ] Status indicators are consistent everywhere
- [ ] Empty states display when no data

---

## Phase 6 — Communications & Reports

**Goal:** Email activity logs. Business reports with export capability.

**Depends on:** Phase 2

**Milestone:** Admin can view email logs, generate program/cohort/revenue reports, export to CSV/Excel.

### Tasks

| # | Task | Details |
|---|------|---------|
| 6.1 | Communications page | `pages/communications.py` — email log table with filters (type, status, program, date) |
| 6.2 | Email detail | Recipient, type, subject, status, sent date. No credentials or infrastructure details exposed |
| 6.3 | Reports page | `pages/reports.py` — tabbed: Program Performance, Cohort Performance, Revenue, Payment Conversion |
| 6.4 | Program performance report | Table: program, registrations, paid, pending, failed, revenue, conversion rate |
| 6.5 | Cohort performance report | Metrics: registrations, paid, pending, failed, revenue, conversion rate, average payment value |
| 6.6 | Revenue report | Filterable by program, cohort, date, payment status. Display: total revenue, this month, today |
| 6.7 | Payment conversion report | Formula: (paid / total) × 100. Display as percentage with trend |
| 6.8 | Export — CSV | `components/exports.py` — download button for CSV export. Respects current filters and user permissions |
| 6.9 | Export — Excel | Multi-sheet Excel export for complex reports |
| 6.10 | Report charts | Plotly/Altair charts for visual report presentation |
| 6.11 | Date range filters | All reports support date range filtering |
| 6.12 | Permission-scoped exports | Program Admin only exports their assigned programs. Viewer cannot export |

### Acceptance Criteria

- [ ] Communications page loads email logs with filters
- [ ] Email detail shows relevant info without exposing infrastructure
- [ ] Program performance report displays correct metrics
- [ ] Cohort performance report displays correct metrics
- [ ] Revenue report filters work correctly
- [ ] Payment conversion calculation is accurate
- [ ] CSV export downloads correctly
- [ ] Excel export downloads correctly
- [ ] Exports respect current filters
- [ ] Exports respect user permissions

---

## Phase 7 — Settings, Activity Logs & Polish

**Goal:** Settings page, integration health, activity logs, error handling, confirmation dialogs, loading/empty states across all pages.

**Depends on:** All prior phases

**Milestone:** Complete admin portal with settings, health monitoring, activity logs, and polished UX across all pages.

### Tasks

| # | Task | Details |
|---|------|---------|
| 7.1 | Settings page | `pages/settings.py` — tabs: General, Email, Payment, Google, Security |
| 7.2 | General settings | Organization name, default currency, timezone |
| 7.3 | Email settings | Sender name, sender email, email templates list |
| 7.4 | Payment settings | Paystack connection status, configuration status. Masked secret keys |
| 7.5 | Google settings | Google integration status, Sheets connection |
| 7.6 | Security settings | Admin user management (list, create, edit, deactivate). Roles: Super Admin, Program Admin, Viewer. Assigned programs for Program Admin |
| 7.7 | Admin user management | Create admin: name, email, role, assigned programs (if Program Admin), password. Calls FastAPI admin APIs |
| 7.8 | Integration health | `components/health.py` — status cards: FastAPI 🟢/🔴, Google Sheets 🟢/🔴, Gmail 🟢/🔴, Paystack 🟢/🔴. Calls health check endpoints |
| 7.9 | Activity logs page | `pages/activity_logs.py` — table with timestamp, user, action, target, details. Filters: user, action, date, program |
| 7.10 | Global error handling | Catch all API errors, display `st.error` with user-friendly message. Never show stack traces |
| 7.11 | Global loading states | `st.spinner` or `st.progress` for all async operations |
| 7.12 | Global empty states | Every page has meaningful empty state message |
| 7.13 | Global confirmation dialogs | All destructive/irreversible actions require confirmation |
| 7.14 | Success/error toasts | Consistent message format: "✓ [action] successful" / "✗ Unable to [action]" |
| 7.15 | UI consistency pass | Consistent spacing, card styles, status colors, typography across all pages |
| 7.16 | Responsive tweaks | Optimize for desktop. Reasonable on laptop/tablet |
| 7.17 | Performance pass | Cache all read-heavy data. Avoid redundant API calls. Lazy load heavy pages |

### Acceptance Criteria

- [ ] Settings page loads all configuration sections
- [ ] Admin can manage admin users (CRUD) with role assignment
- [ ] Integration health shows real-time status of all services
- [ ] Activity logs display with filters
- [ ] All pages have consistent error handling
- [ ] All pages have loading states
- [ ] All pages have empty states
- [ ] All destructive actions require confirmation
- [ ] Success/error messages display consistently
- [ ] UI is visually consistent across all pages
- [ ] No stack traces shown to users
- [ ] Caching reduces redundant API calls

---

## Dependency Graph

```
Phase 1 (Foundation + Login)
    │
    └──→ Phase 2 (API Client & Mocks)
              │
              ├──→ Phase 3 (Dashboard)
              ├──→ Phase 4 (Programs & Cohorts)
              ├──→ Phase 5 (Registrations & Payments)
              ├──→ Phase 6 (Communications & Reports)
              │
              └──→ Phase 7 (Settings, Logs & Polish)  ← requires all
```

**Parallelizable:** Phases 3-6 can run in parallel after Phase 2.
**Critical Path:** Phase 1 → Phase 2 → Phase 3-6 → Phase 7

---

## Streamlit Project Structure

```
streamlit_app/
│
├── app.py                          # Entry point, auth, page routing
│
├── config.py                       # Configuration from secrets/env
│
├── pages/
│   ├── dashboard.py                # KPIs, charts, filters, activity
│   ├── programs.py                 # Program list + create/edit
│   ├── cohorts.py                  # Cohort list + create/edit
│   ├── registrations.py            # Registration list + detail + timeline
│   ├── payments.py                 # Payment list + detail + verify
│   ├── pending_payments.py         # Pending payments + conversion
│   ├── communications.py           # Email logs
│   ├── reports.py                  # Program, cohort, revenue reports
│   ├── settings.py                 # System configuration + admin mgmt
│   └── activity_logs.py            # Audit trail
│
├── services/
│   ├── __init__.py                 # API client factory (mock vs real)
│   ├── api_client.py               # Real FastAPI HTTPX client
│   ├── mock_api.py                 # Mock responses for development
│   └── models.py                   # Pydantic response models
│
├── components/
│   ├── metrics.py                  # KPI card components
│   ├── tables.py                   # Reusable table components
│   ├── filters.py                  # Filter bar components
│   ├── forms.py                    # Reusable form components
│   ├── status.py                   # Status badge/indicator components
│   ├── charts.py                   # Chart components (Plotly/Altair)
│   ├── exports.py                  # CSV/Excel export components
│   └── health.py                   # Integration health cards
│
├── utils/
│   ├── auth.py                     # Authentication helpers
│   └── formatting.py               # Currency, date, number formatting
│
└── .streamlit/
    └── secrets.toml.example        # Template for local secrets
```

---

## Streamlit Secrets Template

```toml
# .streamlit/secrets.toml

[app]
ENV = "development"  # development | production
FASTAPI_BASE_URL = "http://localhost:8000"

[auth]
# streamlit-authenticator config
# Credentials managed via FastAPI admin APIs in production
```

---

## Mock Data Structure

The mock API should return realistic data matching FastAPI response schemas:

| Entity | Mock Records | Fields |
|--------|-------------|--------|
| Programs | 4-6 | program_id, name, description, status, currency |
| Cohorts | 8-10 | cohort_id, program_id, name, dates, amount, status |
| Registrations | 50-100 | registration_id, name, email, phone, program, cohort, status |
| Payments | 40-80 | payment_id, reference, amount, status, gateway, dates |
| Fulfillments | 30-60 | fulfillment_id, email_status, whatsapp_status, status |
| Email Logs | 50-100 | email_id, type, recipient, subject, status, sent_at |
| Activity Logs | 30-50 | log_id, user, action, target, timestamp |

---

## Key Design Decisions

1. **streamlit-authenticator for login** — Handles password hashing, login UI, session management. Credentials managed through FastAPI admin APIs, stored in Google Sheets "Admins" tab.

2. **Mock-first development** — Streamlit pages can be built and tested before FastAPI is complete. Single config switch to go live.

3. **No business logic in Streamlit** — Streamlit calls FastAPI. FastAPI calls Paystack/Sheets/Gmail. Streamlit never touches external services directly.

4. **Role-based UI** — Navigation and actions are filtered by user role. Super Admin sees everything. Program Admin sees scoped data. Viewer sees read-only.

5. **Consistent status indicators** — 🟢 PAID, 🟡 PENDING, 🔴 FAILED, 🟠 REVIEW, ⚪ REFUNDED used everywhere without exception.

6. **Caching for performance** — Read-heavy API calls cached with `@st.cache_data`. Cache invalidated on write operations.

7. **Confirmation for dangerous actions** — Manual payment verification, resend email, deactivate program, delete configuration all require explicit confirmation.

8. **WhatsApp link security** — Links masked in lists, only visible in detail views for authorized admins, never exposed in exports or public contexts.
