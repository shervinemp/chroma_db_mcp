import os
import sys
import logging
import config
import google.generativeai as genai

logger = logging.getLogger(__name__)

# --- Gemini API Key Configuration ---
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    if not GEMINI_API_KEY:
        raise KeyError
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API Key configured.")
except KeyError:
    logger.error("GEMINI_API_KEY environment variable not set or empty.")
    sys.exit(1)

# --- Helper Functions ---


def generate_embedding(text: str, task_type: str) -> list[float]:
    """
    Generates text embedding using the configured Gemini model.
    """
    if not text or not isinstance(text, str):
        logger.error("Invalid text input for embedding.")
        raise ValueError("Invalid text provided for embedding.")

    valid_task_types = [
        "RETRIEVAL_DOCUMENT",
        "RETRIEVAL_QUERY",
        "SEMANTIC_SIMILARITY",
        "CLASSIFICATION",
        "CLUSTERING",
    ]
    if task_type not in valid_task_types:
        logger.warning(f"Unknown task_type '{task_type}'. Using default.")

    result = genai.embed_content(
        model=config.EMBEDDING_MODEL_NAME, content=text, task_type=task_type
    )
    embedding = result.get("embedding")
    if not embedding:
        logger.error(f"Gemini API did not return an embedding for task '{task_type}'.")
        raise RuntimeError(
            f"Gemini API failed to return embedding for task '{task_type}'."
        )
    return embedding


def generate_summary(context: str, query: str) -> str:
    """
    Generates a summary of the provided context using the Gemini generation model.
    """
    prompt = f"Concisely summarize the following text relevant to the query '{query}'. Respond ONLY with the precise summary itself, without any introductory or concluding phrases:\n\n---\n{context}\n---"
    logger.info(f"Generating summary for query: '{query[:60]}...'")

    model = genai.GenerativeModel(config.GENERATION_MODEL_NAME)
    response = model.generate_content(prompt)
    if response.parts:
        return response.text
    else:
        logger.warning("Gemini summary generation returned no content.")
        raise ValueError("Summary generation failed (empty response from model).")
