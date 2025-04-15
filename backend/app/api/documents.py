from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import Document
from app.services.document_processor import process_document
from typing import List
import os
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    # Create unique filename
    file_path = UPLOAD_DIR / file.filename
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create document record
        document = Document(
            file_name=file.filename,
            file_type=file_ext,
            user_id="temp_user_id"  # Replace with actual user ID from auth
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Process document asynchronously
        await process_document(document.id, file_path)
        
        return {"message": "Document uploaded successfully", "document_id": document.id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document))
    documents = result.scalars().all()
    return documents 