import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.models import DocumentInfo
from app.services.ingestion import ingest_pdf, list_documents, delete_document

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"application/pdf"}


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Save uploaded file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    dest = settings.UPLOAD_DIR / filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = ingest_pdf(str(dest), file.filename)
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    return DocumentInfo(**result)


@router.get("/", response_model=list[DocumentInfo])
async def get_documents():
    return [DocumentInfo(**d) for d in list_documents()]


@router.delete("/{document_id}")
async def remove_document(document_id: str):
    if not delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "deleted", "document_id": document_id}
