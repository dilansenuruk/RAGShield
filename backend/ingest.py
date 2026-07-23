# Data Ingestion Pipeline.

# The directory layout under data/ defines access control:

#     data/finance/...   -> department = "finance"
#     data/hr/...        -> department = "hr"
#     data/general/...   -> department = "general"

# Each chunk is stored with metadata {"department": <folder>, "source": <file>}.
# That single scalar `department` field is what the RBAC retrieval filter uses.

import glob
import os
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from . import config
from .embeddings import get_collection


def _read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            print(f"  ! skipping {path} (pip install pypdf to ingest PDFs)")
            return ""
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return ""


def ingest():
    collection = get_collection()

    # Fresh rebuild each run so re-ingesting never leaves stale chunks behind.
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    documents, metadatas, ids = [], [], []

    for dept in config.DEPARTMENTS:
        dept_dir = os.path.join(config.DATA_DIR, dept)
        if not os.path.isdir(dept_dir):
            continue
        for path in glob.glob(os.path.join(dept_dir, "**", "*"), recursive=True):
            if not os.path.isfile(path):
                continue
            text = _read_file(path)
            if not text.strip():
                continue
            source = os.path.relpath(path, config.DATA_DIR)
            for i, chunk in enumerate(splitter.split_text(text)):
                documents.append(chunk)
                metadatas.append({"department": dept, "source": source})
                ids.append(f"{source}::{i}::{uuid.uuid4().hex[:8]}")

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Ingested {len(documents)} chunks "
          f"from {len(set(m['source'] for m in metadatas))} files into "
          f"'{config.COLLECTION_NAME}'.")
    for dept in config.DEPARTMENTS:
        n = sum(1 for m in metadatas if m["department"] == dept)
        print(f"  {dept:8s}: {n} chunks")


if __name__ == "__main__":
    ingest()
