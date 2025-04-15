from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_DB_PATH = str(BASE_DIR / "chroma_data" / "chroma_db_new")

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def get_or_create_collection(name="document_chunks"):
    client = get_chroma_client()
    try:
        # Try to return existing collection
        return client.get_collection(name=name)
    except ValueError:  # ChromaDB raises ValueError when collection is not found
        # If not found, create a new one
        return client.create_collection(name=name)
