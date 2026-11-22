from fastapi.responses import StreamingResponse
from backend.app.services.pdf_service import generate_pdf_report
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.services.resume_service import (
    extract_resume_text,
    analyze_resume
)

router = APIRouter(prefix="/api/resume", tags=["Resume Analysis"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/analyze")
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Upload a resume and analyze it against a job description."""

    extension = Path(file.filename or "").suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide a job description."
        )

    temp_path = None

    try:
        file_content = await file.read(MAX_FILE_SIZE + 1)

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 5 MB."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        resume_text = extract_resume_text(temp_path)

        results = analyze_resume(
            resume_text,
            job_description
        )

        return {
            "success": True,
            "filename": file.filename,
            "message": "Resume analysis completed successfully.",
            "results": results
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Resume analysis failed. Please try again."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.post(
    "/report",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    }
)
async def download_resume_report(payload: dict):
    try:
        results = payload.get("results", payload)

        report_data = {
            **results,
            "filename": payload.get("filename", "Resume"),
            "job_description": payload.get("job_description", "Not provided")
        }

        pdf_buffer = generate_pdf_report(report_data)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="NeuroNexus_Resume_Report.pdf"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate PDF report: {str(e)}"
        )
