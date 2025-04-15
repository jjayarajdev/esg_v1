import fitz  # PyMuPDF
from docx import Document as DocxDocument
from pathlib import Path
import asyncio
from typing import List, Dict, Optional
import json
import os
from app.database import get_db
from app.models.models import Document
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.chroma_client import get_chroma_client, get_or_create_collection
from app.utils.openai_client import get_openai_client

# Initialize ChromaDB using the utility function
chroma_client = get_chroma_client()

# Create or get collection
collection = get_or_create_collection(name="document_chunks")

async def process_document(document_id: str, file_path: Path):
    """
    Process the uploaded document and extract text content.
    Steps:
    1. Extract text from document
    2. Chunk the text into smaller pieces
    3. Create OpenAI embeddings and store chunks in ChromaDB
    4. Update document status
    """
    try:
        # Get file extension
        file_ext = file_path.suffix.lower()
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            text = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Generate embeddings and store chunks in ChromaDB
        await store_chunks_with_embeddings(document_id, chunks)
        
        # Update document status in database
        async for db in get_db():
            document = await db.get(Document, document_id)
            if document:
                document.processed = True
                await db.commit()
                
        print(f"Document {document_id} processed and stored in ChromaDB with {len(chunks)} chunks")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        raise

def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF file using PyMuPDF."""
    doc = fitz.open(str(file_path))
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from DOCX file using python-docx."""
    doc = DocxDocument(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of approximately equal size."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

async def store_chunks_with_embeddings(document_id: str, chunks: List[str]) -> None:
    """
    Generate OpenAI embeddings and store text chunks in ChromaDB with metadata.
    """
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
    
    # Generate embeddings using OpenAI
    try:
        # Get OpenAI client from centralized utility
        openai_client = get_openai_client()
        embeddings = []
        # Process chunks in batches to avoid rate limits
        batch_size = 20
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            # Using the latest OpenAI API approach
            response = openai_client.embeddings.create(
                model="text-embedding-ada-002", 
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            
        # Add chunks to collection with embeddings
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"Successfully stored {len(chunks)} chunks with OpenAI embeddings")
    
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        raise

# Keep the original store_chunks as fallback
async def store_chunks(document_id: str, chunks: List[str]) -> None:
    """Store text chunks in ChromaDB with metadata (without custom embeddings)."""
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
    
    # Add chunks to collection
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )

async def update_document_status(document_id: str, processed: bool) -> None:
    """Update document processing status in database."""
    # This will be implemented when we have the database setup
    pass 