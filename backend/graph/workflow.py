from langgraph.graph import StateGraph, END
from graph.state import AgentState

from agents.orchestrator import orchestrator_node
from agents.retriever import retrieve_node
from agents.reranker import rerank_node
from agents.validator import validate_node
from agents.summarizer import summarize_node
from agents.search_agent import search_node

def route_orchestrator(state: AgentState) -> str:
    return state.next_step

def route_validator(state: AgentState) -> str:
    return state.next_step

def build_graph():
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("validate", validate_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("search_web", search_node)
    
    # Set entry point
    graph.set_entry_point("orchestrator")
    
    # Add edges
    graph.add_conditional_edges(
        "orchestrator",
        route_orchestrator,
        {
            "retrieve": "retrieve",
            "search_web": "search_web",
            "summarize": "summarize"
        }
    )
    
    # Linear edges
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "validate")
    graph.add_edge("search_web", "validate")
    
    # Conditional edge from validate
    graph.add_conditional_edges(
        "validate",
        route_validator,
        {
            "orchestrate": "orchestrator", # loop back
            "summarize": "summarize"
        }
    )
    
    graph.add_edge("summarize", END)
    
    # Compile
    return graph.compile()
