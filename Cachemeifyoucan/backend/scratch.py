from langchain_core.runnables import RunnableWithFallbacks
from langchain_openai import ChatOpenAI

llm1 = ChatOpenAI(model="gpt-3.5-turbo", max_retries=0)
llm2 = ChatOpenAI(model="gpt-4", max_retries=0)
llms = llm1.with_fallbacks([llm2])

class MyTool:
    name: str = "my_tool"
    description: str = "does something"

try:
    tool_llms = llms.bind_tools([MyTool])
    print("Success")
except Exception as e:
    print("Error:", e)
