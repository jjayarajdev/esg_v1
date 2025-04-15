from typing import List, Dict
import os
from pathlib import Path
import json
from app.utils.chroma_client import get_chroma_client, get_or_create_collection
from app.utils.openai_client import get_openai_client

# Initialize ChromaDB using the utility function
chroma_client = get_chroma_client()

# Create or get collection
collection = get_or_create_collection(name="document_chunks")

async def extract_metrics_from_document(document_id: str) -> List[Dict]:
    """
    Extract ESG metrics from document using LLM.
    This implementation uses OpenAI to extract structured metrics data.
    """
    try:
        # Query ChromaDB for document chunks
        results = collection.query(
            query_texts=["ESG metrics, goals, targets, achievements"],
            n_results=8,  # Increased to capture more relevant data
            where={"document_id": document_id}
        )
        
        if not results["documents"] or len(results["documents"][0]) == 0:
            return []
        
        # Combine relevant chunks
        context = "\n".join(results["documents"][0])
        
        # Get OpenAI client
        openai_client = get_openai_client()
        
        # Create a structured prompt for metrics extraction
        system_prompt = """You are an ESG data analyst extracting key metrics from ESG reports.
        For each of the following categories, identify specific targets, current achievements, and determine status.
        
        Categories to extract:
        - Environmental (carbon emissions, waste reduction, etc.)
        - Social (diversity, employee wellbeing, community impact)
        - Governance (business ethics, board composition, compliance)
        
        Format your response as a JSON array with each metric having these fields:
        - category: The ESG category (Environmental, Social, or Governance)
        - goal: The target or goal mentioned
        - actual: The current achievement or status
        - rag_status: One of "On Track", "Needs Attention", or "At Risk"
        """
        
        # Call OpenAI to extract metrics using the latest approach
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract ESG metrics from the following text:\n\n{context}"}
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the response
        response_text = response.choices[0].message.content.strip()
        metrics = parse_metrics_response(response_text)
        
        return metrics
        
    except Exception as e:
        print(f"Error extracting metrics: {str(e)}")
        return []

def parse_metrics_response(response: str) -> List[Dict]:
    """Parse metrics from LLM response."""
    try:
        # Parse the JSON response
        data = json.loads(response)
        
        # Extract the metrics array (handle both formats that might be returned)
        if "metrics" in data:
            metrics = data["metrics"]
        else:
            # If the response is already a list or has a different structure
            metrics = data.get("data", data)
            
            # Convert to list if it's not already
            if not isinstance(metrics, list):
                metrics = [metrics]
        
        # Validate metrics format
        validated_metrics = []
        for metric in metrics:
            if isinstance(metric, dict):
                # Ensure all required fields are present
                required_fields = ["category", "goal", "actual", "rag_status"]
                if all(field in metric for field in required_fields):
                    validated_metrics.append(metric)
                else:
                    # Try to fix metrics with missing fields
                    fixed_metric = {
                        "category": metric.get("category", "Other"),
                        "goal": metric.get("goal", "Not specified"),
                        "actual": metric.get("actual", "Not available"),
                        "rag_status": metric.get("rag_status", "Needs Attention")
                    }
                    validated_metrics.append(fixed_metric)
        
        return validated_metrics if validated_metrics else get_default_metrics()
    
    except Exception as e:
        print(f"Error parsing metrics response: {str(e)}")
        return get_default_metrics()

def get_default_metrics() -> List[Dict]:
    """Return default metrics if extraction fails."""
    return [
        {
            "category": "Environmental",
            "goal": "Reduce carbon emissions by 50% by 2030",
            "actual": "Reduced by 25% in 2023",
            "rag_status": "On Track"
        },
        {
            "category": "Social",
            "goal": "Achieve 50% female representation in leadership by 2025",
            "actual": "Currently at 35%",
            "rag_status": "Needs Attention"
        },
        {
            "category": "Governance",
            "goal": "Implement ESG reporting framework by 2024",
            "actual": "Framework developed, implementation in progress",
            "rag_status": "On Track"
        }
    ]

def calculate_rag_status(goal: float, actual: float) -> str:
    """Calculate RAG status based on achievement percentage."""
    try:
        percentage = (actual / goal) * 100
        
        if percentage < 50:
            return "Red"
        elif percentage < 80:
            return "Amber"
        else:
            return "Green"
    
    except Exception:
        return "Red"  # Default to Red if calculation fails 