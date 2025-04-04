# Chroma Memory MCP Server

This project implements an MCP server that provides tools for managing a ChromaDB instance.

## Overview

The Chroma Memory MCP Server provides a set of tools for interacting with a ChromaDB instance, allowing you to store, retrieve, and manage memories. It leverages the Model Context Protocol (MCP) to expose these functionalities as tools that can be used by other applications or agents.

## Tools

The following tools are implemented:

* `add_memory`: Adds a memory to the ChromaDB.
  * **Description:** This tool allows you to add a new memory to the ChromaDB. You can specify the text content of the memory, a document ID, and any metadata associated with the memory.
  * **Parameters:**
    * `text` (str, required): The text content of the memory.
    * `doc_id` (str, optional): A unique identifier for the memory document. If not provided, a UUID will be generated.
    * `metadata` (dict, optional): A dictionary containing metadata associated with the memory.
    * `collection_name` (str, optional): The name of the collection to add the memory to. Defaults to `agent_memory`.
  * **Example Usage:**

        ```json
        {
          "tool_name": "add_memory",
          "arguments": {
            "text": "This is a test memory.",
            "doc_id": "test_memory",
            "metadata": {
              "author": "Cline",
              "date": "2024-04-03"
            }
          }
        }
        ```

* `recall_memory`: Recalls memories from the ChromaDB.
  * **Description:** This tool allows you to retrieve memories from the ChromaDB that are relevant to a given query.
  * **Parameters:**
    * `query` (str, required): The query to use for retrieving memories.
    * `top_k` (int, optional): The number of memories to retrieve. Defaults to 3.
    * `filter` (dict, optional): A dictionary containing filters to apply to the memory retrieval.
    * `collection_name` (str, optional): The name of the collection to retrieve memories from. Defaults to `agent_memory`.
  * **Example Usage:**

        ```json
        {
          "tool_name": "recall_memory",
          "arguments": {
            "query": "test memory",
            "top_k": 5
          }
        }
        ```

* `delete_memory`: Deletes a memory from the ChromaDB.
  * **Description:** This tool allows you to delete a specific memory from the ChromaDB.
  * **Parameters:**
    * `doc_id` (str, required): The unique identifier of the memory document to delete.
    * `collection_name` (str, optional): The name of the collection to delete the memory from. Defaults to `agent_memory`.
  * **Example Usage:**

        ```json
        {
          "tool_name": "delete_memory",
          "arguments": {
            "doc_id": "test_memory"
          }
        }
        ```

* `summarize_memory`: Summarizes memories from the ChromaDB.
  * **Description:** This tool allows you to retrieve and summarize memories from the ChromaDB that are relevant to a given query.
  * **Parameters:**
    * `query` (str, required): The query to use for retrieving and summarizing memories.
    * `top_k` (int, optional): The number of memories to retrieve. Defaults to 5.
    * `filter` (dict, optional): A dictionary containing filters to apply to the memory retrieval.
    * `collection_name` (str, optional): The name of the collection to retrieve memories from. Defaults to `agent_memory`.
  * **Example Usage:**

        ```json
        {
          "tool_name": "summarize_memory",
          "arguments": {
            "query": "test memory",
            "top_k": 3
          }
        }
        ```

* `check_memory`: Checks if a memory exists in the ChromaDB.
  * **Description:** This tool allows you to check if a memory exists in the ChromaDB that is relevant to a given topic.
  * **Parameters:**
    * `topic` (str, required): The topic to use for checking memory existence.
    * `filter` (dict, optional): A dictionary containing filters to apply to the memory retrieval.
    * `collection_name` (str, optional): The name of the collection to check memories in. Defaults to `agent_memory`.
  * **Example Usage:**

        ```json
        {
          "tool_name": "check_memory",
          "arguments": {
            "topic": "test memory"
          }
        }
        ```

* `delete_collection`: Deletes a collection from the ChromaDB.
  * **Description:** This tool allows you to delete an entire collection from the ChromaDB. This operation requires privilege.
  * **Parameters:**
    * `collection_name` (str, required): The name of the collection to delete.
  * **Example Usage:**

        ```json
        {
          "tool_name": "delete_collection",
          "arguments": {
            "collection_name": "agent_memory"
          }
        }
        ```

