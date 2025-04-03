import os
import sys
import logging
import chromadb
import config
from decorators import handle_errors_as_mcp

logger = logging.getLogger(__name__)

# --- ChromaDB Client Initialization ---
try:
    db_directory = os.path.join(os.path.dirname(__file__), config.DB_SUBDIR)
    chroma_client = chromadb.PersistentClient(path=db_directory)
    logger.info(f"ChromaDB client initialized. Data directory: {db_directory}")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB client: {e}")
    sys.exit(1)


# --- Helper Functions ---


@handle_errors_as_mcp
def get_collection(collection_name: str = config.DEFAULT_COLLECTION_NAME):
    """
    Gets or creates a ChromaDB collection by name.
    """
    return chroma_client.get_or_create_collection(name=collection_name)
