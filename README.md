# BFSG Checker (Starter: Single URL, Mobile+Desktop, robots.txt, PDF, Docker, SQLite, Worker)

This is a lightweight training/demo project that scans **one URL** for accessibility issues (WCAG 2.1 AA focused),
respects **robots.txt**, runs checks in **desktop + mobile** viewports, generates a **PDF report**, and stores results in **SQLite**.

- **No Redis / No Celery / No Postgres**
- Uses a simple DB-backed job queue (SQLite row status: queued → running → done/failed)
- Designed to have **few moving parts** and be easy to run.

## What you get
- `POST /scan` to enqueue a scan
- `GET /scan/{id}` to view status + summary + findings
- `GET /scans` list scan history
- `GET /report/{id}.pdf` download PDF report
- Screenshots (desktop+mobile) saved under `data/artifacts/screenshots/`

---

## 0) Prerequisites
- Docker + Docker Compose (recommended)

> You can also run locally with Python, but Playwright browser setup is easiest via Docker.

---

## 1) Quick start (Docker)

### 1.1 Build & run
From the project root:

Create .env file out of the .env.example file

Run this command to download the file locally

```bash
curl -L https://unpkg.com/axe-core@4.10.2/axe.min.js -o vendor/axe/axe.min.js
```

To start the docker containers run the command

```bash
docker compose up --build
```

This starts two containers:
- `api` (FastAPI) on http://localhost:8000
- `worker` (background job processor)

### 1.2 Open API docs
Go to:
- http://localhost:8000/docs

---

## 2) Run your first scan

### 2.1 Enqueue a scan
```bash
curl -X POST http://localhost:8000/scan -H "Content-Type: application/json" -d '{"url":"https://wailshalabi.com"}'
```

Response:
```json
{"scan_id": 1, "status": "queued"}
```

### 2.2 Check status
```bash
curl http://localhost:8000/scan/1
```

When finished, you'll see:
- `status: "done"`
- `summary` counts
- `findings` list
- `report_pdf_url`

### 2.3 Download the PDF report
```bash
curl -L http://localhost:8000/report/1.pdf -o report_1.pdf
```

---

## 3) Data locations
The project uses a local folder `./data` (mounted into containers):

- SQLite DB: `data/bfsg_checker.sqlite`
- Screenshots: `data/artifacts/screenshots/<scan_id>/...png`
- PDFs: `data/artifacts/reports/<scan_id>/report.pdf`

---

## 4) Configuration
Copy `.env.example` to `.env` and adjust if needed.

Key settings:
- `SCAN_TIMEOUT_MS` (default 45000)
- `MAX_NAVIGATION_WAIT_MS` (default 30000)
- `USER_AGENT` (optional)
- `ALLOW_ROBOTS_DENY` (default true) – if true, disallowed URLs are rejected

---

## 5) Notes & limitations (important)
- Automated checking cannot prove full BFSG compliance; it helps catch common issues.
- The scan is **single URL only** (no crawling).
- robots.txt is checked for the given URL path and the configured user-agent.
- Findings come from **axe-core** and are mapped to basic fix hints.

---

## 6) Local development (optional, without Docker)
If you want local dev:

1) Install Python 3.12+
2) Create venv
3) Install requirements:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```
4) Ensure `axe.min.js` exists at `./vendor/axe/axe.min.js` (Docker handles this automatically).

Then run:
```bash
uvicorn app.main:app --reload
python -m app.jobs.worker
```

---

## 7) Common troubleshooting
- **Scan stuck in queued**: ensure the `worker` container is running.
- **Browser errors**: rebuild images: `docker compose build --no-cache`
- **robots denied**: either scan an allowed path or set `ALLOW_ROBOTS_DENY=false` in `.env`.

---

## 8) Next upgrades (if you continue)
- Add auth scanning (login scripts)
- Add multi-page crawling with rate limits
- Replace SQLite worker with Redis/Celery for scale
- Add HTML report endpoint and UI dashboard
