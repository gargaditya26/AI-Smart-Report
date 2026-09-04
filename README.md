# Smartreports - AI-Powered Pathology Report Analyzer

A single-page web application that allows users to upload pathology reports, automatically extract lab test results using AI/ML, analyze organ health, and generate comprehensive visual PDF reports.

## Features

- Upload pathology reports (PDF, TXT, JPG, PNG, DOCX)
- AI-powered text extraction and lab test analysis
- Editable lab results table
- Organ health visualization with human body diagram
- AI-generated health recommendations
- PDF report generation with health scores
- Privacy-focused: no permanent storage of uploaded reports

## Technology Stack

### Backend
- FastAPI (Python 3.11+)
- Redis (session/temporary storage)
- PostgreSQL (reference data)
- spaCy + scispaCy (Medical NER)
- PyPDF2, pytesseract (text extraction)
- WeasyPrint (PDF generation)

### Frontend
- React 18+ with Vite
- Tailwind CSS + shadcn/ui
- Axios (HTTP client)
- Recharts (data visualization)
- react-pdf (PDF viewer)
- Framer Motion (animations)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis
- PostgreSQL
- Tesseract OCR

### Installation & Running

**Option 1: Using the startup script (Recommended)**
```bash
chmod +x run.sh
./run.sh
```

**Option 2: Manual setup**

1. Start Redis and PostgreSQL services

2. Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download en_core_sci_sm
uvicorn main:app --reload --port 8000
```

3. Frontend setup (in a new terminal):
```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

### Backend (.env in backend/)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smartreports
DB_USER=postgres
DB_PASSWORD=your_password

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=your-secret-key-here
SESSION_TTL=3600

STORAGE_TYPE=local  # or 's3' or 'azure'
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_BUCKET_NAME=
```

### Frontend (.env in frontend/)
```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
Smartreport/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── utils/           # Utilities
│   │   ├── config/          # Configuration
│   │   └── templates/       # PDF templates
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── hooks/           # Custom hooks
│   │   └── utils/           # Utilities
│   ├── package.json
│   └── vite.config.js
├── run.sh                   # Startup script
└── README.md
```

## API Endpoints

### Upload
- `POST /api/v1/reports/upload` - Upload pathology report
- `GET /api/v1/reports/status/:sessionId` - Get processing status
- `DELETE /api/v1/reports/session/:sessionId` - Delete session

### Analysis
- `POST /api/v1/analysis/extract/:sessionId` - Extract lab tests
- `GET /api/v1/analysis/results/:sessionId` - Get lab results
- `PUT /api/v1/analysis/results/:sessionId` - Update lab results
- `POST /api/v1/analysis/calculate/:sessionId` - Calculate organ scores
- `GET /api/v1/analysis/organ-scores/:sessionId` - Get organ health scores
- `GET /api/v1/analysis/recommendations/:sessionId` - Get recommendations

### PDF
- `POST /api/v1/pdf/generate/:sessionId` - Generate PDF report
- `GET /api/v1/pdf/:pdfId` - Get PDF
- `GET /api/v1/pdf/:pdfId/download` - Download PDF
- `DELETE /api/v1/pdf/:pdfId` - Delete PDF

## Privacy & Security

- Uploaded reports are stored temporarily in Redis (1-hour TTL)
- No permanent storage of patient health information
- Generated PDFs can be deleted immediately by users
- All session data auto-expires after 1 hour
- File virus scanning before processing
- Input validation and sanitization

## Development

### Running Tests

Backend:
```bash
cd backend
pytest -v
```

Frontend:
```bash
cd frontend
npm test
```

### Code Quality

Backend:
```bash
black app/
flake8 app/
```

Frontend:
```bash
npm run lint
npm run format
```

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact support@smartreports.com
