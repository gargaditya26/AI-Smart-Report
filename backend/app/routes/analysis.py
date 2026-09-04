from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.schemas import (
    LabResultsResponse, LabTestCreate, LabTestUpdate,
    OrganScoresResponse
)
from app.services.analysis_service import LabTestAnalysisService
from app.services.organ_health_service import OrganHealthService
from app.config.redis_client import redis_client
from app.config.settings import settings
from typing import List

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/extract/{session_id}")
async def extract_lab_tests(session_id: str):
    """Extract lab tests from uploaded report"""

    # Get extracted text
    text_data = redis_client.get_json(f"extracted_text:{session_id}")

    if not text_data:
        raise HTTPException(status_code=404, detail="Session not found or text not extracted")

    extracted_text = text_data.get("text", "")

    # Extract lab tests
    lab_results = LabTestAnalysisService.extract_lab_tests(extracted_text)

    if not lab_results:
        # Return empty results, user can add manually
        lab_results = []

    # Store lab results
    redis_client.set_json(f"lab_results:{session_id}", lab_results, ttl=settings.SESSION_TTL)

    # Update metadata
    metadata = redis_client.get_json(f"metadata:{session_id}")
    if metadata:
        metadata["status"] = "analyzed"
        redis_client.set_json(f"metadata:{session_id}", metadata, ttl=settings.SESSION_TTL)

    # Calculate confidence
    if lab_results:
        avg_confidence = sum(t["confidence_score"] for t in lab_results) / len(lab_results)
    else:
        avg_confidence = 0.0

    return LabResultsResponse(
        session_id=session_id,
        lab_results=lab_results,
        total_tests=len(lab_results),
        extraction_confidence=avg_confidence
    )


@router.get("/results/{session_id}", response_model=LabResultsResponse)
async def get_lab_results(session_id: str):
    """Get lab test results for a session"""

    lab_results = redis_client.get_json(f"lab_results:{session_id}")

    if lab_results is None:
        raise HTTPException(status_code=404, detail="Lab results not found for this session")

    # Calculate confidence
    if lab_results:
        avg_confidence = sum(t["confidence_score"] for t in lab_results) / len(lab_results)
    else:
        avg_confidence = 0.0

    return LabResultsResponse(
        session_id=session_id,
        lab_results=lab_results,
        total_tests=len(lab_results),
        extraction_confidence=avg_confidence
    )


@router.put("/results/{session_id}")
async def update_lab_results(session_id: str, lab_results: List[dict]):
    """Update entire lab results set"""

    # Store updated results
    redis_client.set_json(f"lab_results:{session_id}", lab_results, ttl=settings.SESSION_TTL)

    return JSONResponse({"message": "Lab results updated successfully"})


@router.post("/add-test/{session_id}")
async def add_manual_test(session_id: str, test_data: LabTestCreate):
    """Add a test manually"""

    # Get existing results
    lab_results = redis_client.get_json(f"lab_results:{session_id}")

    if lab_results is None:
        lab_results = []

    # Add new test
    new_test = LabTestAnalysisService.add_manual_test(
        test_data.test_name,
        test_data.value,
        test_data.unit
    )

    lab_results.append(new_test)

    # Store updated results
    redis_client.set_json(f"lab_results:{session_id}", lab_results, ttl=settings.SESSION_TTL)

    return JSONResponse({"message": "Test added successfully", "test": new_test})


@router.put("/update-test/{session_id}/{test_id}")
async def update_test(session_id: str, test_id: str, test_data: LabTestUpdate):
    """Update a specific test"""

    # Get existing results
    lab_results = redis_client.get_json(f"lab_results:{session_id}")

    if lab_results is None:
        raise HTTPException(status_code=404, detail="Lab results not found")

    # Find and update test
    test_found = False
    for test in lab_results:
        if test["test_id"] == test_id:
            if test_data.test_name:
                test["test_name"] = test_data.test_name
            if test_data.value is not None:
                test["value"] = test_data.value
            if test_data.unit:
                test["unit"] = test_data.unit

            # Recalculate status if value changed
            if test_data.value is not None and test.get("normal_range_min") and test.get("normal_range_max"):
                status, deviation = LabTestAnalysisService._calculate_status(
                    test["value"],
                    test["normal_range_min"],
                    test["normal_range_max"]
                )
                test["status"] = status
                test["deviation_percentage"] = deviation

            test_found = True
            break

    if not test_found:
        raise HTTPException(status_code=404, detail="Test not found")

    # Store updated results
    redis_client.set_json(f"lab_results:{session_id}", lab_results, ttl=settings.SESSION_TTL)

    return JSONResponse({"message": "Test updated successfully"})


@router.delete("/delete-test/{session_id}/{test_id}")
async def delete_test(session_id: str, test_id: str):
    """Delete a specific test"""

    # Get existing results
    lab_results = redis_client.get_json(f"lab_results:{session_id}")

    if lab_results is None:
        raise HTTPException(status_code=404, detail="Lab results not found")

    # Remove test
    lab_results = [test for test in lab_results if test["test_id"] != test_id]

    # Store updated results
    redis_client.set_json(f"lab_results:{session_id}", lab_results, ttl=settings.SESSION_TTL)

    return JSONResponse({"message": "Test deleted successfully"})


@router.post("/calculate/{session_id}")
async def calculate_organ_scores(session_id: str):
    """Calculate organ health scores"""

    # Get lab results
    lab_results = redis_client.get_json(f"lab_results:{session_id}")

    if not lab_results:
        raise HTTPException(status_code=404, detail="Lab results not found")

    # Calculate organ scores
    organ_data = OrganHealthService.calculate_organ_scores(lab_results)

    # Store organ scores
    redis_client.set_json(f"organ_scores:{session_id}", organ_data, ttl=settings.SESSION_TTL)

    return JSONResponse({"message": "Organ scores calculated successfully"})


@router.get("/organ-scores/{session_id}", response_model=OrganScoresResponse)
async def get_organ_scores(session_id: str):
    """Get organ health scores"""

    organ_data = redis_client.get_json(f"organ_scores:{session_id}")

    if not organ_data:
        raise HTTPException(
            status_code=404,
            detail="Organ scores not calculated. Please calculate first."
        )

    return OrganScoresResponse(
        session_id=session_id,
        overall_health_score=organ_data["overall_health_score"],
        organ_scores=organ_data["organ_scores"],
        recommendations=organ_data["recommendations"]
    )


@router.get("/recommendations/{session_id}")
async def get_recommendations(session_id: str):
    """Get health recommendations"""

    organ_data = redis_client.get_json(f"organ_scores:{session_id}")

    if not organ_data:
        raise HTTPException(status_code=404, detail="Recommendations not available")

    return JSONResponse({"recommendations": organ_data.get("recommendations", [])})
