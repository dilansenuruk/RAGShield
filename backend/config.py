# Central configuration and the RBAC access map.
# Everything tunable lives here so the rest of the code stays clean.

import os
from dotenv import load_dotenv

load_dotenv()

# ------- Groq -------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# ------- Paths -------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(BASE_DIR, "chroma_db"))
COLLECTION_NAME = "company_docs"

# ------- Embeddings -------
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # local, CPU-friendly

# ------- RBAC -------
DEPARTMENTS = ["finance", "hr", "general"]