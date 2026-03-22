from graph.state import AgentState
from agents.llm_utils import get_llm
from pydantic import BaseModel, Field

class Plan(BaseModel):
    action: str = Field(description="Must be 'retrieve', 'answer_directly', or 'need_clarification'.")
    revised_query: str = Field(description="A potentially refined query optimized for search if action is 'retrieve'.")

def orchestrator_node(state: AgentState) -> AgentState:
    print("---ORCHESTRATOR NODE---")
    query = state.query
    
    if state.retry_count > 0:
        # If we are retrying, we might need a modified query
        prompt = f"""
        The previous retrieval attempts failed to find good context. 
        Original Query: {query}
        Please provide a new refined search query, picking new keywords or synonyms.
        Output JSON with 'revised_query' and action 'retrieve'.
        """
        try:
            from agents.llm_utils import get_json_llm
            import json
            llm = get_json_llm()
            res = llm.invoke([{"role": "user", "content": prompt}])
            result = json.loads(res.content)
            
            state.query = result.get("revised_query", query)
            state.reasoning_trace.append(f"Orchestrator (Retry): Refined query to '{state.query}'")
            state.next_step = "search_web" if state.use_web_search else "retrieve"
        except Exception as e:
             state.reasoning_trace.append(f"Orchestrator (Retry): Failed to refine. Retrying original.")
             state.next_step = "search_web" if state.use_web_search else "retrieve"
    else:
        # First time planner
        prompt = f"""
        Given the user query, determine if you need to retrieve documents to answer it.
        If it's a casual greeting, action=answer_directly. If fact-based or domain-specific, action=retrieve.
        Query: {query}
        Output JSON formatted to matches this schema: {Plan.model_json_schema()}
        """
        try:
            from agents.llm_utils import get_json_llm
            import json
            llm = get_json_llm()
            res = llm.invoke([{"role": "user", "content": prompt}])
            result = json.loads(res.content)
            
            action = result.get("action", "retrieve")
            state.original_query = state.query
            
            if state.use_web_search:
                state.query = result.get("revised_query", query)
                state.reasoning_trace.append(f"Orchestrator: Web Search is ON. Delegating to Live Search Agent for '{state.query}'.")
                state.next_step = "search_web"
            elif action == "retrieve":
                state.query = result.get("revised_query", query)
                state.reasoning_trace.append(f"Orchestrator: Planning to retrieve internal documents for '{state.query}'.")
                state.next_step = "retrieve"
            else:
                state.reasoning_trace.append(f"Orchestrator: Decided to answer directly without retrieval.")
                state.next_step = "summarize"
                
        except Exception as e:
            state.reasoning_trace.append("Orchestrator: Failed to plan intelligently, defaulting to retrieve.")
            state.next_step = "retrieve"
            
    return state
