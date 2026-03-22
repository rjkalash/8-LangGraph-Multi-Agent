from graph.state import AgentState
from agents.llm_utils import get_json_llm
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="Is the context relevant enough to answer the query?")
    reason: str = Field(description="Reason for validity or invalidity")
    hallucination: bool = Field(description="Does the context contradict itself or look totally made up?")

def validate_node(state: AgentState) -> AgentState:
    print("---VALIDATE NODE---")
    query = state.query
    docs = state.reranked_docs
    
    if not docs:
        state.reasoning_trace.append("Validator: No documents exist to validate.")
        state.is_valid_context = False
        if state.retry_count < state.max_retries:
            state.retry_count += 1
            state.next_step = "orchestrate"
        else:
            state.reasoning_trace.append("Validator: Max retries reached. Forcing generation on empty context.")
            state.next_step = "summarize"
        return state
        
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"""
    You are a validation agent. Evaluate if the provided context is relevant to the user query and is sufficient to answer it.
    Also check for obvious hallucinations in provided text.
    
    Query: {query}
    Context: {context}
    
    Respond EXACTLY in this JSON format:
    {{
        "is_valid": true or false,
        "reason": "Your detailed explanation for why the context is valid or invalid",
        "hallucination": true or false
    }}
    """
    
    try:
        llm = get_json_llm()
        response = llm.invoke([
            ("system", "You are a JSON-only evaluator. You must return ONLY valid JSON with keys 'is_valid', 'reason', and 'hallucination'."),
            ("user", prompt)
        ])
        
        # Parse JSON
        import json
        
        # Sometime Ollama prepends ```json or something, so safely clean it
        raw_json = response.content.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3]
        elif raw_json.startswith("```"):
            raw_json = raw_json[3:-3]
            
        result = json.loads(raw_json.strip())
        
        # Handle string "true"/"false" if LLM messes up boolean
        is_valid = result.get("is_valid", False)
        if isinstance(is_valid, str):
            is_valid = is_valid.lower() == "true"
            
        state.is_valid_context = is_valid
        state.hallucination_detected = result.get("hallucination", False)
        reason = result.get("reason") or result.get("Reason") or "No reason provided"
        
        state.reasoning_trace.append(f"Validator: Context valid={state.is_valid_context}. Reason: {reason}")
        
    except Exception as e:
        print(f"Validation err: {e}")
        # Default to True to allow progress if JSON parsing fails
        state.is_valid_context = True
        state.reasoning_trace.append("Validator: Failed to validate, proceeding anyway.")

    if not state.is_valid_context and state.retry_count < state.max_retries:
        state.retry_count += 1
        state.reasoning_trace.append(f"Validator: Context invalid. Retrying ({state.retry_count}/{state.max_retries}).")
        # In a real system you'd use a web search or expand query. Here we just loop back.
        state.next_step = "orchestrate"
    elif not state.is_valid_context:
         state.reasoning_trace.append(f"Validator: Max retries reached. Forcing generation.")
         state.next_step = "summarize"
    else:
        state.next_step = "summarize"
        
    return state
