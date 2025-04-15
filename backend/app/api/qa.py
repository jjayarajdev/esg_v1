from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import QAInteraction
from app.services.qa_service import get_answer_from_llm
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import select

router = APIRouter()

class QuestionRequest(BaseModel):
    document_id: str
    question: str

class ValidationRequest(BaseModel):
    interaction_id: str
    is_valid: bool

@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get answer from LLM
        answer, citations = await get_answer_from_llm(
            request.document_id,
            request.question
        )
        
        # Store interaction
        interaction = QAInteraction(
            user_id="temp_user_id",  # Replace with actual user ID from auth
            document_id=request.document_id,
            question=request.question,
            answer=answer,
            citations=citations
        )
        
        db.add(interaction)
        await db.commit()
        await db.refresh(interaction)
        
        # Ensure we have consistent field names for the frontend
        return {
            "id": interaction.id,
            "interaction_id": interaction.id, # For backward compatibility
            "question": interaction.question,
            "answer": interaction.answer,
            "citations": citations or [], # Ensure citations is always at least an empty array
            "validated": interaction.validated,
            "created_at": interaction.created_at.isoformat() if interaction.created_at else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_answer(
    request: ValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get interaction
        interaction = await db.get(QAInteraction, request.interaction_id)
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        # Update validation status
        interaction.validated = request.is_valid
        await db.commit()
        
        return {"message": "Validation recorded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{document_id}")
async def get_chat_history(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(QAInteraction)
            .where(QAInteraction.document_id == document_id)
            .order_by(QAInteraction.created_at)
        )
        interactions = result.scalars().all()
        
        # Format the response to ensure consistent structure for frontend
        formatted_interactions = []
        for interaction in interactions:
            formatted_interactions.append({
                "id": interaction.id,
                "question": interaction.question,
                "answer": interaction.answer,
                "citations": interaction.citations or [],
                "validated": interaction.validated,
                "created_at": interaction.created_at.isoformat() if interaction.created_at else None
            })
        
        return formatted_interactions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 