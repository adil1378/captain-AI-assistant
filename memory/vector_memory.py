"""
Captain AI OS — ChromaDB Semantic Vector Memory Module.
Provides persistent high-dimensional embeddings for semantic search,
long-term user fact recall, and contextual document retrieval.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

_CHROMA_DIR = Path("./data/chroma_db")


def _get_embedding_fn():
    """Get embedding function for ChromaDB (SentenceTransformer / HuggingFace fallback)."""
    try:
        from chromadb.utils import embedding_functions
        return embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    except Exception as e:
        logger.warning(f"ChromaDB embedding function load error ({e}). Using default.")
        return None


def _get_client():
    """Initialize persistent ChromaDB client."""
    import chromadb
    _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(_CHROMA_DIR))


def _get_collection(name: str = "captain_semantic_memory"):
    """Get or create a ChromaDB collection safely avoiding embedding function conflicts."""
    client = _get_client()
    embed_fn = _get_embedding_fn()
    if embed_fn:
        try:
            return client.get_or_create_collection(name=name, embedding_function=embed_fn)
        except Exception as e:
            logger.debug(f"ChromaDB collection load fallback ({e}). Accessing existing collection without explicit embed_fn.")
            return client.get_collection(name=name)
    return client.get_or_create_collection(name=name)


def should_store_semantic_memory(user_text: str) -> bool:
    """
    Selective Memory Storage Discipline Validator.
    Determines if a user turn is worthy of long-term ChromaDB vector memory indexing.
    Only stores explicit user preferences, facts, project decisions, and explicit 'remember' commands.
    Prevents storage of greetings, ordinary Q&A, weather, news, system metrics, and location queries.
    """
    if not user_text:
        return False

    q = user_text.lower().strip()
    words = q.split()

    # Rule 1: Reject short trivial turns (< 4 words) unless explicit command
    if len(words) < 4 and not any(k in q for k in ["remember", "prefer", "my name", "my stack"]):
        return False

    # Rule 2: Explicit DO NOT STORE patterns
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "how are you"]
    if any(q.startswith(g) for g in greetings) or q in greetings:
        return False

    ephemeral_topics = [
        "weather", "temperature", "forecast", "news", "system metrics",
        "cpu usage", "ram", "disk", "where is", "location of", "show on map",
        "what is python", "what is fastapi", "tell me about"
    ]
    if any(topic in q for topic in ephemeral_topics):
        return False

    # Rule 3: Explicit STORE patterns (High-value facts & preferences)
    high_value_triggers = [
        "remember", "prefer", "my name", "my project", "my email", "my stack",
        "our stack", "we decided", "note that", "store this", "always use",
        "never use", "i live in", "my location is"
    ]
    if any(trigger in q for trigger in high_value_triggers):
        return True

    return False


def store_semantic_memory(memory_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Store a text memory/fact into ChromaDB.

    Args:
        memory_id: Unique identifier for the memory chunk.
        text: The text content to embed.
        metadata: Key-value metadata dict (e.g. {'session_id': '1', 'type': 'fact'}).

    Returns:
        bool indicating success.
    """
    try:
        collection = _get_collection()
        meta = metadata or {}
        collection.upsert(
            ids=[memory_id],
            documents=[text],
            metadatas=[meta]
        )
        logger.debug(f"VectorMemory: Stored semantic memory '{memory_id}'")
        return True
    except Exception as e:
        logger.error(f"VectorMemory store error ({memory_id}): {e}")
        return False


from src.backend.config import settings


def query_semantic_memory(
    query: str,
    top_k: int = 3,
    filter_metadata: Optional[Dict[str, Any]] = None,
    distance_threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Search for semantically relevant memories matching the query, enforcing distance thresholding.

    Args:
        query: Search string query.
        top_k: Number of top matches to return.
        filter_metadata: Optional metadata filter dict.
        distance_threshold: Maximum allowed vector distance (defaults to settings.VECTOR_MEMORY_DISTANCE_THRESHOLD).

    Returns:
        List of dicts containing 'id', 'document', 'metadata', 'distance'.
    """
    threshold = distance_threshold if distance_threshold is not None else getattr(settings, "VECTOR_MEMORY_DISTANCE_THRESHOLD", 0.80)
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)
        kwargs: Dict[str, Any] = {
            "query_texts": [query],
            "n_results": actual_k
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = collection.query(**kwargs)
        formatted = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            ids = results["ids"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for i in range(len(docs)):
                dist = float(distances[i])
                logger.info(f"VectorMemory: Query '{query}' item '{ids[i]}' distance={dist:.4f} (threshold={threshold:.2f})")
                if dist <= threshold:
                    formatted.append({
                        "id": ids[i],
                        "document": docs[i],
                        "metadata": metas[i],
                        "distance": dist
                    })
                else:
                    logger.info(f"VectorMemory: Discarded item '{ids[i]}' with distance {dist:.4f} > {threshold:.2f}")

        logger.debug(f"VectorMemory: Query '{query}' returned {len(formatted)} relevant semantic matches.")
        return formatted
    except Exception as e:
        logger.error(f"VectorMemory query error for '{query}': {e}")
        return []


def clear_session_semantic_memory(session_id: str) -> bool:
    """Clear memories associated with a specific session without deleting global ChromaDB knowledge."""
    try:
        collection = _get_collection()
        collection.delete(where={"session_id": session_id})
        logger.info(f"VectorMemory: Cleared session-scoped semantic memory for '{session_id}'.")
        return True
    except Exception as e:
        logger.warning(f"VectorMemory session clear warning for '{session_id}': {e}")
        return False


def clear_semantic_memory() -> bool:
    """Clear all items in the semantic memory collection."""
    try:
        client = _get_client()
        client.delete_collection("captain_semantic_memory")
        logger.info("VectorMemory: Cleared all semantic memory.")
        return True
    except Exception as e:
        logger.error(f"VectorMemory clear error: {e}")
        return False
