# Shared ChromaDB collection factory.
# Both ingestion and retrieval go through `get_collection()` so they always agree
# on the embedding model and the distance metric (cosine similarity).

import chromadb
from chromadb.utils import embedding_functions
from . import config

# this function returns the embedding function
def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL)

# An embedding function converts text into numbers.
# Example: "The elephant is running."
# [0.12, 0.84, -0.19, ... 384 values] <-- all-MiniLM-L6-v2
# [0.12, -0.43, 0.82, ... 768 values] <-- all-mpnet-base-v2


def get_collection(embedding_function=None):
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_function or get_embedding_function(), # if enbedding_function is NONE, then it is false.
        metadata={"hnsw:space": "cosine"},  # distance in [0, 2], lower = closer
    )

# "cosine" - Compares the angle between vectors - for sentence embeddings (most common)
# "l2" - Euclidean distance - for raw numeric vectors
# "ip" - Inner product (dot product) - for some embedding models

# Cosine similarity focuses entirely on the direction (the angle) of the vectors, completely ignoring their magnitude (length)