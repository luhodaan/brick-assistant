from typing import Literal, TypedDict, Union
from pydantic import Field,BaseModel
from langchain.chat_models.base import BaseChatModel
from pathlib import Path

# Define the config
class GraphConfig(TypedDict):
    model: Union[
        Literal[ "openai", "llama3.2"], BaseChatModel
    ]


class AgentConfig(BaseModel):
    """
    Centralized configuration for the agent.
    All required parameters must be passed explicitly.
    """
    database_uri: str = Field(..., description="Database connection URI")
    openai_api_key: str = Field(..., description="OpenAI API key")
    metadata_file: Path = Field(..., description="Path to metadata JSON file")
    ttl_files_path: Path = Field(..., description="Directory containing TTL files")
    default_model: str = Field("gpt-4-1106-preview", description="Default LLM model")
    top_k_results: int = Field(5, description="Number of results to return for searches")