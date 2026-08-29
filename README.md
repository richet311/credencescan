# CredenceScan

A privacy-first web app that reads financial documents (pay stubs, bank
statements, budget sheets) and turns them into plain-language budgeting
insights, without ever touching a real bank account.

> **Disclaimer:** This is an independent personal project. It is not
> affiliated with, endorsed by, or connected to any bank, credit union, or
> financial institution, and it does not connect to real accounts or real
> financial data. All sample documents used for development and demos are
> synthetic.

## Why this exists

Built as a portfolio project ahead of a fintech-focused, social-impact
hackathon application. It's meant to show secure full-stack development and
applied ML skills (OCR, model training, API security), on a problem that's
actually useful to nonprofits and individuals working on financial literacy.

## What it does

1. A user uploads a sample financial document (image or PDF).
2. The backend extracts the text. Born-digital PDFs get their embedded text
   pulled directly; scanned PDFs and images fall back to OCR (EasyOCR). It
   then classifies the document type and pulls out key fields (income,
   expenses, line items) using a lightweight model trained on a synthetic,
   self-generated dataset.
3. A rules-based insight engine turns those fields into plain-language
   feedback: spending breakdown, savings rate, budgeting suggestions.
4. The frontend shows the extracted data and insights. Nothing is persisted
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
| OCR        | EasyOCR, PyMuPDF (for born-digital PDF text)  |
| Hosting    | Render.com free tier                          |

No paid or credit-card-gated cloud services are used anywhere in this
project.

## Security

- **Rate limiting** on every API route via `slowapi`, keyed by client IP, to
  prevent abuse and accidental self-DoS.
- **CORS** locked to an explicit allow list of origins (set via env var),
  not wildcarded.
- **Input validation** via Pydantic models on every request body. Uploaded
  files are checked against a size limit and their actual file signature
  (magic bytes), not just their extension, so a renamed/spoofed file gets
  rejected before it's processed.
- **No persistent storage of uploaded documents.** Processing happens
  in-memory for the life of the request.
- **Centralized error handling.** Exceptions are caught, logged with context
  on the server, and returned to clients as generic messages, so no stack
  traces or internals leak over the API.
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
`GET /api/health`. On first startup it downloads the EasyOCR model weights
(a one-time download, needs internet access); after that they're cached
locally and startup is fast.

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

- [x] **Phase 1:** repo scaffold. FastAPI + Vue skeletons wired together,
      security middleware (rate limiting, CORS, structured logging, error
      handling), README.
- [x] **Phase 2:** document upload endpoint with file validation
      (size/magic-byte checks) and text extraction (direct text-layer
      extraction for born-digital PDFs, OCR fallback for scans and images).
- [ ] **Phase 3:** synthetic dataset generation and training the
      document-type classifier / field-extraction model.
- [ ] **Phase 4:** budgeting insight engine, JWT auth, frontend upload +
      results UI.
- [ ] **Phase 5:** tests, CI, security pass, deployment to Render.

## Emulating this project

Everything above is enough to clone this repo, install dependencies, and run
both services locally. Copy `.env.example` to `.env` in both `backend/` and
`frontend/` and adjust values as needed. No external accounts or paid
services are required to run it.

## License

MIT, see [LICENSE](LICENSE).
