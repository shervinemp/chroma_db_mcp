# Configuration constants for the MCP Chroma Memory Server

# Gemini Models
EMBEDDING_MODEL_NAME = "models/embedding-001"
# Using the specific experimental model identifier provided by the user
GENERATION_MODEL_NAME = "gemini-2.5-pro-exp-03-25"

# ChromaDB Settings
DEFAULT_COLLECTION_NAME = "agent_memory"
DB_SUBDIR = "chroma_db_data"  # Subdirectory within the project for DB persistence
