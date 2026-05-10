import json
import re
def extract_json(text: str) -> dict:
    """
    Attempts to extract JSON from LLM output, handling markdown blocks 
    and extra text.
    """
    if isinstance(text, list):
        text = "".join([str(t.get("text", t)) if isinstance(t, dict) else str(t) for t in text])
    text = str(text).strip()
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if match:
        block = match.group(1).strip()
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass
    match = re.search(r'(\{.*?\})', text, re.DOTALL)
    if match:
        block = match.group(1).strip()
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {} 