* `summarize_collection`: Summarizes a collection in the ChromaDB.
  * **Description:** This tool allows you to summarize an entire collection in the ChromaDB.
  * **Parameters:**
    * `collection_name` (str, required): The name of the collection to summarize.
    * `query` (str, optional): A query to focus the summarization.
    * **Example Usage:**

        ```json
        {
          "tool_name": "summarize_collection",
          "arguments": {
            "collection_name": "agent_memory",
            "query": "test"
          }
        }
        ```

* `update_memory_metadata`: Updates the metadata of a memory document.
  * **Description:** This tool allows you to update the metadata of a specific memory document in the ChromaDB.
  * **Parameters:**
    * `doc_id` (str, required): The unique identifier of the memory document to update.
    * `metadata` (dict, required): A dictionary containing the new metadata for the memory document.
    * `collection_name` (str, optional): The name of the collection containing the memory document. Defaults to `agent_memory`.
    * **Example Usage:**

        ```json
        {
          "tool_name": "update_memory_metadata",
          "arguments": {
            "doc_id": "test_memory",
            "metadata": {
              "author": "New Author"
            }
          }
        }
        ```

* `get_memory_by_id`: Retrieves a memory document by its ID.
  * **Description:** This tool allows you to retrieve a specific memory document from the ChromaDB by its ID.
  * **Parameters:**
    * `doc_id` (str, required): The unique identifier of the memory document to retrieve.
    * `collection_name` (str, optional): The name of the collection containing the memory document. Defaults to `agent_memory`.
    * **Example Usage:**

        ```json
        {
          "tool_name": "get_memory_by_id",
          "arguments": {
            "doc_id": "test_memory"
          }
        }
        ```

* `list_collections`: Lists all collections in the ChromaDB.
  * **Description:** This tool allows you to list all the collections in the ChromaDB.
  * **Parameters:** None
  * **Example Usage:**
        ```json
        {
          "tool_name": "list_collections",
          "arguments": {}
        }
        ```
* `recall_memory_with_distance`: Recalls memories and their distances from the query.
  * **Description:** This tool allows you to retrieve memories from the ChromaDB that are relevant to a given query, and also returns the distance of each memory from the query vector.
  * **Parameters:**
        *`query` (str, required): The query to use for retrieving memories.
        *   `top_k` (int, optional): The number of memories to retrieve. Defaults to 3.
        *`filter` (dict, optional): A dictionary containing filters to apply to the memory retrieval.
        *   `collection_name` (str, optional): The name of the collection to retrieve memories from. Defaults to `agent_memory`.
    * **Example Usage:**
        ```json
        {
          "tool_name": "recall_memory_with_distance",
          "arguments": {
            "query": "test",
            "top_k": 3
          }
        }
        ```
* `recall_memory_hybrid`: Recalls memories using hybrid search (vector + keyword).
  * **Description:** This tool allows you to retrieve memories from the ChromaDB that are relevant to a given query, using a hybrid search approach that combines vector search with keyword search.
  * **Parameters:**
    * `query` (str, required): The query to use for retrieving memories.
    * `keyword` (str, optional): A keyword to filter the memories by.
    * `top_k` (int, optional): The number of memories to retrieve. Defaults to 3.
    * `filter` (dict, optional): A dictionary containing filters to apply to the memory retrieval.
    * `collection_name` (str, optional): The name of the collection to retrieve memories from. Defaults to `agent_memory`.
    * **Example Usage:**

        ```json
        {
          "tool_name": "recall_memory_hybrid",
          "arguments": {
            "query": "test",
            "keyword": "memory",
            "top_k": 3
          }
        }
        ```

## Setup

1. Install the dependencies: `pip install -r requirements.txt`
2. Configure the Gemini API key by setting the `GEMINI_API_KEY` environment variable.
3. Run the server: `python server.py`

## Architecture

The Chroma Memory MCP Server is built using the following components:

* **ChromaDB:** A persistent vector database used for storing and retrieving memories.
* **Model Context Protocol (MCP):** A protocol for exposing functionalities as tools that can be used by other applications or agents.
* **Google Gemini Models:** Used for generating text embeddings and summaries.
* **FastMCP:** A library for building MCP servers.

## Dependencies

The project has the following dependencies:

* `chromadb`
* `google-generativeai`
* `fastmcp`
