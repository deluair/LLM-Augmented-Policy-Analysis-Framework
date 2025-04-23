# src/data_pipeline/datastore/vector_database.py

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from src.config import settings # Import your project settings
from src.utils.exceptions import RetrievalError, ConfigurationError

logger = logging.getLogger(__name__)

class VectorDatabaseManager:
    """Manages interactions with the vector database (ChromaDB)."""

    def __init__(self, collection_name: str = "policy_documents", embedding_model_name: Optional[str] = None):
        """Initializes the VectorDatabaseManager.

        Args:
            collection_name (str): Name of the ChromaDB collection to use.
            embedding_model_name (Optional[str]): Name or path of the Sentence Transformer model. 
                                                 Defaults to the one in project settings.
        """
        self.collection_name = collection_name
        
        # Determine embedding model
        _model_name = embedding_model_name or settings.models.embedding_model_name
        if not _model_name:
             raise ConfigurationError(message="Embedding model name not configured in settings.")
        self.embedding_model_name = _model_name

        try:
            logger.info(f"Loading sentence transformer model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("Sentence transformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model '{self.embedding_model_name}': {e}")
            raise ConfigurationError(message=f"Failed to load embedding model: {e}")

        # Configure ChromaDB client
        # Example: Persistent storage in a directory
        # Adjust path as needed, potentially using settings.database.vector_db_path
        db_path = "./chroma_db" # Make this configurable via settings if preferred
        logger.info(f"Initializing ChromaDB client with persistent path: {db_path}")
        try:
             # Using persistent client
             self.client = chromadb.PersistentClient(path=db_path)
             # Or use in-memory client for testing:
             # self.client = chromadb.Client() 
             
             # Get or create the collection
             logger.info(f"Getting or creating ChromaDB collection: {self.collection_name}")
             # You might need to specify the embedding function if not using default
             # See ChromaDB docs for custom embedding functions if needed
             self.collection = self.client.get_or_create_collection(name=self.collection_name)
             logger.info(f"Connected to ChromaDB collection '{self.collection_name}'.")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise ConfigurationError(message=f"ChromaDB initialization failed: {e}")

    def add_documents(self, documents: List[Dict[str, Any]], text_key: str = "cleaned_text", id_key: str = "url"):
        """Adds or updates documents in the vector database.

        Args:
            documents (List[Dict[str, Any]]): List of documents (dictionaries).
            text_key (str): The key in each document dict that holds the text to embed.
            id_key (str): The key in each document dict to use as the unique ID.
        """
        if not documents:
            logger.warning("No documents provided to add.")
            return

        ids = []
        texts_to_embed = []
        metadatas = []

        for doc in documents:
            doc_id = doc.get(id_key)
            text = doc.get(text_key)

            if not doc_id or not text:
                logger.warning(f"Skipping document due to missing ID ('{id_key}') or text ('{text_key}'): {doc}")
                continue
            
            ids.append(str(doc_id)) # Chroma IDs must be strings
            texts_to_embed.append(text)
            
            # Prepare metadata (only string, int, float, bool allowed by Chroma)
            metadata = {k: v for k, v in doc.items() if k not in [text_key, id_key] and isinstance(v, (str, int, float, bool))}
            # Convert other types like lists/sets (e.g., tags) to strings if needed
            if 'tags' in doc and isinstance(doc['tags'], (list, set)):
                 metadata['tags'] = ",".join(sorted(list(doc['tags']))) 
            metadatas.append(metadata)

        if not ids:
             logger.warning("No valid documents found to add after filtering.")
             return

        try:
            logger.info(f"Generating embeddings for {len(texts_to_embed)} documents...")
            embeddings = self.embedding_model.encode(texts_to_embed, show_progress_bar=True).tolist()
            logger.info("Embeddings generated.")

            logger.info(f"Adding/updating {len(ids)} documents in collection '{self.collection_name}'...")
            # Use upsert to add new or update existing documents based on ID
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts_to_embed, # Store the text itself if desired
                metadatas=metadatas
            )
            logger.info(f"Successfully added/updated {len(ids)} documents.")

        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            # Don't raise ConfigurationError here, it's a runtime/retrieval issue
            # Consider a more specific exception if needed
            raise RetrievalError(f"Failed to add documents to vector store: {e}")

    def search(self, query_text: str, n_results: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Searches the vector database for documents similar to the query text.

        Args:
            query_text (str): The text to search for.
            n_results (int): The maximum number of results to return.
            filter_metadata (Optional[Dict[str, Any]]): Metadata filter to apply (ChromaDB format).

        Returns:
            List[Dict[str, Any]]: A list of search results, including documents, metadatas, and distances.
        """
        try:
            logger.info(f"Generating query embedding for: '{query_text[:100]}...'")
            query_embedding = self.embedding_model.encode([query_text]).tolist()
            logger.info("Query embedding generated.")

            logger.info(f"Searching collection '{self.collection_name}' for {n_results} results...")
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=filter_metadata, # Pass the filter dictionary directly
                include=['metadatas', 'documents', 'distances'] # Specify what to include
            )
            logger.info(f"Search completed. Found {len(results.get('ids', [[]])[0])} results.")

            # Reformat results into a more usable list of dictionaries
            formatted_results = []
            ids = results.get('ids', [[]])[0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            documents = results.get('documents', [[]])[0]

            for i, doc_id in enumerate(ids):
                 formatted_results.append({
                      "id": doc_id,
                      "distance": distances[i],
                      "metadata": metadatas[i],
                      "document": documents[i] 
                 })
            
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            raise RetrievalError(f"Vector search failed: {e}")


# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(log_level='INFO')
#
#     # Assuming you have settings configured (.env file)
#     try:
#         db_manager = VectorDatabaseManager(collection_name="test_policies")
#
#         # Sample docs (replace with actual processed docs)
#         docs_to_add = [
#             {'url': 'doc1', 'cleaned_text': 'Federal reserve raises interest rates.', 'publication_date': '2023-01-01', 'tags': {'interest_rates', 'inflation'}},
#             {'url': 'doc2', 'cleaned_text': 'Unemployment rate decreases slightly.', 'publication_date': '2023-02-15', 'tags': {'unemployment', 'labor_market'}},
#             {'url': 'doc3', 'cleaned_text': 'New policy focuses on controlling inflation.', 'publication_date': '2023-03-10', 'tags': {'inflation', 'policy'}}
#         ]
#         db_manager.add_documents(docs_to_add)
#
#         # Search example
#         search_query = "What is the latest news on inflation?"
#         search_results = db_manager.search(query_text=search_query, n_results=2)
#
#         print(f"\\n--- Search Results for '{search_query}' ---")
#         for result in search_results:
#             print(f"  ID: {result['id']}, Distance: {result['distance']:.4f}")
#             print(f"  Metadata: {result['metadata']}")
#             print(f"  Text: {result['document'][:100]}...")
#             print("-" * 10)
#
#         # Search with filter
#         filter_query = "interest rates"
#         metadata_filter = {"tags": {"$contains": "inflation"}} # Example Chroma filter: find docs tagged with 'inflation'
#         print(f"\\n--- Filtered Search for '{filter_query}' (tag=inflation) ---")
#         filtered_results = db_manager.search(query_text=filter_query, n_results=2, filter_metadata=metadata_filter)
#         for result in filtered_results:
#             print(f"  ID: {result['id']}, Distance: {result['distance']:.4f}")
#             print(f"  Metadata: {result['metadata']}")
#             print(f"  Text: {result['document'][:100]}...")
#             print("-" * 10)
#
#     except ConfigurationError as e:
#         logger.critical(f"Configuration error: {e}")
#     except RetrievalError as e:
#         logger.critical(f"Datastore operation failed: {e}")

