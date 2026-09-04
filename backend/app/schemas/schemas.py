from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID


# Upload Schemas
class UploadResponse(BaseModel):
    session_id: str
    filename: str
    file_size: int
    status: str
    message: str


class ProcessingStatus(BaseModel):
    session_id: str
    stage: Literal["upload", "extraction", "analysis", "completed", "error"]
    progress: int
    message: str
    error: Optional[str] = None


# Lab Test Schemas
class LabTest(BaseModel):
    test_id: str
    test_name: str
    value: float
    unit: str
    normal_range_min: Optional[float] = None
    normal_range_max: Optional[float] = None
    status: Literal["Normal", "Slightly High", "Slightly Low", "High", "Low", "Critical High", "Critical Low"]
    deviation_percentage: float = 0
    confidence_score: float = 0.0
    source: Literal["extracted", "manual"] = "extracted"


class LabTestCreate(BaseModel):
    test_name: str
    value: float
    unit: str


class LabTestUpdate(BaseModel):
    test_name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None


class LabResultsResponse(BaseModel):
    session_id: str
    lab_results: List[LabTest]
    total_tests: int
    extraction_confidence: float


# Organ Health Schemas
class RelatedTest(BaseModel):
    test_name: str
    value: float
    unit: str
    status: str


class OrganScore(BaseModel):
    organ_id: str
    organ_name: str
    health_score: int
    status: Literal["Excellent", "Good", "Attention Needed", "Concerning", "Critical"]
    color: Literal["green", "yellow", "orange", "red"]
    test_count: int
    abnormal_test_count: int
    related_tests: List[RelatedTest]
    description: Optional[str] = None


class Recommendation(BaseModel):
    recommendation_id: str
    organ_name: str
    text: str
    category: Literal["immediate", "lifestyle", "dietary", "follow_up", "consult_doctor"]
    priority: int
    severity: Literal["critical", "important", "suggested", "optional"]
    related_tests: List[str]


class OrganScoresResponse(BaseModel):
    session_id: str
    overall_health_score: int
    organ_scores: List[OrganScore]
    recommendations: List[Recommendation]


# PDF Schemas
class PDFGenerateRequest(BaseModel):
    session_id: str


class PDFGenerateResponse(BaseModel):
    pdf_id: str
    pdf_url: str
    message: str
    generation_date: datetime


# Error Schema
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
    timestamp: datetime


# Reference Data Schemas
class TestDefinition(BaseModel):
    test_name: str
    category: str
    normal_range_min: Optional[float]
    normal_range_max: Optional[float]
    unit: str
    aliases: List[str] = []


class OrganDefinition(BaseModel):
    organ_id: str
    organ_name: str
    description: str
    related_tests: List[str]
