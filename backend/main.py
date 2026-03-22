from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid
from typing import Dict, Any

from graph.workflow import build_graph
from graph.state import AgentState

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LangGraph Multi-Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for demonstration purposes
queries_db: Dict[str, dict] = {}
history_db: Dict[str, list] = {}

class QueryRequest(BaseModel):
    user_id: str
    query: str
    use_web_search: bool = False

class QueryResponse(BaseModel):
    query_id: str
    status: str

def run_workflow(query_id: str, query: str, user_id: str, use_web_search: bool):
    import time
    start_time = time.time()
    graph = build_graph()
    state = AgentState(query=query, use_web_search=use_web_search)
    queries_db[query_id]["trace"] = []
    
    try:
        final_state_obj = None
        for event in graph.stream(state):
            node_name = list(event.keys())[0]
            node_state = event[node_name]
            final_state_obj = node_state
            
            # Pydantic vs dict handling depending on LangGraph version
            if hasattr(node_state, "reasoning_trace"):
                queries_db[query_id]["trace"] = node_state.reasoning_trace
            elif isinstance(node_state, dict) and "reasoning_trace" in node_state:
                queries_db[query_id]["trace"] = node_state["reasoning_trace"]

        queries_db[query_id]["status"] = "completed"
        
        # Helper to extract from final_state safely
        def get_val(state_obj, key, default):
            if hasattr(state_obj, key): return getattr(state_obj, key)
            if isinstance(state_obj, dict): return state_obj.get(key, default)
            return default
            
        queries_db[query_id]["result"] = {
            "final_answer": get_val(final_state_obj, "final_answer", None),
            "reasoning_trace": get_val(final_state_obj, "reasoning_trace", []),
            "retrieved_docs_count": len(get_val(final_state_obj, "retrieved_docs", [])),
            "reranked_docs_count": len(get_val(final_state_obj, "reranked_docs", [])),
            "hallucination_detected": get_val(final_state_obj, "hallucination_detected", False),
            "retries": get_val(final_state_obj, "retry_count", 0),
            "time_taken": round(time.time() - start_time, 2)
        }
    except Exception as e:
        queries_db[query_id]["status"] = "failed"
        queries_db[query_id]["error"] = str(e)
        print(f"Workflow error: {e}")
        
    # Append to history
    if user_id not in history_db:
        history_db[user_id] = []
    
    history_db[user_id].append({
        "query_id": query_id,
        "query": query,
        "answer": queries_db[query_id].get("result", {}).get("final_answer", None),
        "trace": queries_db[query_id].get("result", {}).get("reasoning_trace", [])
    })

@app.post("/query", response_model=QueryResponse)
async def submit_query(req: QueryRequest, background_tasks: BackgroundTasks):
    query_id = str(uuid.uuid4())
    queries_db[query_id] = {"status": "processing", "query": req.query, "user_id": req.user_id}
    
    # Run langgraph workflow in background
    background_tasks.add_task(run_workflow, query_id, req.query, req.user_id, req.use_web_search)
    
    return QueryResponse(query_id=query_id, status="processing")

@app.get("/status/{query_id}")
async def get_status(query_id: str):
    data = queries_db.get(query_id)
    if not data:
        return {"error": "Not found"}
    return data

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    return {"user_id": user_id, "history": history_db.get(user_id, [])}
