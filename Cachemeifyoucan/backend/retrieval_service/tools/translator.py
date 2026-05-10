import logging
from typing import List
from langchain_core.documents import Document
from backend.utils.logger import get_logger

logger = get_logger("RetrievalService.Translator")
_models_cache = {}

def detect_and_translate(docs: List[Document]) -> List[Document]:
    """Detects document language and translates non-English text leveraging Helsinki-NLP models."""
    try:
        import langdetect
        from transformers import pipeline
    except ImportError:
        logger.warning("langdetect or transformers missing, skipping translation.")
        return docs
        
    processed_docs = []
    
    for doc in docs:
        try:
            lang = langdetect.detect(doc.page_content)
        except Exception:
            lang = 'en'
            
        doc.metadata["source_language"] = lang
        
        if lang == 'en':
            processed_docs.append(doc)
            continue
            
        original_doc = Document(page_content=doc.page_content, metadata=doc.metadata.copy())
        original_doc.metadata["is_translation"] = False
        processed_docs.append(original_doc)
        
        model_name = f"Helsinki-NLP/opus-mt-{lang}-en"
        
        if model_name not in _models_cache:
            try:
                logger.info(f"Downloading/loading translation model: {model_name}")
                _models_cache[model_name] = pipeline("translation", model=model_name)
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")
                _models_cache[model_name] = None
        
        translator_pipeline = _models_cache.get(model_name)
        
        if translator_pipeline:
            try:
                chunked_text = doc.page_content[:1500] 
                res = translator_pipeline(chunked_text)
                translated_text = res[0]['translation_text']
                
                trans_doc = Document(page_content=translated_text, metadata=doc.metadata.copy())
                trans_doc.metadata["language"] = "en"
                trans_doc.metadata["is_translation"] = True
                
                processed_docs.append(trans_doc)
                logger.info(f"Successfully generated a translation for cross-lingual support (Source: {doc.metadata.get('source', 'Unknown')})")
            except Exception as e:
                logger.warning(f"Translation inference failed for chunk: {e}")
                
    return processed_docs
