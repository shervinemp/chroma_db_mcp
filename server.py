#!/usr/bin/env python
import sys
import logging

from mcp.server.fastmcp import FastMCP
import tools
import decorators
import config

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# --- FastMCP Server Initialization ---
mcp = FastMCP("Chroma Memory Server")


# --- Register Tools ---


@mcp.tool()
def add_memory(
    text: str,
    doc_id: str | None = None,
    metadata: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> str:
    return tools.add_memory(text, doc_id, metadata, collection_name)


@mcp.tool()
def recall_memory(
    query: str,
    top_k: int = 1,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> list[str]:
    return tools.recall_memory(query, top_k, filter, collection_name)


@mcp.tool()
def delete_memory(
    doc_id: str, collection_name: str = config.DEFAULT_COLLECTION_NAME
) -> bool:
    return tools.delete_memory(doc_id, collection_name)


@mcp.tool()
def summarize_memory(
    query: str,
    top_k: int = 5,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> str:
    return tools.summarize_memory(query, top_k, filter, collection_name)


@mcp.tool()
def check_memory(
    topic: str,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> bool:
    return tools.check_memory(topic, filter, collection_name)


@mcp.tool()
def delete_collection(collection_name: str) -> bool:
    return tools.delete_collection(collection_name)


@mcp.tool()
def summarize_collection(collection_name: str, query: str = "") -> str:
    return tools.summarize_collection(collection_name, query)


@mcp.tool()
def update_memory_metadata(
    doc_id: str,
    metadata: dict,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> bool:
    return tools.update_memory_metadata(doc_id, metadata, collection_name)


@mcp.tool()
def get_memory_by_id(
    doc_id: str, collection_name: str = config.DEFAULT_COLLECTION_NAME
) -> str:
    return tools.get_memory_by_id(doc_id, collection_name)


@mcp.tool()
def list_collections() -> list[str]:
    return tools.list_collections()


@mcp.tool()
def recall_memory_with_distance(
    query: str,
    top_k: int = 1,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> list[tuple[str, float]]:
    return tools.recall_memory_with_distance(query, top_k, filter, collection_name)


@mcp.tool()
def recall_memory_hybrid(
    query: str,
    keyword: str = None,
    top_k: int = 1,
    filter: dict | None = None,
    collection_name: str = config.DEFAULT_COLLECTION_NAME,
) -> list[str]:
    return tools.recall_memory_hybrid(query, keyword, top_k, filter, collection_name)


@mcp.tool()
def grant_privilege() -> bool:
    """Grants temporary privilege for the next sensitive operation."""
    return decorators.grant_privilege()


# --- Run the server ---
if __name__ == "__main__":
    logger.info("Starting Chroma Memory MCP Server...")
    mcp.run()
