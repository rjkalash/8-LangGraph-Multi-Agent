from graph.state import AgentState
from langchain_core.documents import Document
from langchain_community.tools import DuckDuckGoSearchRun

def search_node(state: AgentState) -> AgentState:
    print("---WEB SEARCH NODE---")
    query = state.query
    state.reasoning_trace.append(f"Web Search Agent: Searching internet for '{query}'...")
    
    try:
        search = DuckDuckGoSearchRun()
        result = search.invoke(query)
        
        # Wrap the raw string result into a Document object
        doc = Document(
            page_content=result,
            metadata={"source": "DuckDuckGo Web Search", "query": query}
        )
        
        # We append directly to reranked_docs so it goes straight to validation/summarization
        # Or we can put it in retrieved_docs and let the Reranker process it alongside internal DB docs
        # Since it's usually highly relevant, we'll put it directly into retrieved_docs to be reranked.
        state.retrieved_docs.append(doc)
        
        # If it's pure web string, we might just bypass retrieval entirely if we want
        # Let's say web search REPLACES retrieval for this flow:
        state.reranked_docs = [doc]
        state.reasoning_trace.append(f"Web Search Agent: Retrieved live results.")
        
    except Exception as e:
        state.reasoning_trace.append(f"Web Search Agent: Search failed ({str(e)}).")
        print(f"Web search error: {e}")
        
    state.next_step = "validate" # Go straight to validation
    return state
