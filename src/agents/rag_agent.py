from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.agents.state import AgentState
from src.agents.base_agent import BaseAgent, AgentMetadata
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from tools.rag_tools import query_rag
from utils.text_utils import clean_think_tags
from loguru import logger


class RagAgent(BaseAgent):
    """
    Production V2 RAG Agent.
    Retrieves relevant document contexts from the FAISS vectorstore
    and synthesizes answers using the configured LLM.
    """

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="rag_agent",
            description="Document Q&A and Retrieval-Augmented Generation Agent",
            version="2.0.0",
            capabilities=["rag", "document_qa", "pdf_search", "file_search"]
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        history = state.get("messages", [])
        scratchpad = state.get("scratchpad", {})

        # --- Retrieve relevant chunks from vectorstore ---
        rag_result = query_rag(user_query, top_k=4)
        context_text = ""

        if rag_result.get("status") == "success" and rag_result.get("results"):
            chunks = rag_result["results"]
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                source = chunk.get("source", "unknown")
                page = chunk.get("page")
                page_str = f" (page {page})" if page is not None else ""
                context_parts.append(
                    f"[Source {i}: {source}{page_str}]\n{chunk['content']}"
                )
            context_text = "\n\n".join(context_parts)
            logger.info(f"RagAgent: Retrieved {len(chunks)} relevant context chunks for query '{user_query}'")
        elif rag_result.get("status") == "no_relevant_docs":
            logger.warning(f"RagAgent: No document context passed relevance threshold for query '{user_query}'")
            return {
                "messages": [AIMessage(content="I don't have enough information in the provided documents to answer your question.")],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
        else:
            error_msg = rag_result.get("error", "No indexed documents found.")
            logger.warning(f"RagAgent: RAG lookup failed — {error_msg}")
            context_text = f"[No relevant documents found: {error_msg}]"

        # --- Build LLM prompt ---
        system_prompt = (
            "You are Captain RAG, an expert document analyst. "
            "Answer the user's question using ONLY the provided document context below. "
            "If the context does not contain enough information, say so clearly. "
            "Cite source references where appropriate. "
            "Format your answer in clear, structured markdown."
        )

        messages_to_send = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Document Context:\n\n{context_text}"),
        ]
        # Ensure active query is present as tail HumanMessage
        messages_to_send.extend(history)
        if not history or not (isinstance(history[-1], HumanMessage) and history[-1].content == user_query):
            messages_to_send.append(HumanMessage(content=user_query))

        llm = model_manager.get_model(
            model_name=settings.RAG_MODEL,
            temperature=0.2,
            max_tokens=2048
        )

        try:
            text_chunks = []
            async for chunk in llm.astream(messages_to_send):
                await self.check_pause()
                chunk_str = chunk.content if hasattr(chunk, "content") else str(chunk)
                text_chunks.append(chunk_str)

            raw_text = "".join(text_chunks)
            clean_text = clean_think_tags(raw_text)

            if not clean_text or len(clean_text) < 3:
                clean_text = context_text or "No relevant document context was found for your query."

            scratchpad["rag_context"] = context_text
            scratchpad["rag_output"] = clean_text

            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        except Exception as e:
            logger.error(f"RagAgent LLM error: {e}")
            fallback = context_text if context_text else f"RAG agent encountered an error: {e}"
            return {
                "messages": [AIMessage(content=fallback)],
                "error": str(e),
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
