import datetime
from typing import List, Optional
from langchain_core.documents import Document
def calculate_drift(docs: List[Document]) -> Optional[str]:
    dates = []
    for doc in docs:
        d = doc.metadata.get("date")
        if d:
            try:
                dates.append(datetime.datetime.strptime(d, "%Y-%m-%d").date())
            except:
                pass
    if not dates:
        return None
    oldest = min(dates)
    newest = max(dates)
    today = datetime.date.today()
    span = (newest - oldest).days
    age = (today - newest).days
    if span > 90 or age > 30:
        return f"Temporal drift detected: knowledge span is {span} days, and latest data is {age} days old."
    return None
