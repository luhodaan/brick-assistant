from typing import Union
from brick_assistant.config import settings

from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

def _get_llm(llm: Union[str, BaseChatModel], llm_api_key: str) -> BaseChatModel:
    """
    Get the LLM instance based on the provided model name or instance.
    
    Args:
        llm (Union[str, BaseChatModel]): The model name or an instance of a chat model.
        
    Returns:
        BaseChatModel: An instance of the specified LLM.
    """

    if isinstance(llm, BaseChatModel):
        return llm
    

    if llm == "llama3-groq":
        return ChatOllama(model="llama3-groq-tool-use:8b", temperature=0.0)
    elif llm == "openai":
        return ChatOpenAI(model="gpt-4.1-mini-2025-04-14", openai_api_key=llm_api_key, temperature=0.0)
    return llm