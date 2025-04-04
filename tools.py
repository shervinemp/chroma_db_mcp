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
    top_k: int = 1,
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


@handle_errors_as_mcp
def update_memory_metadata(
    doc_id: str,
    metadata: dict,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> bool:
    """
    Core logic for updating the metadata of a memory document.
    Returns True on success. Raises McpError on failure.
    """
    logger.debug(
        f"Executing update_memory_metadata logic for doc_id '{doc_id}' in collection '{collection_name}'"
    )
    if not doc_id:
        raise ValueError("doc_id cannot be empty.")
    if not metadata or not isinstance(metadata, dict):
        raise ValueError("Metadata must be a non-empty dictionary.")

    memory_collection = database.get_collection(collection_name)
    # Fetch the existing document to preserve the embedding
    results = memory_collection.get(ids=[doc_id], include=["embeddings"])
    if not results or not results["embeddings"] or not results["embeddings"][0]:
        raise ValueError(
            f"Document with id '{doc_id}' not found in collection '{collection_name}'."
        )

    embedding = results["embeddings"][0]

    # Update the metadata
    memory_collection.update(
        ids=[doc_id],
        metadatas=[metadata],
        embeddings=[embedding],  # embeddings must be passed during update
    )

    logger.info(
        f"Successfully updated metadata for document '{doc_id}' in '{collection_name}'."
    )
    return True


@handle_errors_as_mcp
def get_memory_by_id(
    doc_id: str, collection_name: str = config.DEFAULT_COLLECTION_NAME
) -> str:
    """
    Core logic for retrieving a memory document by its ID.
    Returns the document's text content on success, empty string if not found.
    """
    logger.debug(
        f"Executing get_memory_by_id logic for doc_id '{doc_id}' in collection '{collection_name}'"
    )
    if not doc_id:
        raise ValueError("doc_id cannot be empty.")

    memory_collection = database.get_collection(collection_name)
    results = memory_collection.get(
        ids=[doc_id], include=["metadatas"]
    )  # Only fetch metadata

    if not results or not results["metadatas"] or not results["metadatas"][0]:
        logger.warning(
            f"Document with id '{doc_id}' not found in collection '{collection_name}'."
        )
        return ""  # Return empty string if not found

    metadata = results["metadatas"][0][0]  # Access the first document's metadata
    if metadata and "original_text" in metadata:
        return metadata["original_text"]
    else:
        logger.warning(
            f"No text content found for document '{doc_id}' in collection '{collection_name}'."
        )
        return ""  # Return empty string if no text content


@require_privilege
@handle_errors_as_mcp
def list_collections() -> list[str]:
    """
    Core logic for listing all collections in ChromaDB.
    Returns a list of collection names.
    """
    logger.debug("Executing list_collections logic")
    return database.chroma_client.list_collections()


@handle_errors_as_mcp
def recall_memory_with_distance(
    query: str,
    top_k: int = 1,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> list[tuple[str, float]]:
    """
    Core logic for recalling relevant memory documents and their distances.
    Returns a list of tuples, where each tuple contains the text and the distance.
    """
    logger.debug(
        f"Executing recall_memory_with_distance logic for collection '{collection_name}'"
    )
    if not query:
        raise ValueError("Query cannot be empty.")

    memory_collection = database.get_collection(collection_name)
    query_embedding = llm_utils.generate_embedding(query, task_type="RETRIEVAL_QUERY")

    results = memory_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filter,
        include=["metadatas", "distances"],
    )

    retrieved_texts = []
    if (
        results
        and results.get("metadatas")
        and results.get("distances")
        and len(results["metadatas"]) > 0
    ):
        for i, metadata_item in enumerate(results["metadatas"][0]):
            if metadata_item and "original_text" in metadata_item:
                text = metadata_item["original_text"]
                distance = results["distances"][0][i]
                retrieved_texts.append((text, distance))

    logger.info(
        f"Retrieved {len(retrieved_texts)} relevant text chunks from '{collection_name}'."
    )
    return retrieved_texts


@handle_errors_as_mcp
def recall_memory_hybrid(
    query: str,
    keyword: str = None,
    top_k: int = 1,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> list[str]:
    """
    Core logic for recalling relevant memory documents using hybrid search (vector + keyword).
    Returns a list of texts.
    """
    logger.debug(
        f"Executing recall_memory_hybrid logic for collection '{collection_name}'"
    )
    if not query:
        raise ValueError("Query cannot be empty.")

    memory_collection = database.get_collection(collection_name)
    query_embedding = llm_utils.generate_embedding(query, task_type="RETRIEVAL_QUERY")

    # Basic hybrid search (can be improved with more sophisticated techniques)
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
                text = metadata_item["original_text"]
                if (
                    keyword is None or keyword.lower() in text.lower()
                ):  # Basic keyword filter
                    retrieved_texts.append(text)

    logger.info(
        f"Retrieved {len(retrieved_texts)} relevant text chunks from '{collection_name}'."
    )
    return retrieved_texts


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


@handle_errors_as_mcp
def list_collection_ids(collection_name: str) -> list[str]:
    """
    Core logic for listing all document IDs in a collection.
    Returns a list of document IDs.
    """
    logger.debug(
        f"Executing list_collection_ids logic for collection '{collection_name}'"
    )
    if not collection_name:
        raise ValueError("Collection name cannot be empty.")

    memory_collection = database.get_collection(collection_name)
    results = memory_collection.get(include=[])

    if not results or not results.get("ids"):
        logger.warning(f"No documents found in collection '{collection_name}'.")
        return []

    ids = results["ids"]
    logger.info(f"Retrieved {len(ids)} document IDs from '{collection_name}'.")
    return ids
