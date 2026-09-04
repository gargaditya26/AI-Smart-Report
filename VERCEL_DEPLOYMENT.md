# SmartReports — Vercel Deployment

This package is prepared for a single Vercel project:

- React/Vite frontend → `frontend/dist`
- FastAPI → `api/index.py` under `/api/*`
- Redis → external Redis provider via `REDIS_URL`
- PDF output → `/tmp` per Vercel invocation, with regeneration from Redis metadata when needed

## Deploy

1. Push the whole `Smartreport` folder to GitHub.
2. Import the repository into Vercel.
3. Keep the project root at the repository root. Vercel will use the included `vercel.json`.
4. Add these Environment Variables in Vercel:
   - `REDIS_URL` = your production Redis connection URL
   - `SECRET_KEY` = a long random secret
   - `SESSION_TTL` = `3600`
   - `MAX_FILE_SIZE` = `10485760`
5. Deploy.

The frontend calls `/api/...` on the same domain, so no `VITE_API_URL` is required in production.

## Important OCR note

Direct text extraction from normal text-based PDFs is supported. The existing OCR path (`pytesseract` + `pdf2image`) needs system binaries such as Tesseract/Poppler. Those binaries are not bundled in this Vercel package. Scanned/image-only reports therefore need an external OCR service or a later server/container deployment if OCR is required.

## Local development

Run backend from `backend/`:

```cmd
cd backend
py -m uvicorn main:app --reload --port 8000
```

Run frontend from `frontend/`:

```cmd
npm install
npm run dev
```

For local development, Vite proxies `/api` to port 8000.
