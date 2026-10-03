# NxtWave Growth Intern Challenge – Growth Measurement Backend

A production-ready, demo-focused, and PostgreSQL-compatible REST API built with Python 3.11+, FastAPI, SQLAlchemy, SQLite, Pydantic, and Pytest.

This backend serves as the measurement, attribution, and growth tracking layer for NxtWave's 7-day Growth Challenge targeting 500 final-year engineering student workshop registrations for **"Build Your First AI Project in 60 Minutes"**.

---

## 🚀 Key Responsibilities

1. **Registration Management**: Captures registrants, normalizes email addresses, prevents duplicate signups, and assigns unique referral codes.
2. **Referral Attribution**: Generates unique `AI60-XXXX` codes for users and tracks incoming referrals via `referred_by` attribution without exposing private user data.
3. **Analytics Event Tracking**: Tracks user journey events (`page_view`, `hero_cta_click`, `registration_started`, `registration_completed`, `whatsapp_share`, etc.) with session IDs and custom metadata.
4. **UTM Attribution**: Full support for `source`, `medium`, `campaign`, and `content`.
5. **Growth Metrics & Conversion Tracking**: Real-time aggregation of conversion rate, referral share rate, and referral registration rate.
6. **Abuse Protection**: Simple in-memory rate limiting to protect public endpoints.

---

## 🏗️ Architecture & Technical Decisions

- **FastAPI Framework**: High performance, native OpenAPI (Swagger) documentation, and Pydantic validation.
- **SQLAlchemy ORM**: Database abstractions using standard SQL types for seamless portability. Swap SQLite with PostgreSQL simply by changing `DATABASE_URL`.
- **Decoupled Architecture**: Standard layer separation:
  - `api/`: Endpoint route handlers and HTTP responses.
  - `schemas/`: Pydantic validation models.
  - `services/`: Encapsulated domain business logic.
  - `db/`: Database configuration, session management, and models.
  - `core/`: Configuration and middleware rate limiting.
- **Testing Reliability**: `conftest.py` uses SQLAlchemy `StaticPool` with a shared in-memory SQLite database (`sqlite:///:memory:`) so all test requests run deterministically.

---

## 📁 Project Structure

