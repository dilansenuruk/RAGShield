# Shared ChromaDB collection factory.
# Both ingestion and retrieval go through `get_collection()` so they always agree
# on the embedding model and the distance metric (cosine similarity).

import chromadb
from chromadb.utils import embedding_functions
from . import config


def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )


def get_collection(embedding_function=None):
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_function or get_embedding_function(),
        metadata={"hnsw:space": "cosine"},  # distance in [0, 2], lower = closer
    )
