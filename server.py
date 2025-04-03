#!/usr/bin/env python
import sys
import logging

from mcp.server.fastmcp import FastMCP
import tools
import decorators

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
    collection_name: str = "agent_memory",
) -> str:
    return tools.add_memory(text, doc_id, metadata, collection_name)


@mcp.tool()
def recall_memory(
    query: str,
    top_k: int = 3,
    filter: dict | None = None,
    collection_name: str = "agent_memory",
) -> list[str]:
    return tools.recall_memory(query, top_k, filter, collection_name)


@mcp.tool()
def delete_memory(doc_id: str, collection_name: str = "agent_memory") -> bool:
    return tools.delete_memory(doc_id, collection_name)


@mcp.tool()
def summarize_memory(
    query: str,
    top_k: int = 5,
    filter: dict | None = None,
    collection_name: str = "agent_memory",
) -> str:
    return tools.summarize_memory(query, top_k, filter, collection_name)


@mcp.tool()
def check_memory(
    topic: str, filter: dict | None = None, collection_name: str = "agent_memory"
) -> bool:
    return tools.check_memory(topic, filter, collection_name)


@mcp.tool()
def delete_collection(collection_name: str) -> bool:
    return tools.delete_collection(collection_name)


@mcp.tool()
def summarize_collection(collection_name: str, query: str = "") -> str:
    return tools.summarize_collection(collection_name, query)


@mcp.tool()
def grant_privilege() -> bool:
    """Grants temporary privilege for the next sensitive operation."""
    return decorators.grant_privilege()


# --- Run the server ---
if __name__ == "__main__":
    logger.info("Starting Chroma Memory MCP Server...")
    mcp.run()