```
/backend
├── app/
│   ├── main.py                   # Application entrypoint & CORS middleware
│   ├── api/                      # REST API Routers
│   │   ├── registrations.py      # POST /api/v1/registrations
│   │   ├── referrals.py          # GET /api/v1/referrals/{referral_code}
│   │   ├── analytics.py          # POST /api/v1/events
│   │   ├── metrics.py            # GET /api/v1/metrics/summary
│   │   └── health.py             # GET /api/v1/health
│   ├── models/                   # Model exports
│   │   ├── registration.py
│   │   ├── referral.py
│   │   └── analytics_event.py
│   ├── schemas/                  # Pydantic Schemas
│   │   ├── registration.py
│   │   ├── referral.py
│   │   ├── analytics.py
│   │   └── metrics.py
│   ├── services/                 # Business Logic Services
│   │   ├── registration_service.py
│   │   ├── referral_service.py
│   │   ├── analytics_service.py
│   │   └── metrics_service.py
│   ├── db/                       # Database Setup & Models
│   │   ├── database.py
│   │   └── models.py
│   └── core/                     # App Configuration & Security
│       ├── config.py
│       └── rate_limiter.py
├── tests/                        # Automated Pytest Suite
│   ├── conftest.py
│   ├── test_registration.py
│   ├── test_referral.py
│   ├── test_analytics.py
│   ├── test_metrics.py
│   └── test_health.py
├── .env.example                  # Environment template
├── .env                          # Active environment config
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- `pip`

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Contents of `.env`:
```env
APP_ENV=development
DATABASE_URL=sqlite:///./nxtwave_growth.db
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
```

---

## 🏃 Running the Server

Start the application with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

- **Base URL**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

## 🧪 Running Automated Tests

Run the complete pytest suite:
```bash
python -m pytest -v
```

---

## 🔌 API Endpoints & Usage

### 1. Health Check
`GET /api/v1/health`

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. User Registration
`POST /api/v1/registrations`

**Request Payload:**
```json
{
  "full_name": "Rahul Sharma",
  "email": "rahul.sharma@example.com",
  "phone": "+91 9876543210",
  "college_name": "IIT Hyderabad",
  "branch": "Computer Science",
  "graduation_year": 2026,
  "source": "whatsapp",
  "medium": "community",
  "campaign": "ai60",
  "content": "college-group",
  "referral_code": "AI60-KR12"
}
```

*Note: `referral_code` in the request body is the incoming referrer's code (`referred_by`).*

**Response (201 Created):**
```json
{
  "success": true,
  "registration_id": "1",
  "referral_code": "AI60-XP44",
  "message": "Registration successful"
}
```

---

### 3. Referral Statistics Lookup
`GET /api/v1/referrals/{referral_code}`

**Example:** `GET /api/v1/referrals/AI60-KR12`

**Response (200 OK):**
```json
{
  "referral_code": "AI60-KR12",
  "total_referred_registrations": 5
}
```

---

### 4. Track Analytics Event
`POST /api/v1/events`

**Request Payload:**
```json
{
  "event_name": "registration_started",
  "session_id": "sess_98765",
  "anonymous_id": "anon_12345",
  "source": "whatsapp",
  "medium": "community",
  "campaign": "ai60",
  "content": "college-group",
  "referral_code": "AI60-KR12",
  "metadata": {
    "page": "landing_page"
  }
}
```

**Supported Events:** `page_view`, `hero_cta_click`, `project_preview_click`, `registration_started`, `registration_completed`, `whatsapp_share`, `referral_copied`, `faq_opened`.

**Response (201 Created):**
```json
{
  "success": true,
  "event_id": "1",
  "message": "Event recorded successfully"
}
```

---

### 5. Growth Metrics Summary
`GET /api/v1/metrics/summary`

**Response (200 OK):**
```json
{
  "total_registrations": 120,
  "registrations_today": 35,
  "registrations_by_source": {
    "whatsapp": 80,
    "instagram": 40
  },
  "registrations_by_medium": {
    "community": 80,
    "social": 40
  },
  "registrations_by_campaign": {
    "ai60": 120
  },
  "registrations_by_college": {
    "IIT Hyderabad": 50,
    "BITS Pilani": 70
  },
  "registrations_by_branch": {
    "Computer Science": 90,
    "ECE": 30
  },
  "total_referral_registrations": 45,
  "top_referral_codes": [
    {
      "referral_code": "AI60-KR12",
      "count": 12
    }
  ],
  "cta_events": 200,
  "registration_started": 150,
  "registration_completed": 120,
  "whatsapp_share_events": 60,
  "registration_conversion_rate": 80.0,
  "referral_share_rate": 50.0,
  "referral_registration_rate": 37.5
}
```

---

## 📈 Metric Formulas

1. **Registration Conversion Rate**:
   $$\text{registration\_conversion\_rate} = \frac{\text{registration\_completed}}{\text{registration\_started}} \times 100$$

2. **Referral Share Rate**:
   $$\text{referral\_share\_rate} = \frac{\text{whatsapp\_share}}{\text{registration\_completed}} \times 100$$

3. **Referral Registration Rate**:
   $$\text{referral\_registration\_rate} = \frac{\text{registrations\_with\_referred\_by}}{\text{total\_registrations}} \times 100$$

*(When denominator is 0, each formula safely returns `0.0%`).*

---

## 💻 Frontend Integration Guide (Lovable / React)

### Tracking Referral Parameter & Registration Example
```typescript
// Detect referral code from URL query params (e.g. ?ref=AI60-KR12)
const urlParams = new URLSearchParams(window.location.search);
const referrerCode = urlParams.get('ref') || '';

// Call Registration API
async function handleRegistration(formData) {
  const payload = {
    ...formData,
    source: 'whatsapp',
    medium: 'community',
    campaign: 'ai60',
    referral_code: referrerCode // Passed as incoming referral code
  };

  const response = await fetch('http://localhost:8000/api/v1/registrations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (response.ok) {
    console.log("Your new referral code is:", data.referral_code);
    // e.g. Share link: https://landingpage.com?ref=${data.referral_code}
  } else {
    alert(data.detail);
  }
}
```

---

## 🐘 Replacing SQLite with PostgreSQL in Production

To switch to PostgreSQL in production:

1. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```
2. Update `.env` or set environment variable:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/nxtwave_growth
   ```
3. Restart the backend service. SQLAlchemy will automatically create tables and manage connections via PostgreSQL with **zero changes to business logic or API endpoints**.
