from graph.state import AgentState
from rag.reranker import DocumentReranker

def rerank_node(state: AgentState) -> AgentState:
    print("---RERANK NODE---")
    query = state.query
    docs = state.retrieved_docs
    
    if not docs:
        state.reasoning_trace.append("Reranker: No documents to rerank.")
        state.next_step = "validate"
        return state
        
    try:
        reranker = DocumentReranker()
        reranked = reranker.rerank(query, docs, top_k=3)
        state.reranked_docs = reranked
        state.reasoning_trace.append(f"Reranker: Selected top {len(reranked)} documents via Cross-Encoder.")
    except Exception as e:
        print(f"Reranking skipped/failed: {e}")
        state.reranked_docs = docs[:3] # fallback
        state.reasoning_trace.append(f"Reranker: Fallback to top 3 retrieved documents.")
        
    state.next_step = "validate"
    return state
