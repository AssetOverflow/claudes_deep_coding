"""ChromaDB manager for vector database operations."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class ChromaMemoryManager:
    """Manages ChromaDB vector database for long-term memory and RAG."""

    def __init__(
        self,
        persist_directory: Optional[Path] = None,
        collection_name: str = "deepagents_memory",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Initialize ChromaDB manager.

        Args:
            persist_directory: Directory to persist ChromaDB data (for local mode)
            collection_name: Name of the collection to use
            host: ChromaDB server host (for client/server mode)
            port: ChromaDB server port (for client/server mode)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Determine if we're using client/server or local mode
        if host and port:
            logger.info(f"Connecting to ChromaDB server at {host}:{port}")
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            # Local persistent mode
            if persist_directory:
                persist_directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Using local ChromaDB at {persist_directory}")
                self.client = chromadb.PersistentClient(
                    path=str(persist_directory),
                    settings=Settings(anonymized_telemetry=False),
                )
            else:
                # In-memory mode (for testing)
                logger.info("Using in-memory ChromaDB")
                self.client = chromadb.Client(
                    settings=Settings(anonymized_telemetry=False)
                )

        # Use default embedding function (sentence transformers)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Memory storage for deepagents coding tasks"},
        )

        logger.info(f"ChromaDB collection '{collection_name}' ready")

    def add_memory(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the memory store.

        Args:
            documents: List of text documents to store
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document (will be auto-generated if not provided)
        """
        if not documents:
            logger.warning("No documents provided to add_memory")
            return

        # Auto-generate IDs if not provided
        if ids is None:
            import uuid

            ids = [str(uuid.uuid4()) for _ in documents]

        # Ensure metadatas exist
        if metadatas is None:
            metadatas = [{} for _ in documents]

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Added {len(documents)} documents to memory")
        except Exception as e:
            logger.error(f"Error adding documents to memory: {e}")
            raise

    def query_memory(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the memory store for relevant documents.

        Args:
            query_texts: List of query strings
            n_results: Number of results to return per query
            where: Metadata filter
            where_document: Document content filter

        Returns:
            Query results containing documents, distances, and metadata
        """
        try:
            results = self.collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )
            logger.info(f"Query returned {len(results.get('ids', [[]])[0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying memory: {e}")
            raise

    def get_memory_by_id(self, ids: List[str]) -> Dict[str, Any]:
        """
        Retrieve specific memories by their IDs.

        Args:
            ids: List of document IDs to retrieve

        Returns:
            Documents and their metadata
        """
        try:
            results = self.collection.get(ids=ids)
            logger.info(f"Retrieved {len(results.get('ids', []))} documents by ID")
            return results
        except Exception as e:
            logger.error(f"Error retrieving memories by ID: {e}")
            raise

    def update_memory(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Update existing memories.

        Args:
            ids: IDs of documents to update
            documents: New document content (optional)
            metadatas: New metadata (optional)
        """
        try:
            self.collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"Updated {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error updating memories: {e}")
            raise

    def delete_memory(self, ids: List[str]) -> None:
        """
        Delete memories by their IDs.

        Args:
            ids: IDs of documents to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting memories: {e}")
            raise

    def count(self) -> int:
        """
        Get the total number of documents in the collection.

        Returns:
            Number of documents
        """
        return self.collection.count()

    def clear(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Memory storage for deepagents coding tasks"},
            )
            logger.info(f"Cleared collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
