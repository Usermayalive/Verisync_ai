import json
import random
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from .state import GraphState
from backend.utils.logger import get_logger
from backend.utils.helpers import extract_json
from .llm_client import get_llm
from .prompts import (
    CAUSAL_AUTOPSY_PROMPT,
    FAKE_CHAIN_PROMPT,
    EPISTEMIC_JUDGE_PROMPT,
    GENERATE_ANSWER_PROMPT
)
from backend.retrieval_service.interfaces import (
    get_session_retriever,
    get_source_manifest,
    detect_temporal_drift,
    get_duplicate_sources,
    get_pii_report,
    add_to_session_store
)
from langgraph.prebuilt import ToolNode
from .tools import all_tools

logger = get_logger("Nodes")
tool_node = ToolNode(all_tools)

def _format_docs(docs: List[Document]):
    return "\n\n".join([
        f"Source: {d.metadata.get('source', 'Unknown')} (Location: {d.metadata.get('location', 'Unknown')})\nContent: {d.page_content}"
        for d in docs
    ])

def retrieve_node(state: GraphState) -> Dict[str, Any]:
    logger.info("Executing retrieve_node")
    session_id = state.get("session_id", "default")
    messages = state.get("messages", [])
    new_docs = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            new_docs.append(Document(
                page_content=msg.content,
                metadata={"source": f"Tool:{msg.name}", "session_id": session_id, "type": "tool_result"}
            ))
        elif isinstance(msg, HumanMessage) and len(msg.content) > 50:
            new_docs.append(Document(
                page_content=msg.content,
                metadata={"source": "User Chat", "session_id": session_id, "type": "chat_history"}
            ))
    if new_docs:
        add_to_session_store(session_id, new_docs)
    
    retriever = get_session_retriever(session_id)
    # Using the updated method that returns both doc and distance
    results = retriever.similarity_search_with_score(state["question"])
    
    logger.info(f"[DEBUG] session_id={session_id}, query={state['question']}, num_results={len(results)}")
    for doc, score in results[:3]:
        logger.info(f"[DEBUG]   score={score:.4f}, source={doc.metadata.get('source','?')}, text={doc.page_content[:60]}")

    docs = [doc for doc, score in results]
    if results:
        min_distance = min(score for doc, score in results)
        max_similarity = 1.0 - min_distance
    else:
        max_similarity = 0.0

    logger.info(f"[DEBUG] max_similarity={max_similarity:.4f}")

    # Fallback for summarization intent if vector search returns nothing
    summary_phrases = ["summary", "summarize", "overview", "what is this about", "general idea"]
    is_summary = any(p in state["question"].lower() for p in summary_phrases)
    if is_summary:
        max_similarity = 1.0 # Force pass for summarization
        if not docs:
            logger.info("Summarization intent detected. Fetching sample documents.")
            try:
                from backend.retrieval_service.storage.session_retriever import get_session_vector_store
                store = get_session_vector_store(session_id)
                res = store.similarity_search_with_score("", k=5) 
                docs = [doc for doc, score in res]
            except Exception as e:
                logger.warning(f"Summarization fallback failed: {e}")

    drift = detect_temporal_drift(docs)
    return {
        "documents": docs,
        "max_similarity": max_similarity,
        "source_manifest": get_source_manifest(session_id),
        "temporal_drift_warning": drift,
        "duplicate_sources": get_duplicate_sources(session_id),
        "pii_report": get_pii_report(session_id)
    }

def generate_answer_node(state: GraphState) -> Dict[str, Any]:
    logger.info("Executing generate_answer_node")
    model = state.get("model")
    llm = get_llm(model=model)
    chain = GENERATE_ANSWER_PROMPT | llm
    docs_str = _format_docs(state.get("documents", []))
    try:
        res = chain.invoke({"query": state["question"], "documents": docs_str})
        parsed = extract_json(res.content)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        parsed = {"answer": "Error generating answer.", "citations": []}
    return {
        "final_answer": parsed.get("answer", "No answer generated."),
        "citations": parsed.get("citations", []),
        "messages": [AIMessage(content=parsed.get("answer", ""))]
    }

def causal_autopsy_node(state: GraphState) -> Dict[str, Any]:
    logger.info("Executing causal_autopsy_node")
    model = state.get("model")
    llm = get_llm(bind_tools=all_tools, model=model)
    docs_str = _format_docs(state.get("documents", []))
    prompt = CAUSAL_AUTOPSY_PROMPT.format(query=state["question"], documents=docs_str)
    res = llm.invoke(prompt)
    if hasattr(res, "tool_calls") and res.tool_calls:
        return {"messages": [res]}
    try:
        parsed = extract_json(res.content)
    except Exception:
        parsed = {"error": "Failed to parse real chain"}
    return {"real_chain": parsed, "messages": [res]}

