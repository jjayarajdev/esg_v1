import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global client
_client = None

def get_openai_client():
    """
    Get the OpenAI client instance (singleton).
    This function handles initialization errors and provides consistent
    access to the OpenAI client across the application.
    """
    global _client
    
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            # Dynamic import to avoid potential initialization issues
            from openai import OpenAI
            logger.info("Initializing OpenAI client with API key")
            _client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise
    
    return _client 