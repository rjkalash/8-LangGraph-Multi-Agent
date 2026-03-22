from graph.state import AgentState
from rag.retriever import HybridRetriever
from rag.vectorstore import get_vectorstore

def retrieve_node(state: AgentState) -> AgentState:
    print("---RETRIEVE NODE---")
    query = state.query
    
    # Initialize retriever
    vectorstore = get_vectorstore()
    retriever = HybridRetriever(vectorstore)
    
    # Get documents
    docs = retriever.get_relevant_documents(query)
    
    # Update state
    state.retrieved_docs = docs
    state.reasoning_trace.append(f"Retriever: Found {len(docs)} documents using Hybrid Search.")
    state.next_step = "rerank"
    
    return state
