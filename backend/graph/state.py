from typing import List, Optional, Any
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    query: str
    original_query: Optional[str] = None
    use_web_search: bool = False
    
    # Store fetched documents
    retrieved_docs: List[Any] = Field(default_factory=list)
    reranked_docs: List[Any] = Field(default_factory=list)
    
    # Validation status
    is_valid_context: bool = False
    hallucination_detected: bool = False
    
    # Retry and loop control
    retry_count: int = 0
    max_retries: int = 3
    
    # Answer generation
    final_answer: Optional[str] = None
    reasoning_trace: List[str] = Field(default_factory=list)
    
    # Next step routing
    next_step: Optional[str] = None
