import os
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
from config import settings


def get_embeddings():
    """Returns local Ollama embeddings (nomic-embed-text-v2-moe:latest) or HuggingFace fallback."""
    try:
        from langchain_ollama import OllamaEmbeddings
        logger.info(f"Loading Ollama Embeddings model: {settings.ollama_embed_model}")
        return OllamaEmbeddings(base_url=settings.ollama_base_url, model=settings.ollama_embed_model)
    except Exception as e:
        logger.warning(f"OllamaEmbeddings failed ({e}), trying HuggingFaceEmbeddings fallback.")
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def ingest_document(file_path: str) -> Dict[str, Any]:
    """Load a document (PDF, TXT, DOCX, MD) and index into FAISS vectorstore."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {"status": "error", "error": f"File not found: {file_path}"}

        ext = path.suffix.lower()
        docs = []

        if ext == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(str(path))
            docs = loader.load()
        elif ext in [".txt", ".md"]:
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(str(path), encoding="utf-8")
            docs = loader.load()
        elif ext == ".docx":
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(str(path))
            docs = loader.load()
        else:
            return {"status": "error", "error": f"Unsupported file type: {ext}"}

        if not docs:
            return {"status": "error", "error": f"No content extracted from {file_path}"}

        from langchain.text_splitter import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = text_splitter.split_documents(docs)

        embeddings = get_embeddings()
        from langchain_community.vectorstores import FAISS

        index_path = settings.vectorstore_dir / "faiss_index"

        if index_path.exists():
            vectorstore = FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)
            vectorstore.add_documents(chunks)
        else:
            vectorstore = FAISS.from_documents(chunks, embeddings)

        vectorstore.save_local(str(index_path))

        logger.info(f"Indexed {len(chunks)} chunks from {path.name} into FAISS vectorstore.")
        return {"status": "success", "file": path.name, "chunks_indexed": len(chunks)}

    except Exception as e:
        logger.error(f"Error indexing document {file_path}: {e}")
        return {"status": "error", "error": str(e)}


def query_rag(query: str, top_k: int = 4, score_threshold: float = None) -> Dict[str, Any]:
    """Retrieve relevant document contexts from vectorstore for a query with distance thresholding."""
    try:
        index_path = settings.vectorstore_dir / "faiss_index"
        if not index_path.exists():
            return {"status": "error", "error": "No indexed documents found. Please ingest documents first."}

        if score_threshold is None:
            score_threshold = getattr(settings, "RAG_RELEVANCE_THRESHOLD", 1.25)

        embeddings = get_embeddings()
        from langchain_community.vectorstores import FAISS
        vectorstore = FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)

        docs_and_scores = vectorstore.similarity_search_with_score(query, k=top_k)
        contexts = []
        for d, score in docs_and_scores:
            logger.info(f"RAG Chunk Score for query '{query}': {score:.4f} (Threshold: {score_threshold})")
            if score <= score_threshold:
                contexts.append({
                    "content": d.page_content,
                    "source": d.metadata.get("source", "unknown"),
                    "page": d.metadata.get("page", None),
                    "relevance_score": float(score)
                })
            else:
                logger.warning(f"RAG Chunk EXCLUDED (score {score:.4f} > threshold {score_threshold}): {d.page_content[:60]}...")

        if not contexts:
            return {"status": "no_relevant_docs", "query": query, "results": [], "message": "No documents met the relevance distance threshold."}

        return {"status": "success", "query": query, "results": contexts}

    except Exception as e:
        logger.error(f"RAG search error for '{query}': {e}")
        return {"status": "error", "error": str(e)}


def rag_search_tool(query: str, top_k: int = 4) -> Dict[str, Any]:
    """Alias for query_rag for backward compatibility."""
    return query_rag(query, top_k=top_k)
