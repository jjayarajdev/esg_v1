import os
from typing import Tuple, List, Dict, Optional
import json
import re
from pathlib import Path
from app.utils.chroma_client import get_chroma_client, get_or_create_collection
from app.utils.openai_client import get_openai_client

# Initialize ChromaDB using the utility function
chroma_client = get_chroma_client()

# Create or get collection
collection = get_or_create_collection(name="document_chunks")

async def get_answer_from_llm(document_id: str, question: str) -> Tuple[str, Optional[List[Dict]]]:
    """
    Get answer from OpenAI's LLM based on document content and question.
    Uses Retrieval Augmented Generation (RAG) with ChromaDB and OpenAI.
    Handles ESG report generation with specific formatting for tables.
    """
    try:
        openai_client = get_openai_client()
        
        # First, create embedding for the question using the latest approach
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=question
        )
        question_embedding = embedding_response.data[0].embedding
        
        # Query ChromaDB for relevant chunks using embedding
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=5,  # Increased for ESG report generation
            where={"document_id": document_id}
        )
        
        # If no results with embeddings, fallback to text query
        if not results["documents"] or len(results["documents"][0]) == 0:
            results = collection.query(
                query_texts=[question],
                n_results=5,  # Increased for ESG report generation
                where={"document_id": document_id}
            )
        
        if not results["documents"] or len(results["documents"][0]) == 0:
            return "I couldn't find any relevant information in the document to answer your question.", []
        
        # Combine relevant chunks for context
        context = "\n".join(results["documents"][0])
        
        # Check if this is an ESG report generation query
        is_esg_report_query = is_esg_report_generation_query(question)
        
        if is_esg_report_query:
            # Use specialized prompt for ESG report generation
            system_prompt = """You are an ESG report specialist tasked with generating a structured report from document content.

Objective: Carefully analyze the provided ESG document to identify specific targets, achievements, and trends for each of the 13 categories listed below. Fill in the table with the extracted information, ensuring that all categories are addressed.

Instructions:
1. Carefully read the data, focusing on sections that discuss the following categories:
   - Sustainable Materials
   - Water
   - Energy
   - Waste & Effluent
   - Land Use/Animal Stewardship
   - GHG Emissions
   - Transportation
   - Design & Operation
   - Supply Chain Compliance
   - Health & Wellbeing
   - Inclusion
   - Social Responsibility
   - Stakeholder Engagement

2. Assess Trends:
   Evaluate and record the trend for each category as IMPROVED, SAME, or WORSENED.

3. Compile Data into a Structured Markdown Table:
   Organize the information into the required table format with columns for Category, Target/Goal, Achievement, and Trend.

4. Verification:
   Cross-check the information for accuracy against the document content provided.

5. Do not leave any category empty. If information is not available for a category, indicate "No data available" in the corresponding cells.

6. Format the table as a standard markdown table that will render properly on all platforms.
"""
            
            # Call OpenAI with specialized prompt for ESG report using the latest approach
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Document content:\n{context}\n\nGenerate a comprehensive ESG report using the information from this document, following the format in the instructions."}
                ],
                temperature=0.2,
                max_tokens=2000  # Increased for longer table responses
            )
        else:
            # Regular question answering prompt
            system_prompt = """You are an AI assistant for question answering on ESG (Environmental, Social, and Governance) documents. 
            Use the provided document excerpts to answer the user's question. 
            If the answer cannot be found in the excerpts, say "I don't have enough information to answer this question."
            Provide specific answers with direct references to the document where possible."""
            
            # Call OpenAI to generate answer using the latest approach
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # Or gpt-3.5-turbo depending on your needs
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Document excerpts:\n{context}\n\nQuestion: {question}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
        
        # Extract answer
        answer = response.choices[0].message.content.strip()
        
        # Format citations
        citations = []
        for i, (text, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            citations.append({
                "text": text,
                "chunk_index": metadata.get("chunk_index", i)
            })
        
        return answer, citations
        
    except Exception as e:
        print(f"Error getting answer from LLM: {str(e)}")
        return f"Sorry, I couldn't process your question at this time. Error: {str(e)}", []

def is_esg_report_generation_query(question: str) -> bool:
    """
    Determine if a question is asking for ESG report generation.
    Looks for keywords and phrases related to ESG reporting.
    """
    # Convert to lowercase for case-insensitive matching
    q_lower = question.lower()
    
    # Check for ESG report generation indicators
    report_keywords = [
        "esg report", 
        "sustainability report", 
        "generate table", 
        "create table", 
        "categories",
        "sustainable materials",
        "water",
        "energy",
        "waste",
        "ghg emissions"
    ]
    
    # Check if the query mentions multiple ESG categories
    categories_count = sum(1 for keyword in [
        "sustainable materials", "water", "energy", "waste", "land use", 
        "ghg emissions", "transportation", "design", "supply chain",
        "health", "inclusion", "social responsibility", "stakeholder"
    ] if keyword in q_lower)
    
    # Return true if multiple report keywords or categories are found
    return any(keyword in q_lower for keyword in report_keywords) or categories_count >= 3

def format_citations(citations: List[Dict]) -> List[Dict]:
    """Format citations for frontend display."""
    return [
        {
            "text": citation["text"],
            "chunk_index": citation["chunk_index"],
            "highlight": True
        }
        for citation in citations
    ] 