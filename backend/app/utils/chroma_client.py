import chromadb
from app.config.chroma_config import get_chroma_client as config_get_client, get_or_create_collection as config_get_or_create_collection
from typing import Optional

_client: Optional[chromadb.PersistentClient] = None  # Use Optional and type hint

def get_chroma_client() -> chromadb.PersistentClient:
    """
    Get the ChromaDB client instance (singleton).
    """
    global _client
    if _client is None:
        _client = config_get_client()
    return _client

def get_or_create_collection(name: str, metadata: Optional[dict] = None) -> chromadb.Collection:
    """
    Get an existing collection or create a new one if it doesn't exist.
    """
    collection = config_get_or_create_collection(name=name)
    return collection