def fake_chain_node(state: GraphState) -> Dict[str, Any]:
    logger.info("Executing fake_chain_node")
    model = state.get("model")
    llm = get_llm(model=model)
    chain = FAKE_CHAIN_PROMPT | llm
    manifest_str = ", ".join(state.get("source_manifest", []))
    try:
        res = chain.invoke({"query": state["question"], "source_manifest": manifest_str})
        parsed = extract_json(res.content)
    except Exception as e:
        logger.error(f"Fake chain gen failed: {e}")
        parsed = {"fake_chain_a": {}, "fake_chain_b": {}}
    return {
        "fake_chain": parsed.get("fake_chain_a", {}),
        "fake_chain_b": parsed.get("fake_chain_b", {})
    }

def epistemic_judge_node(state: GraphState) -> Dict[str, Any]:
    logger.info("Executing epistemic_judge_node")
    model = state.get("model")
    llm = get_llm(use_judge_model=True, bind_tools=all_tools, model=model)
    chains = [
        {"id": "REAL", "data": state.get("real_chain", {})},
        {"id": "FAKE_A", "data": state.get("fake_chain", {})},
        {"id": "FAKE_B", "data": state.get("fake_chain_b", {})}
    ]
    random.shuffle(chains)
    mapped_chains = {chr(65+i): c for i, c in enumerate(chains)}
    prompt = EPISTEMIC_JUDGE_PROMPT.format(
        query=state["question"],
        documents=_format_docs(state.get("documents", [])),
        chain_a=json.dumps(mapped_chains["A"]["data"]),
        chain_b=json.dumps(mapped_chains["B"]["data"]),
        chain_c=json.dumps(mapped_chains["C"]["data"])
    )
    actual_result = "NONE"
    reasoning = "Error during judgment"
    try:
        res = llm.invoke(prompt)
        parsed = extract_json(res.content)
        chosen_id = parsed.get("grounded_chain_id", "NONE")
        actual_result = mapped_chains.get(chosen_id, {}).get("id", "NONE")
        reasoning = parsed.get("reasoning", "")
    except Exception:
        pass
    return {
        "epistemic_judge_result": "REAL" if actual_result == "REAL" else "FAKE",
        "judge_reasoning": reasoning
    }

def refusal_node(state: GraphState) -> Dict[str, Any]:
    logger.info("Executing refusal_node (conversation-aware)")
    question = state.get("question", "").lower()
    chat_history = state.get("chat_history", [])

    STOP_WORDS = {
        "know", "about", "think", "tell", "what", "where", "when", "how", "this",
        "that", "there", "their", "they", "your", "does", "do", "you", "been", "from"
    }
    query_words = set(w for w in question.split() if len(w) > 4 and w not in STOP_WORDS)

    mentioned_in_conversation = []
    past_history = list(chat_history)
    if past_history and past_history[-1].get("role") == "user" and past_history[-1].get("content", "").lower() == question:
        past_history.pop()

    for entry in past_history:
        content = (entry.get("content") or "").lower()
        for word in query_words:
            if word in content:
                mentioned_in_conversation.append(word)

    mentioned_in_conversation = list(set(mentioned_in_conversation))
    docs = state.get("documents", [])
    summary_phrases = ["summary", "summarize", "overview", "what is this about", "general idea"]
    is_summary = any(p in question for p in summary_phrases)
    
    if is_summary and docs:
        sources = list(set([d.metadata.get("source", "Unknown") for d in docs]))
        source_list = ", ".join(sources[:3])
        msg = (
            f"I'd love to help, but I'm primarily designed to answer specific questions rather than provide broad summaries! "
            f"Right now, I have access to files like **{source_list}**. "
            "Could you ask me a specific question about the details inside them?"
        )
    elif mentioned_in_conversation:
        terms = ", ".join(f'"{w}"' for w in mentioned_in_conversation[:5])
        msg = (
            f"We were just chatting about {terms}! However, I double-checked my uploaded documents and couldn't find any verified information about it there. "
            f"Would you like me to look into something else from the files we uploaded?"
        )
    elif docs:
        sources = list(set([d.metadata.get("source", "Unknown") for d in docs]))
        source_list = ", ".join(sources[:3])
        msg = (
            f"I've searched through my knowledge base, but I can't seem to find anything related to that! "
            f"Currently, my files are mostly about topics like **{source_list}**. "
            f"Would you like to ask a question about those, or maybe upload a new file?"
        )
    else:
        msg = (
            "It looks like I don't have any documents uploaded yet (or none that mention that topic). "
            "Try pasting a YouTube link, uploading a PDF, or asking about a file we've already added!"
        )

    return {"final_answer": msg, "refusal_reason": msg}
