# CredenceScan

A privacy-first web app that reads financial documents (pay stubs, bank
statements, budget sheets) and turns them into plain-language budgeting
insights — without ever touching a real bank account.

> **Disclaimer:** This is an independent personal project. It is **not**
> affiliated with, endorsed by, or connected to any bank, credit union, or
> financial institution. It does not connect to real accounts or real
> financial data of any kind. All sample documents used for development and
> demos are synthetic, generated for this project.

## Why this exists

This project was built as a portfolio piece ahead of a fintech-focused,
social-impact hackathon application — a way to demonstrate secure full-stack
development and applied ML skills (OCR, model training, API security) end to
end, on a problem that's genuinely useful to nonprofits and individuals
working on financial literacy.

## What it does

1. A user uploads a sample financial document (image or PDF).
2. The backend extracts text via OCR, then classifies the document type and
   pulls out key fields (income, expenses, line items) using a lightweight
   model trained on a synthetic, self-generated dataset.
3. A rules-based insight engine turns those fields into plain-language
   feedback: spending breakdown, savings rate, budgeting suggestions.
4. The frontend shows the extracted data and insights — nothing is persisted
   beyond the session unless the user explicitly saves it.

## Architecture

```
frontend/  Vue 3 + Vite SPA
   |
   |  HTTPS, rate-limited, CORS-locked
   v
backend/   FastAPI service
   - OCR + document classification pipeline
   - Insight engine
   - JWT-based auth
   - Structured logging + centralized error handling
```

## Tech stack

| Layer      | Choice                                      |
|------------|----------------------------------------------|
| Frontend   | Vue 3, Vite, plain JavaScript (no TypeScript) |
| Backend    | Python, FastAPI                               |
| Auth       | JWT (`python-jose`, `passlib`)                |
| Rate limiting | `slowapi`                                   |
| OCR        | EasyOCR / Tesseract (added in a later phase)  |
| Hosting    | Render.com free tier                          |

No paid or credit-card-gated cloud services are used anywhere in this
project.

## Security

- **Rate limiting** on every API route via `slowapi`, keyed by client IP, to
  prevent abuse and accidental self-DoS.
- **CORS** locked to an explicit allow-list of origins (configured via env
  var), not wildcarded.
- **Input validation** via Pydantic models on every request body; uploaded
  files (added in a later phase) are checked by size, extension, and magic
  bytes before processing.
- **No persistent storage of uploaded documents** — processing happens
  in-memory for the life of the request.
- **Centralized error handling** — all exceptions are caught, logged with
  context on the server, and returned to clients as generic messages (no
  stack traces or internals leak over the API).
- **Structured logging** to the console so failures are visible to whoever
  is running the service, without exposing sensitive data in logs.

## Getting started

### Prerequisites

- Python 3.13
- Node.js 20+

### Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate      # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`, with a health check at
`GET /api/health`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app is now at the URL Vite prints (default `http://localhost:5173`).

## Project structure

```
CredenceScan/
├── backend/
│   ├── app/
│   │   ├── main.py           FastAPI app, middleware, error handlers
│   │   ├── core/              config, logging, security/rate-limiting
│   │   └── api/routes/        route handlers
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   └── components/
│   └── package.json
└── README.md
```

## Roadmap

- [x] **Phase 1** — Repo scaffold: FastAPI + Vue skeletons wired together,
      security middleware (rate limiting, CORS, structured logging, error
      handling), README.
- [ ] **Phase 2** — Document upload endpoint with file validation
      (type/size/magic-byte checks) and OCR text extraction.
- [ ] **Phase 3** — Synthetic dataset generation and training of the
      document-type classifier / field-extraction model.
- [ ] **Phase 4** — Budgeting insight engine, JWT auth, frontend upload +
      results UI.
- [ ] **Phase 5** — Tests, CI, security pass, deployment to Render.

## Emulating this project

Everything above is enough to clone this repo, install dependencies, and run
both services locally. Copy `.env.example` to `.env` in both `backend/` and
`frontend/` and adjust values as needed — no external accounts or paid
services are required to run it.

## License

MIT — see [LICENSE](LICENSE).
