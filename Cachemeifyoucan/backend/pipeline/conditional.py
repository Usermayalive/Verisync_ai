from .state import GraphState
from langgraph.prebuilt import tools_condition

MAX_RETRIES = 3
CONFIDENCE_THRESHOLD = 0.5

FAST_TRACK_THRESHOLD = 0.85

def route_retrieval(state: GraphState):
    max_sim = state.get("max_similarity", 0.0)
    
    # PGVector returns L2 distance (lower = better). max_similarity = 1.0 - distance.
    # Good matches with all-MiniLM-L6-v2 typically have max_similarity 0.3-0.6.
    # 0.30 filters out truly irrelevant queries while letting real matches pass.
    if max_sim >= 0.30:
        return "generate"
    
    return "refuse"

def route_epistemic_judge(state: GraphState):
    result = state.get("epistemic_judge_result", "FAKE")
    retries = state.get("retry_count", 0)
    if result == "REAL":
        return "synthesize"
    if retries < MAX_RETRIES:
        return "retry"
    else:
        return "refuse"

def route_audit_agent(state: GraphState):
    return tools_condition(state)
