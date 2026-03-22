from typing import List
from langchain_core.documents import Document
from .vectorstore import get_vectorstore
from langchain_community.retrievers import BM25Retriever

class HybridRetriever:
    def __init__(self, vectorstore, k=5):
        self.vectorstore = vectorstore
        self.k = k
        self.bm25_retriever = None
        self._initialize_bm25()

    def _initialize_bm25(self):
        try:
            # We fetch all documents from chroma to initialize BM25
            docs = self.vectorstore.get()
            if docs and len(docs["documents"]) > 0:
                documents = [Document(page_content=doc, metadata=meta) for doc, meta in zip(docs["documents"], docs["metadatas"])]
                self.bm25_retriever = BM25Retriever.from_documents(documents)
                self.bm25_retriever.k = self.k
        except Exception as e:
            print(f"BM25 initialization skipped: {e}")

    def add_documents(self, documents: List[Document]):
        self.vectorstore.add_documents(documents)
        # Re-initialize BM25 on new data
        self._initialize_bm25()

    def get_relevant_documents(self, query: str) -> List[Document]:
        # 1. Vector Search
        vector_docs = self.vectorstore.similarity_search(query, k=self.k)
        
        # 2. Keyword Search
        keyword_docs = []
        if self.bm25_retriever:
            keyword_docs = self.bm25_retriever.invoke(query)
            
        # Combine and deduplicate
        all_docs = []
        seen = set()
        for doc in vector_docs + keyword_docs:
            doc_id = doc.metadata.get("id", doc.page_content[:50])
            if doc_id not in seen:
                all_docs.append(doc)
                seen.add(doc_id)
                
        return all_docs
