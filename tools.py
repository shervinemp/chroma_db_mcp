import uuid
import logging

import database
import llm_utils
import config

from decorators import require_privilege, handle_errors_as_mcp

logger = logging.getLogger(__name__)


# --- Tool Logic Implementation ---


@handle_errors_as_mcp
def add_memory(
    text: str,
    doc_id: str | None = None,
    metadata: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> str:
    """
    Core logic for adding/updating a memory document.
    Returns doc_id on success. Raises McpError on failure.
    """
    logger.debug(f"Executing add_memory logic for collection '{collection_name}'")
    if not text:
        raise ValueError("Text content cannot be empty.")

    final_doc_id = doc_id if doc_id else uuid.uuid4().hex
    logger.debug(f"Using doc_id '{final_doc_id}'")

    memory_collection = database.get_collection(collection_name)
    embedding = llm_utils.generate_embedding(text, task_type="RETRIEVAL_DOCUMENT")

    final_metadata = {"original_text": text}
    if metadata:
        final_metadata.update(metadata)

    memory_collection.add(
        ids=[final_doc_id], embeddings=[embedding], metadatas=[final_metadata]
    )
    logger.info(
        f"Successfully added/updated document '{final_doc_id}' in '{collection_name}'."
    )
    return final_doc_id


@handle_errors_as_mcp
def recall_memory(
    query: str,
    top_k: int = 3,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> list[str]:
    """
    Core logic for recalling relevant memory documents.
    Returns list of texts on success. Raises McpError on failure.
    """
    logger.debug(f"Executing recall_memory logic for collection '{collection_name}'")
    if not query:
        raise ValueError("Query cannot be empty.")

    memory_collection = database.get_collection(collection_name)
    query_embedding = llm_utils.generate_embedding(query, task_type="RETRIEVAL_QUERY")

    results = memory_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filter,
        include=["metadatas"],
    )

    retrieved_texts = []
    if results and results.get("metadatas") and len(results["metadatas"]) > 0:
        for metadata_item in results["metadatas"][0]:
            if metadata_item and "original_text" in metadata_item:
                retrieved_texts.append(metadata_item["original_text"])

    logger.info(
        f"Retrieved {len(retrieved_texts)} relevant text chunks from '{collection_name}'."
    )
    return retrieved_texts


@handle_errors_as_mcp
def delete_memory(
    doc_id: str, collection_name: str = config.DEFAULT_COLLECTION_NAME
) -> bool:
    """
    Core logic for deleting a memory document.
    Returns True on success. Raises McpError on failure.
    """
    logger.debug(
        f"Executing delete_memory logic for doc_id '{doc_id}' in collection '{collection_name}'"
    )
    if not doc_id:
        raise ValueError("doc_id cannot be empty.")

    memory_collection = database.get_collection(collection_name)

    memory_collection.delete(ids=[doc_id])
    logger.info(f"Attempted deletion of document '{doc_id}' from '{collection_name}'.")
    return True


@handle_errors_as_mcp
def summarize_memory(
    query: str,
    top_k: int = 5,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> str:
    """
    Core logic for recalling and summarizing memories.
    Returns summary string on success, empty string if no context. Raises McpError on failure.
    """
    logger.debug(f"Executing summarize_memory logic for collection '{collection_name}'")
    if not query:
        raise ValueError("Query cannot be empty.")

    # Step 1: Recall relevant info (will raise exceptions on failure)
    retrieved_texts = recall_memory(
        query=query, top_k=top_k, filter=filter, collection_name=collection_name
    )

    if not retrieved_texts:
        logger.warning(
            f"No context found for summarization query in '{collection_name}'."
        )
        return ""  # Return empty string for no context

    # Step 2: Combine and Summarize (will raise exceptions on failure)
    combined_chunks = "\n---\n".join(retrieved_texts)
    summary = llm_utils.generate_summary(combined_chunks, query)

    logger.info(f"Generated summary for query in '{collection_name}'.")
    return summary


@handle_errors_as_mcp
def check_memory(
    topic: str,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> bool:
    """
    Core logic for checking memory existence.
    Returns True/False on success. Raises McpError on failure.
    """
    logger.debug(
        f"Executing check_memory logic for topic '{topic}' in collection '{collection_name}'"
    )
    if not topic:
        raise ValueError("Topic cannot be empty.")

    memory_collection = database.get_collection(collection_name)
    query_embedding = llm_utils.generate_embedding(topic, task_type="RETRIEVAL_QUERY")

    results = memory_collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        where=filter,
        include=[],
    )
    exists = bool(results and results.get("ids") and results["ids"][0])
    logger.info(
        f"Check memory result for topic '{topic}' in '{collection_name}': {exists}"
    )
    return exists


@handle_errors_as_mcp
def summarize_collection(collection_name: str, query: str = "") -> str:
    """
    Core logic for summarizing an entire collection. The query is optional.
    Returns summary string on success, empty string if no context. Raises McpError on failure.
    """
    logger.debug(
        f"Executing summarize_collection logic for collection '{collection_name}'"
    )
    if not collection_name:
        raise ValueError("Collection name cannot be empty.")

    # Step 1: Retrieve all documents from the collection
    memory_collection = database.get_collection(collection_name)
    results = memory_collection.get(include=["metadatas"])

    if not results or not results.get("metadatas"):
        logger.warning(
            f"No documents found in collection '{collection_name}' for summarization."
        )
        return ""

    retrieved_texts = []
    for metadata_item in results["metadatas"]:
        if metadata_item and "original_text" in metadata_item:
            retrieved_texts.append(metadata_item["original_text"])

    if not retrieved_texts:
        logger.warning(
            f"No text content found in collection '{collection_name}' for summarization."
        )
        return ""

    # Step 2: Combine and Summarize
    combined_chunks = "\\n---\\n".join(retrieved_texts)
    summary = llm_utils.generate_summary(combined_chunks, query)

    logger.info(f"Generated summary for collection '{collection_name}'.")
    return summary


@require_privilege
@handle_errors_as_mcp
def delete_collection(collection_name: str) -> bool:
    """
    Core logic for deleting an entire collection. Requires privilege.
    Returns True on success. Raises McpError on failure.
    """
    logger.debug(
        f"Executing delete_collection logic for collection '{collection_name}'"
    )
    if not collection_name:
        raise ValueError("Collection name cannot be empty.")

    database.chroma_client.delete_collection(name=collection_name)
    logger.info(f"Attempted deletion of collection '{collection_name}'.")
    return True
