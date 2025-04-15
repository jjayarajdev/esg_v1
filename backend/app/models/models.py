from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Text, UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)

class QAInteraction(Base):
    __tablename__ = "qa_interactions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)
    validated = Column(Boolean, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ESGMetric(Base):
    __tablename__ = "esg_metrics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    category = Column(String, nullable=False)
    goal = Column(Text, nullable=True)
    actual = Column(Text, nullable=True)
    rag_status = Column(String, nullable=True)
    extracted_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 