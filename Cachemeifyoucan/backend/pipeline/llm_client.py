from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from backend.config import settings

def get_llm(use_judge_model=False, temperature=0.0, bind_tools=None, model: str = None):
    models = []
    # If model is specified, override selection
    model = model.lower() if isinstance(model, str) else model
    if model == "deepseek":
        # Keep judge-routing intent if a DeepSeek judge model is explicitly configured.
        model_name = (
            settings.JUDGE_MODEL
            if use_judge_model and settings.JUDGE_MODEL.lower().startswith("deepseek")
            else "deepseek-chat"
        )
        ds_llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            max_retries=2
        )
        if bind_tools:
            return ds_llm.bind_tools(bind_tools)
        return ds_llm
    elif model == "gemini":
        model_name = settings.JUDGE_MODEL if use_judge_model else settings.DEFAULT_MODEL
        for api_key in settings.valid_google_api_keys:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key,
                max_retries=1
            )
            if bind_tools:
                llm = llm.bind_tools(bind_tools)
            models.append(llm)
        if not models:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=settings.GOOGLE_API_KEY,
                max_retries=1
            )
            if bind_tools:
                llm = llm.bind_tools(bind_tools)
            return llm
        main_llm = models[0]
        if len(models) > 1:
            main_llm = main_llm.with_fallbacks(models[1:])
        return main_llm
    # Default: use env config (USE_DEEPSEEK or fallback)
    if settings.USE_DEEPSEEK:
        model_name = "deepseek-chat"
        ds_llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            max_retries=2
        )
        if bind_tools:
            return ds_llm.bind_tools(bind_tools)
        return ds_llm
    # 1. Google Gemini Models
    model_name = settings.JUDGE_MODEL if use_judge_model else settings.DEFAULT_MODEL
    for api_key in settings.valid_google_api_keys:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key,
            max_retries=1
        )
        if bind_tools:
            llm = llm.bind_tools(bind_tools)
        models.append(llm)
    # 2. Deepseek Model as Final Fallback
    if settings.DEEPSEEK_API_KEY and "change-this" not in settings.DEEPSEEK_API_KEY.lower():
        ds_llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=temperature,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            max_retries=1
        )
        if bind_tools:
            ds_llm = ds_llm.bind_tools(bind_tools)
        models.append(ds_llm)
    if not models:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.GOOGLE_API_KEY,
            max_retries=1
        )
        if bind_tools:
            llm = llm.bind_tools(bind_tools)
        return llm
    main_llm = models[0]
    if len(models) > 1:
        main_llm = main_llm.with_fallbacks(models[1:])
    return main_llm
