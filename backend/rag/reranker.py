from typing import List
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

class DocumentReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.encoder = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: List[Document], top_k: int = 3) -> List[Document]:
        if not documents:
            return []
            
        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.encoder.predict(pairs)
        
        # Combine docs and scores
        doc_scores = list(zip(documents, scores))
        # Sort by score descending
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k
        return [doc for doc, score in doc_scores[:top_k]]
