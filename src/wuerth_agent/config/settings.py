import os
from pathlib import Path

# Database Configuration
def get_database_uri() -> str:
    """Get the database URI from environment variables."""
    uri = os.getenv("DATABASE_URI")
    if not uri:
        raise ValueError("DATABASE_URI environment variable is not set.")
    return uri

# API Keys
def get_openai_api_key() -> str:
    """Get the OpenAI API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.") 
    return api_key

# CONSTANTS
# Model Configuration 
DEFAULT_MODEL = "gpt-4.1-mini"
TOP_K_RESULTS = 5

# File Paths
METADATA_FILE = "data/metadataloc.json"
TTL_FILES_PATH = Path("data/ttl_files")  