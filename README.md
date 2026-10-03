# NxtWave Growth Challenge – Full Stack Production Deployment Guide

A high-performance, measurement-focused, and demo-ready application designed for NxtWave's Growth Challenge.

---

## 🏗️ Architecture & Deployment Flow

```
[ Public Frontend ]  (e.g., Vercel / Netlify / Render Static)
  URL: https://your-frontend-app.vercel.app
        │
        ▼ (HTTPS REST API Requests)
[ Public Backend API ] (e.g., Render / Railway / Fly.io / Docker)
  URL: https://your-backend-api.onrender.com/api/v1
        │
        ▼ (SQLAlchemy ORM)
[ Database ] (SQLite locally / PostgreSQL in production)
```

---

## 🛠️ Environment Variables Configuration

### 1. Frontend Environment (`Frontend/.env`)

| Variable | Development Value | Production Example | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | `https://your-backend-api.onrender.com/api/v1` | Base URL for FastAPI backend endpoints |
| `VITE_USE_MOCK_API` | `false` | `false` | Set to `true` only for offline UI demo testing |

> [!NOTE]
> Referral URLs and WhatsApp sharing links dynamically resolve using `window.location.origin` (or `VITE_PUBLIC_FRONTEND_URL`), automatically outputting `https://your-frontend-app.vercel.app/?ref=AI60-XXXX` in production without hardcoding `localhost`.

### 2. Backend Environment (`Backend/.env`)

| Variable | Development Value | Production Example | Description |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | `development` | `production` | Application environment state |
| `DATABASE_URL` | `sqlite:///./nxtwave_growth.db` | `postgresql://user:pass@host:5432/dbname` | Database connection string |
| `FRONTEND_URL` | `http://localhost:5173` | `https://your-frontend-app.vercel.app` | Primary frontend origin |
| `CORS_ORIGINS` | `http://localhost:5173` | `http://localhost:5173,https://your-frontend-app.vercel.app` | Comma-separated allowed CORS origins |

---

## ⚠️ Database Persistence & PostgreSQL Migration Note

- **Local Development**: Uses SQLite (`nxtwave_growth.db`).
- **Production Warning**: Cloud platforms like Render, Heroku, or Vercel use ephemeral file systems. If deployed with SQLite on an ephemeral filesystem, database records will reset on server restarts.
- **Production Recommendation**: Provide a managed PostgreSQL database URL in production:
  ```env
  DATABASE_URL=postgresql://username:password@postgres-host.railway.app:5432/nxtwave_growth
  ```
  *SQLAlchemy ORM will handle tables and connection pooling automatically with zero code changes.*

---

## 🚀 Local Development Commands

### 1. Run Backend API
```powershell
cd Backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- API Base URL: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`

### 2. Run Frontend Web App
```powershell
cd Frontend
npm install
npm run dev
```
- Local URL: `http://localhost:5173`

---

## ☁️ Public Deployment Instructions

### Deploying Frontend to Vercel / Netlify
1. Connect repository branch to Vercel / Netlify.
2. Set Build Command: `npm run build`
3. Set Output Directory: `dist`
4. Environment Variable:
   - `VITE_API_BASE_URL` = `https://your-backend-api.onrender.com/api/v1`

### Deploying Backend to Render / Railway
1. Create a Web Service on Render / Railway pointing to `/Backend`.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Set Environment Variables:
   - `APP_ENV` = `production`
   - `FRONTEND_URL` = `https://your-frontend-app.vercel.app`
   - `CORS_ORIGINS` = `https://your-frontend-app.vercel.app`
   - `DATABASE_URL` = `postgresql://user:pass@host:5432/dbname` (or persistent disk SQLite)
