from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from app.config import settings
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Initialize embedding model
try:
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    EMBEDDING_DIM = model.get_sentence_embedding_dimension()
    logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL} with dimension: {EMBEDDING_DIM}")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise

# Initialize Qdrant client
try:
    client = QdrantClient(url=settings.QDRANT_URL, timeout=30)
    logger.info(f"Connected to Qdrant at {settings.QDRANT_URL}")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    raise

# Create collection if it doesn't exist
try:
    collection_info = client.get_collection(settings.QDRANT_COLLECTION)
    logger.info(f"Collection {settings.QDRANT_COLLECTION} already exists")
except Exception:
    try:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created collection {settings.QDRANT_COLLECTION} with dimension {EMBEDDING_DIM}")
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        raise

def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using the sentence transformer model
    """
    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

def upsert_tool(tool_id: int, name: str, description: str, tags: List[str]) -> bool:
    """
    Upsert tool embedding into vector database
    """
    try:
        # Combine text for embedding
        text = f"{name} {description} {' '.join(tags)}"
        embedding = get_embedding(text)
        
        point = PointStruct(
            id=tool_id,
            vector=embedding,
            payload={
                "name": name,
                "description": description,
                "tags": tags,
                "tool_id": tool_id
            }
        )
        
        operation_info = client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[point],
            wait=True
        )
        
        logger.info(f"Upserted tool {tool_id} to vector database: {operation_info}")
        return True
    except Exception as e:
        logger.error(f"Error upserting tool to vector database: {e}")
        return False

def search_tools(query: str, limit: int = 10) -> List[dict]:
    """
    Search for tools using semantic similarity
    """
    try:
        query_embedding = get_embedding(query)
        
        search_result = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True,
            score_threshold=0.3  # Minimum similarity threshold
        )
        
        results = []
        for result in search_result:
            results.append({
                "id": result.payload["tool_id"],
                "name": result.payload["name"],
                "description": result.payload["description"],
                "tags": result.payload.get("tags", []),
                "score": result.score
            })
        
        logger.info(f"Semantic search for '{query}' returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error searching tools: {e}")
        return []

def delete_tool(tool_id: int) -> bool:
    """
    Delete tool from vector database
    """
    try:
        operation_info = client.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=[tool_id]
        )
        
        logger.info(f"Deleted tool {tool_id} from vector database: {operation_info}")
        return True
    except Exception as e:
        logger.error(f"Error deleting tool from vector database: {e}")
        return False