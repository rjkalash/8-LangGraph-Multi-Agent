from graph.state import AgentState
from agents.llm_utils import get_llm

def summarize_node(state: AgentState) -> AgentState:
    print("---SUMMARIZE NODE---")
    query = state.original_query if state.original_query else state.query
    docs = state.reranked_docs
    
    if docs:
        context = "\n\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(docs)])
        prompt = f"""
        You are an expert assistant. Synthesize a final answer based ONLY on the provided context.
        If the context does not contain the complete answer, use the context to provide the best possible partial answer. 
        Only if the context is completely void of relevant info, say "I don't have enough information to answer that." 
        Do not make up facts outside the provided context, but be deeply analytical with what you have.
        
        Question: {query}
        
        Context:
        {context}
        """
    else:
         prompt = f"""
         Answer the user's question directly and concisely:
         Question: {query}
         """
    
    try:
        llm = get_llm()
        response = llm.invoke([{"role": "user", "content": prompt}])
        state.final_answer = response.content
        state.reasoning_trace.append("Summarizer: Generated final coherent answer.")
    except Exception as e:
         state.final_answer = "Sorry, I encountered an error generating the final answer."
         state.reasoning_trace.append(f"Summarizer Err: {e}")
         print(e)
         
    state.next_step = "end"
    return state
