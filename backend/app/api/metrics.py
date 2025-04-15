from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import ESGMetric
from app.services.metrics_service import extract_metrics_from_document
from typing import List
from pydantic import BaseModel
from sqlalchemy import select

router = APIRouter()

class ESGMetricCreate(BaseModel):
    category: str
    goal: str
    actual: str
    rag_status: str

@router.post("/extract/{document_id}")
async def extract_metrics(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Extract ESG metrics from document using LLM."""
    try:
        metrics = await extract_metrics_from_document(document_id)
        
        # Store metrics in database
        for metric in metrics:
            db_metric = ESGMetric(
                document_id=document_id,
                category=metric["category"],
                goal=metric["goal"],
                actual=metric["actual"],
                rag_status=metric["rag_status"],
                extracted_by="LLM"
            )
            db.add(db_metric)
        
        await db.commit()
        return {"message": "Metrics extracted successfully", "metrics": metrics}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_metrics(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get ESG metrics for a document."""
    try:
        result = await db.execute(
            select(ESGMetric)
            .where(ESGMetric.document_id == document_id)
        )
        metrics = result.scalars().all()
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}")
async def create_metric(
    document_id: str,
    metric: ESGMetricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Manually create an ESG metric."""
    try:
        db_metric = ESGMetric(
            document_id=document_id,
            category=metric.category,
            goal=metric.goal,
            actual=metric.actual,
            rag_status=metric.rag_status,
            extracted_by="Manual"
        )
        db.add(db_metric)
        await db.commit()
        await db.refresh(db_metric)
        return db_metric
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{metric_id}")
async def update_metric(
    metric_id: str,
    metric: ESGMetricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update an ESG metric."""
    try:
        db_metric = await db.get(ESGMetric, metric_id)
        if not db_metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        db_metric.category = metric.category
        db_metric.goal = metric.goal
        db_metric.actual = metric.actual
        db_metric.rag_status = metric.rag_status
        
        await db.commit()
        await db.refresh(db_metric)
        return db_metric
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 