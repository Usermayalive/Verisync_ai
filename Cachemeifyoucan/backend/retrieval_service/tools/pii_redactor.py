import logging
from typing import List
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from langchain_core.documents import Document
from backend.utils.logger import get_logger
logger = get_logger("RetrievalService.PII")
class PIIRedactor:
    def __init__(self):
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
        self.anonymizer = AnonymizerEngine()
    def redact(self, docs: List[Document]) -> List[Document]:
        for doc in docs:
            results = self.analyzer.analyze(text=doc.page_content, language='en')
            anonymized_result = self.anonymizer.anonymize(
                text=doc.page_content,
                analyzer_results=results
            )
            doc.page_content = anonymized_result.text
            doc.metadata["pii_redacted"] = True
        return docs
_redactor = None
def pii_redact(docs: List[Document]) -> List[Document]:
    global _redactor
    if _redactor is None:
        try:
            _redactor = PIIRedactor()
        except Exception as e:
            logger.error(f"Error: {e}")
            return docs
    return _redactor.redact(docs)
