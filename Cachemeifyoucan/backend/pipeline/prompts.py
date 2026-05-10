from langchain_core.prompts import PromptTemplate

LIGHTWEIGHT_JUDGE_PROMPT = PromptTemplate(
    template="""
You are an expert filter. Given the following user query and a set of retrieved documents, 
decide if the documents contain enough information to answer the query.

User Query: {query}
Retrieved Documents:
{documents}

Respond ONLY with a JSON object:
{{
    "status": "SUFFICIENT" or "AMBIGUOUS" or "INSUFFICIENT" or "CHITCHAT",
    "confidence_score": 0.0 to 1.0,
    "reasoning": "Brief explanation"
}}

SUFFICIENT: The chunks clearly or partially answer the question with credible evidence. Also use SUFFICIENT if the user is asking for a general "Summary", "Overview", or "What is this about?" and there are retrieved documents present. 
AMBIGUOUS: Chunks are relevant but may be vague, incomplete, or require deeper auditing to confirm. Use this if there is ANY potential relevance.
INSUFFICIENT: Absolutely no relevant chunks found in the provided context for this specific query. Do not use this if the user is asking for a summary and documents are present.
CHITCHAT: The user is just saying hello, giving a greeting, or asking a conversational pleasantry (e.g., "hi", "how are you").
""",
    input_variables=["query", "documents"]
)

CAUSAL_AUTOPSY_PROMPT = PromptTemplate(
    template="""
You are an expert evidence tracer agent. Given the query and documents, 
create a logical chain of evidence. You can use tools to verify facts or extract data.

User Query: {query}
Retrieved Documents:
{documents}

Output ONLY valid JSON:
{{
    "claim": "The verified answer piece",
    "inference": "The logical connection",
    "raw_data_locator": "Exact source and location",
    "tool_verification": "Details of any tool use"
}}
""",
    input_variables=["query", "documents"]
)

FAKE_CHAIN_PROMPT = PromptTemplate(
    template="""
You are an adversarial testing system. You must generate TWO highly plausible but completely FAKE evidence chains.
They must use different, invented source names NOT in the manifest.

Actual Source Manifest (DO NOT USE): {source_manifest}
User Query: {query}

Output ONLY valid JSON:
{{
    "fake_chain_a": {{
        "claim": "Plausible but false answer A",
        "inference": "Flawed reasoning A",
        "raw_data_locator": "Invented Source 1"
    }},
    "fake_chain_b": {{
        "claim": "Plausible but false answer B",
        "inference": "Flawed reasoning B",
        "raw_data_locator": "Invented Source 2"
    }}
}}
""",
    input_variables=["query", "source_manifest"]
)

EPISTEMIC_JUDGE_PROMPT = PromptTemplate(
    template="""
You are the Final Epistemic Judge. You have a query, documents, and THREE evidence chains (A, B, and C).
One is real and grounded in the retrieved documents or tool results. The other two are hallucinations.

User Query: {query}
Retrieved Documents:
{documents}

Chain A: {chain_a}
Chain B: {chain_b}
Chain C: {chain_c}

Identify the grounded chain. Use your tools if you need to verify source existence or facts.
Output ONLY valid JSON:
{{
    "grounded_chain_id": "A", "B", or "C" (or "NONE"),
    "reasoning": "Why this one is real and the others are fake",
    "confidence_score": 0.0 to 1.0
}}
""",
    input_variables=["query", "documents", "chain_a", "chain_b", "chain_c"]
)

GENERATE_ANSWER_PROMPT = PromptTemplate(
    template="""
Analyze the query and documents. Provide a clear, detailed, and beautifully formulated answer containing inline citations.

User Query: {query}
Documents: {documents}

Output ONLY valid JSON matching this exact structure:
{{
    "answer": "The prose answer with inline citations like [Source Name]",
    "citations": [
        {{"source": "name", "location": "page/row", "content_summary": "..."}},
        ...
    ]
}}
""",
    input_variables=["query", "documents"]
)

SYNTHESIZE_ANSWER_PROMPT = PromptTemplate(
    template="""
You are an answer refiner. You have an initial answer and a verified evidence chain.
Add any missing citations or ground it further based on the verified chain. 
Do not rewrite the prose significantly unless it's wrong.

Initial Answer: {initial_answer}
Verified Chain: {real_chain}

Final Answer (Prose with added citations):
""",
    input_variables=["initial_answer", "real_chain"]
)

TABLE_EXTRACTION_PROMPT = PromptTemplate(
    template="""
Extract table parameters if the query targets a specific cell.
Query: {query}

JSON Output:
{{
    "requires_table_tool": true/false,
    "table_id": "Table 1",
    "row_index": 0,
    "col_index": 0,
    "source_hint": "filename"
}}
""",
    input_variables=["query"]
)
