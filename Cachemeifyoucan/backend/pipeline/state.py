from typing import Annotated, List, Dict, Any, Optional, Sequence
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

def merge_documents(old: List[Document], new: List[Document]) -> List[Document]:
    return old + new

def merge_messages(old: Sequence[BaseMessage], new: Sequence[BaseMessage]) -> List[BaseMessage]:
    return list(old) + list(new)

class GraphState(TypedDict):
    question: str
    session_id: str
    model: Optional[str]
    retry_count: int
    documents: Annotated[List[Document], merge_documents]
    source_manifest: List[str]
    citations: List[Dict[str, Any]]
    lightweight_judge_result: str
    judge_confidence: float
    max_similarity: float
    real_chain: Dict[str, Any]
    fake_chain: Dict[str, Any]
    fake_chain_b: Dict[str, Any]
    epistemic_judge_result: str
    judge_reasoning: str
    final_answer: str
    refusal_reason: str
    temporal_drift_warning: Optional[str]
    duplicate_sources: List[str]
    pii_report: List[Dict[str, Any]]
    chat_history: List[Dict[str, str]]
    chat_context_reference: Optional[str]
    messages: Annotated[List[BaseMessage], merge_messages]
