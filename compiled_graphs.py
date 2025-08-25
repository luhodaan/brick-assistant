import os
from pathlib import Path
from dotenv import load_dotenv

# Import your config class and graph classes
from wuerth_agent.config.configs import AgentConfig  

from wuerth_agent.graphs.wuerth_vanilla_graph_dev_rdf import WuerthVanillaGraphRDF


# Load .env file manually (for getting the values)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")
else:
    print(f".env file not found at: {env_path}")

# Check what's in the environment
print("DEBUG: DATABASE_URI:", os.getenv("DATABASE_URI"))
print("DEBUG: OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

# Create the config instance with values from environment
config = AgentConfig(
    database_uri="postgresql+psycopg2://user:password@localhost:25432/store_data",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    metadata_file=Path("data/metadataloc.json"),  
    ttl_files_path=Path("data/ttl_files")  
)

# Create graph instances with injected config

wuerth_vanilla_graph_devRDF = WuerthVanillaGraphRDF(keys=config)._compiled_graph()
