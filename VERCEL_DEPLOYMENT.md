# 🚀 Vercel Deployment & Serverless Integration Guide

## Executive Summary
This document provides complete instructions for deploying the **Vendor Data Quality & Executive Command Center Platform** to Vercel Serverless Functions.

---

## 📁 Vercel Project Architecture

```
vendor_project/
├── api/
│   └── index.py            # Primary Vercel Serverless Entry Point (WSGI Export)
├── vercel.json             # Vercel Builder (@vercel/python) & Route Mapping Config
├── app.py                  # Primary Local Entry Point & Flask App Instance
├── requirements.txt        # Verified Production Dependencies (13 Packages)
├── instance/
│   └── vendors.db          # Authoritative 500 Enterprise Vendor SQLite Database
├── src/                    # DDD Domain Services, Infrastructure & REST APIs
├── templates/              # HTML Templates (Executive Dashboard, Vendor360, etc.)
└── static/                 # Static Assets (CSS, JS, Images, OpenAPI Spec)
```

---

## ⚙️ Required Environment Variables

Configure the following environment variables in the **Vercel Project Settings -> Environment Variables**:

| Variable Name | Purpose | Sample Production Value |
|---|---|---|
| `FLASK_ENV` | Application runtime environment mode | `production` |
| `SECRET_KEY` | Flask session cookie encryption key | `v10-prod-secret-key-9823719283` |
| `JWT_SECRET_KEY` | JSON Web Token signing secret key | `v10-jwt-secret-key-3918273918` |
| `DATABASE_URL` | Optional PostgreSQL / Cloud DB URI | *(Optional - defaults to auto-copied 500-vendor SQLite DB in `/tmp/vendors.db`)* |
| `LOG_LEVEL` | Application logging verbosity | `INFO` |

---

## 💻 Local Testing & Verification Commands

Before deploying to Vercel, verify local execution using PowerShell or Terminal:

```powershell
# 1. Run local development server
$env:PYTHONPATH="."
py app.py

# 2. Test Vercel Serverless Entry Point Import (Check A)
py -c "from api.index import app; print('Vercel Entry Point Exposed:', app)"

# 3. Execute Vercel Pre-Flight Verification Suite
py C:\Users\rahul\.gemini\antigravity\brain\31f2bf25-14f5-4ffc-b043-7525b100fe53\scratch\verify_vercel_preflight_checklist.py
```

---

## ☁️ Deployment Commands (Vercel CLI & Git)

### Method 1: Git Integration (Recommended)
1. Push all code changes to your GitHub/GitLab repository branch (`main`).
2. Import repository into **Vercel Dashboard** (`https://vercel.com/new`).
3. Vercel will automatically detect `vercel.json` and `api/index.py` and deploy.

### Method 2: Vercel CLI Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy directly from repository root
vercel --prod
```

---

## 🧪 Post-Deployment Verification Steps

After Vercel completes deployment, test your public URL (`https://<your-app>.vercel.app`):

1. **Unauthenticated Health Probe**:
   `GET https://<your-app>.vercel.app/health`
   - Expected Response: `{"status": "healthy"}` (HTTP 200)

2. **Executive Command Center Landing**:
   `GET https://<your-app>.vercel.app/`
   - Expected UI: Executive Dashboard with 500 Active Vendors KPI

3. **Active Vendor Registry Table**:
   `GET https://<your-app>.vercel.app/dashboard`
   - Expected UI: 10 Vendor Rows rendered on Page 1 (`Showing 1 - 10 of 500 vendors`)

4. **API Vendor Search Endpoint**:
   `GET https://<your-app>.vercel.app/api/v2/search?query=&page=1&limit=10`
   - Expected JSON: `{"success": true, "total": 500, "results": [...]}`

---

## ⚡ Serverless Architecture & Real-Time Server Lifecycle

1. **Ephemeral Filesystem (`/tmp`)**:
   - Vercel Serverless Functions execute inside an ephemeral container sandbox where only the `/tmp` directory is writable.
   - On function cold start, `src/config.py` automatically copies the authoritative 500-vendor SQLite database (`instance/vendors.db`) to `/tmp/vendors.db`.
   - This provides the Flask application a 100% writable, pre-populated database without `sqlite3.OperationalError` read-only locking errors.

2. **Persistent Socket Server & Port 5001 Isolation**:
   - Vercel Serverless Functions operate on a request-driven HTTP execution lifecycle. They do **NOT** support long-lived background process daemons, `asyncio` event loops, or listening on custom TCP ports (e.g. `0.0.0.0:5001`).
   - In previous iterations, `create_app()` automatically executed `EventQueue.start_realtime_server(port=5001)` on import, attempting to bind port 5001 and throwing `[Errno 10048]`.
   - **Refactored Architecture**:
     - **Import & Factory Isolation**: `create_app()` and `from api.index import app` are now 100% side-effect-free. Zero sockets are bound, zero ports are listened on, and zero background threads are spawned during module import.
     - **Local Development**: Running `py app.py` as `__main__` starts both the local Flask server on `port 5000` AND the background WebSocket gateway on `port 5001`.
     - **Vercel Serverless Runtime**: Vercel imports `app` safely from `api/index.py`. All REST endpoints, Executive Dashboard UI, Vendor 360, Fraud Detection, OCR, AI Copilot RAG, and JSON exports operate seamlessly over standard HTTP/HTTPS.
