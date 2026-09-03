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
   pulled directly; scanned PDFs and images fall back to OCR (EasyOCR).
3. A classifier (trained on a synthetic, self-generated dataset) labels the
   document type (pay stub, bank statement, budget sheet), and a rules-based
   engine pulls out key fields (income, expenses) and turns them into
   plain-language insights: withholding rate, savings rate, overspending
   warnings.
4. The frontend shows the extracted data and insights. The original file is
   never stored; a JWT-protected endpoint exposes an in-memory history of
   past analyses (filename, classification, insights) for the current
   server session only, cleared on restart.

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
| Classifier | scikit-learn (TF-IDF + logistic regression)   |
| Synthetic data | Faker                                     |
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
- **No persistent storage of uploaded documents.** The original file is
  processed in memory and discarded. Only derived, non-file insights
  (filename, classification, generated insights) are kept in an in-memory
  history for the current server process, and that's wiped on restart.
- **Bounded upload reads.** Files are read in fixed-size chunks with the
  size limit enforced as each chunk arrives, not after the whole file is
  buffered — an oversized upload is rejected before it can exhaust memory.
- **JWT-protected routes.** The analysis history endpoint requires a bearer
  token issued by `/api/auth/login`; the login route is itself rate-limited
  to blunt credential-guessing attempts, and the credential check uses a
  constant-time comparison rather than `==`.
- **Security response headers** (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`) on every response.
- **Graceful degradation under resource pressure.** If the OCR model fails
  to load (e.g. not enough memory on a constrained host), the app still
  starts; born-digital PDFs keep working via direct text extraction, and
  only OCR-dependent uploads report it's unavailable, instead of the whole
  service crash-looping.
- **Insecure-default guard.** At startup, if `ENVIRONMENT=production` and
  the JWT secret or demo password are still at their placeholder default,
  the server logs a clear error so that's caught before real traffic hits it.
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
python -m app.ml.generate_dataset   # one-time: builds a synthetic training set
python -m app.ml.train_classifier   # one-time: trains and saves the classifier
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`, with a health check at
`GET /api/health`. On first startup it downloads the EasyOCR model weights
(a one-time download, needs internet access); after that they're cached
locally and startup is fast. If you skip the two `app.ml` commands, the API
still runs; document classification is just skipped (uploads still get text
extraction and field-based insights).

The demo login (`POST /api/auth/login`) uses the `DEMO_USERNAME` /
`DEMO_PASSWORD` values from your `.env` — it's a single hardcoded credential
pair to demonstrate JWT-protected routes, not a real user system.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app is now at the URL Vite prints (default `http://localhost:5173`).

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

The suite mocks out OCR and the classifier at the route level, so it runs in
a couple of seconds with no network access, no EasyOCR model download, and
no trained classifier required. It covers file validation (signature/size
checks), the insight engine's field extraction and math, JWT creation and
expiry, the login and protected-history routes, and the upload route's
happy path plus its untrained-classifier fallback.

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs this test suite
and a frontend production build on every push and pull request against
`main`.

## Project structure

```
CredenceScan/
├── .github/workflows/ci.yml   test + build on every push/PR
├── backend/
│   ├── app/
│   │   ├── main.py           FastAPI app, middleware, error handlers
│   │   ├── core/              config, logging, security, auth, deps
│   │   ├── api/routes/        route handlers (health, documents, auth)
│   │   ├── services/          OCR, classifier, insight engine, history
│   │   └── ml/                dataset generation + classifier training
│   ├── tests/                 pytest suite
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   └── components/        ApiStatus, UploadForm, AccountPanel
│   └── package.json
├── render.yaml                deployment blueprint
└── README.md
```

## Known limitations

- The classifier is trained entirely on synthetic, template-generated text,
  so each document type has distinct boilerplate phrases (e.g. "Pay Stub" vs
  "Account Statement"). It reports near-perfect accuracy on held-out
  synthetic data, which is easier than real-world documents; it hasn't been
  validated against real-world formatting variety.
- The insight engine matches a small, fixed set of field labels via keyword
  search (e.g. "gross income", "net pay"). Documents that phrase these
  differently won't have those fields extracted.
- The demo login is a single hardcoded credential pair, not a real user
  system with registration or persistent accounts. Because of that, the
  analysis history is a single shared list rather than scoped per account —
  fine for a one-account demo, not a pattern to keep in a real multi-user
  system.
- EasyOCR pulls in PyTorch, which is a real memory footprint. It's untested
  on Render's free tier (512MB RAM); the app is built to degrade gracefully
  if OCR can't load there rather than crash-loop, but born-digital-PDF-only
  operation may be what actually works on that tier in practice. See
  [Deployment](#deployment).

## Roadmap

- [x] **Phase 1:** repo scaffold. FastAPI + Vue skeletons wired together,
      security middleware (rate limiting, CORS, structured logging, error
      handling), README.
- [x] **Phase 2:** document upload endpoint with file validation
      (size/magic-byte checks) and text extraction (direct text-layer
      extraction for born-digital PDFs, OCR fallback for scans and images).
- [x] **Phase 3:** synthetic dataset generation (Faker-based templates for
      pay stubs, bank statements, budget sheets) and a trained document-type
      classifier (TF-IDF + logistic regression, scikit-learn).
- [x] **Phase 4:** rules-based budgeting insight engine, JWT auth with a
      protected analysis-history endpoint, frontend upload results view and
      login/history panel.
- [x] **Phase 5:** pytest suite + GitHub Actions CI, a security pass
      (bounded upload reads, constant-time credential check, security
      headers, graceful OCR degradation, insecure-default startup guard),
      and a Render deployment blueprint. Actually deploying still requires
      a Render account — see [Deployment](#deployment).

## Deployment

`render.yaml` is a Render Blueprint defining both services (the FastAPI
backend and the static Vue frontend) on the free plan. To use it:

1. Push this repo to GitHub (already done if you're reading this on
   github.com/richet311/credencescan).
2. In Render, choose **New +** -> **Blueprint** and point it at the repo.
   Render reads `render.yaml` and proposes both services.
3. Deploy. `JWT_SECRET_KEY` and `DEMO_PASSWORD` are auto-generated; `PORT`
   is supplied by Render.
4. Once both services have their `onrender.com` URLs, set `ALLOWED_ORIGINS`
   on the backend service to the frontend's URL, and `VITE_API_BASE_URL` on
   the frontend service to the backend's URL, then redeploy both. Neither
   can be known before the first deploy, which is why they're left for this
   manual step rather than baked into the blueprint.

This blueprint hasn't been run against a live Render account — verify the
service keys against Render's current Blueprint docs if anything doesn't
match what you see in the dashboard, and treat step 2 onward as something
you'll need to actually click through and adjust, not a guaranteed one-shot.
The known risk called out in
[Known limitations](#known-limitations) — EasyOCR/PyTorch's memory
footprint versus the free tier's 512MB — is the most likely thing to need
iterating on.

## Emulating this project

Everything above is enough to clone this repo, install dependencies, and run
both services locally. Copy `.env.example` to `.env` in both `backend/` and
`frontend/` and adjust values as needed. No external accounts or paid
services are required to run it.

## License

MIT, see [LICENSE](LICENSE).
