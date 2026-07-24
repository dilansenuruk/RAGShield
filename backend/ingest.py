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

# the underscore tells other programmers: "This function is meant to be used only inside this module." <-- Python naming convention
# function_name(input_parameters: input_parameter_type) -> return_type:
def _read_file(path: str) -> str:
    # ext gets assigned the file extension (ex: .PDF, .txt, .md)
    # lower() --> ex: .PDF becomes .pdf
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f: # errors="ignore" <-- This prevents ingestion from crashing because of one bad character.
            return f.read()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            print(f"  ! skipping {path} (pip install pypdf to ingest PDFs)")
            return "" # if pypdf is not installed, it returns an empty string for .pdf files
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return "" # for .jpg, .png, .docx it returns an empty string


def ingest():
    collection = get_collection()

    # Fresh rebuild each run so re-ingesting never leaves stale chunks behind.
    # Now the database will not contains duplicates, Deleting first ensures the collection is rebuilt from scratch.
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    documents, metadatas, ids = [], [], []

    for dept in config.DEPARTMENTS:
        dept_dir = os.path.join(config.DATA_DIR, dept)
        # checks whether the directory actually exists.
        if not os.path.isdir(dept_dir):
            continue
        for path in glob.glob(os.path.join(dept_dir, "**", "*"), recursive=True):
            # glob returns both files and directories. We only want files. So, directories are skipped.
            if not os.path.isfile(path):
                continue
            text = _read_file(path)
            # if the file contains only spaces, tabs, or newlines, text.strip() becomes an empty string, and the file is skipped.
            if not text.strip():
                continue
            # converts an absolute path into a path relative to the data directory.
            # C:\Project\data\finance\salary.txt --> finance\salary.txt
            source = os.path.relpath(path, config.DATA_DIR)
            for i, chunk in enumerate(splitter.split_text(text)):
                documents.append(chunk)
                metadatas.append({"department": dept, "source": source})
                ids.append(f"{source}::{i}::{uuid.uuid4().hex[:8]}")
                # suppose, source = finance/salary.txt, i = 3, uuid = a7f3b2c19d...
                # the resulting id becomes: finance/salary.txt::3::a7f3b2c1

    # checks whether at least one chunk was collected.
    if documents:
        # adds the documents, metadatas, and ids to the collection in ChromaDB.
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    # ex: Ingested 54 chunks from 6 files into 'company_docs'.
    print(f"Ingested {len(documents)} chunks "
          f"from {len(set(m['source'] for m in metadatas))} files into "
          f"'{config.COLLECTION_NAME}'.")
    
    for dept in config.DEPARTMENTS:
        n = sum(1 for m in metadatas if m["department"] == dept)
        # this counts how many chunks belong to each department.
        print(f"  {dept:8s}: {n} chunks") # :8s <-- left-align the department name in a field of width 8 characters.


if __name__ == "__main__":
    ingest()
