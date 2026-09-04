# SmartReports - Quick Start Guide

## Prerequisites

Before running SmartReports, ensure you have the following installed:

1. **Python 3.11+**
   ```bash
   python3 --version
   ```

2. **Node.js 18+**
   ```bash
   node --version
   ```

3. **Redis**
   - macOS: `brew install redis && brew services start redis`
   - Linux: `sudo apt-get install redis-server && sudo systemctl start redis`
   - Windows: Download from https://redis.io/download

4. **Tesseract OCR** (for image text extraction)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

## Installation & Running

### Option 1: Using the Startup Script (Recommended)

1. Navigate to the project directory:
   ```bash
   cd /Users/nooram/Desktop/Labbuddy/GitHub/Smartreport
   ```

2. Make the script executable (if not already):
   ```bash
   chmod +x run.sh
   ```

3. Run the startup script:
   ```bash
   ./run.sh
   ```

   This will:
   - Check prerequisites
   - Install Python dependencies (first run only)
   - Install Node.js dependencies (first run only)
   - Start the backend on port 8000
   - Start the frontend on port 5173

4. Open your browser and navigate to:
   - **Frontend**: http://localhost:5173
   - **API Documentation**: http://localhost:8000/docs

5. To stop the application, press `Ctrl+C` in the terminal

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download spaCy models:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Create necessary directories:
   ```bash
   mkdir -p uploads pdfs
   ```

6. Start the backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

#### Frontend Setup (in a new terminal)

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. **Upload Report**: Drag and drop or click to upload a pathology report (PDF, TXT, JPG, PNG, DOCX)

2. **Processing**: The system will:
   - Extract text from your document
   - Identify lab test results using AI
   - Display results for your review

3. **Review & Edit**:
   - Check the extracted test results
   - Add missing tests manually
   - Edit any incorrect values
   - Delete irrelevant tests

4. **Analyze Health**: Click "Analyze Organ Health" to:
   - Calculate organ health scores
   - Get personalized recommendations
   - View overall health assessment

5. **Generate Report**: Click "Generate PDF Report" to:
   - Create a comprehensive PDF report
   - Download for your records
   - Share with healthcare providers

## Supported File Formats

- **PDF**: Direct text extraction or OCR
- **TXT**: Plain text files
- **JPG/PNG**: OCR-based text extraction
- **DOCX**: Microsoft Word documents

## Troubleshooting

### Redis Connection Error
```
Error: Redis is not running
```
**Solution**: Start Redis service
- macOS: `brew services start redis`
- Linux: `sudo systemctl start redis`

### Port Already in Use
```
Error: Port 8000 is already in use
```
**Solution**: Kill the process using the port or change the port in the code

### Tesseract Not Found
```
Error: Tesseract command not found
```
**Solution**:
1. Install Tesseract (see Prerequisites)
2. Update `TESSERACT_CMD` in `backend/.env` with the correct path

### Module Not Found Errors
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

### Backend Configuration (backend/.env)

Key settings you may want to adjust:

- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `SESSION_TTL`: Session expiration time in seconds (default: 3600)
- `MAX_FILE_SIZE`: Maximum upload file size (default: 10MB)
- `TESSERACT_CMD`: Path to Tesseract executable

### Frontend Configuration (frontend/.env)

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Production Deployment

For production deployment:

1. **Backend**:
   - Use Gunicorn with Uvicorn workers
   - Set up PostgreSQL database
   - Configure AWS S3 or Azure Blob Storage
   - Enable HTTPS
   - Set strong `SECRET_KEY` in `.env`

2. **Frontend**:
   - Build for production: `npm run build`
   - Serve with Nginx or similar
   - Update `VITE_API_URL` to production API

## Privacy & Security

- Uploaded reports are stored temporarily in Redis (1-hour TTL)
- No permanent storage of patient health information
- Generated PDFs stored for 24 hours (deletable by user)
- All session data auto-expires
- CORS configured for security

## Support

For issues or questions:
- Check the troubleshooting section above
- Review API documentation at http://localhost:8000/docs
- Check logs in the terminal where servers are running

## License

Proprietary - All rights reserved
