import re
def format_citations(text, documents):
    for i, doc in enumerate(documents):
        source = doc.metadata.get("source", "Unknown")
        pattern = re.compile(re.escape(doc.page_content[:50]), re.IGNORECASE)
        if pattern.search(text):
            text += f" [{source}]"
    return text
