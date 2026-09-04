from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.routes import upload, analysis, pdf
import os

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="SmartReports API",
    description="AI-Powered Pathology Report Analyzer",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(pdf.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SmartReports API - AI-Powered Pathology Report Analyzer",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "smartreports-api"
    }


@app.get("/api/v1/reference/tests")
async def get_reference_tests():
    """Get reference test definitions"""
    from app.services.analysis_service import LabTestAnalysisService

    tests = []
    for test_name, info in LabTestAnalysisService.TEST_DEFINITIONS.items():
        tests.append({
            "test_name": test_name,
            "unit": info["unit"],
            "normal_range_min": info["min"],
            "normal_range_max": info["max"],
            "aliases": info["aliases"]
        })

    return JSONResponse({"tests": tests})


@app.get("/api/v1/reference/organs")
async def get_reference_organs():
    """Get reference organ definitions"""
    from app.services.organ_health_service import OrganHealthService

    organs = []
    for organ_name, tests in OrganHealthService.ORGAN_TEST_MAPPING.items():
        organs.append({
            "organ_name": organ_name,
            "related_tests": tests,
            "description": OrganHealthService.ORGAN_DESCRIPTIONS.get(organ_name, "")
        })

    return JSONResponse({"organs": organs})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
