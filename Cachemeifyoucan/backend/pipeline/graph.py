from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import (
    retrieve_node,
    generate_answer_node,
    causal_autopsy_node,
    fake_chain_node,
    epistemic_judge_node,
    refusal_node,
    tool_node
)
from .conditional import (
    route_retrieval,
    route_epistemic_judge,
    route_audit_agent
)

def increment_retry_node(state: GraphState):
    return {"retry_count": state.get("retry_count", 0) + 1}

def build_graph():
    workflow = StateGraph(GraphState)
    
    # Define Nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("audit_agent", causal_autopsy_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("fake_chain", fake_chain_node)
    workflow.add_node("epistemic_judge", epistemic_judge_node)
    workflow.add_node("refusal", refusal_node)
    workflow.add_node("increment_retry", increment_retry_node)

    # Define Flow
    workflow.set_entry_point("retrieve")
    
    # The Decision Point
    workflow.add_conditional_edges(
        "retrieve",
        route_retrieval,
        {
            "generate": "generate_answer", # Fast Track (Immediate Answer)
            "refuse": "refusal"
        }
    )
    
    # Parallel Audit Branching (Currently detached from Fast Track for raw speed, can be customized later)
    # audit_agent handles its own tool loop
    workflow.add_conditional_edges(
        "audit_agent",
        route_audit_agent,
        {
            "tools": "tools",
            "__end__": "fake_chain" 
        }
    )
    
    workflow.add_edge("tools", "audit_agent")
    workflow.add_edge("fake_chain", "epistemic_judge")
    
    workflow.add_conditional_edges(
        "epistemic_judge",
        route_epistemic_judge,
        {
            "synthesize": "generate_answer", # Redirect synthesized to standard generate
            "retry": "increment_retry",
            "refuse": "refusal"
        }
    )
    
    workflow.add_edge("increment_retry", "retrieve")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("refusal", END)
    
    return workflow.compile()
