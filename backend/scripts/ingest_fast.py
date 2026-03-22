import os
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rag.vectorstore import get_vectorstore
from scripts.ingest import load_sample_docs

def ingest_fast():
    print("Ingesting ONLY sample_docs.md for fast update...")
    docs = load_sample_docs()
    
    print(f"Loaded {len(docs)} documents.")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = text_splitter.split_documents(docs)
    
    # Clean metadatas
    for i, split in enumerate(splits):
        split.metadata["id"] = f"fast_{i}"
        safe_meta = {}
        for k, v in split.metadata.items():
             if isinstance(v, (str, int, float, bool)):
                 safe_meta[k] = v
             else:
                 safe_meta[k] = str(v)
        split.metadata = safe_meta
        
    vectorstore = get_vectorstore()
    print(f"Adding {len(splits)} chunks to ChromaDB...")
    vectorstore.add_documents(documents=splits)
    print("Ingestion complete! You can now query your sample_docs.md data!")

if __name__ == "__main__":
    ingest_fast()
