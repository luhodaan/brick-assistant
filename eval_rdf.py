from brick_assistant.evals.dataset_ttl import Examples
from brick_assistant.evals.grader import final_answer_correct
from compiled_graphs import wuerth_vanilla_graph_devRDF as graph
from langsmith import Client

import os
from pathlib import Path
from dotenv import load_dotenv

# Import your config class and graph classes
from brick_assistant.config.configs import AgentConfig  

from brick_assistant.graphs.wuerth_vanilla_graph_dev_rdf import WuerthVanillaGraphRDF

from langchain.globals import set_llm_cache
set_llm_cache(None)


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
def make_graph():
    config = AgentConfig(
        database_uri="postgresql+psycopg2://user:password@localhost:25432/store_data",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        metadata_file=Path("data/metadataloc.json"),  
        ttl_files_path=Path("data/ttl_files")  
    )
    return WuerthVanillaGraphRDF(keys=config)._compiled_graph()



examples = Examples
client = Client()


Dataset_name = "wuerth_ttl_RDF_threadsafe"
if not client.has_dataset(dataset_name=Dataset_name):
    dataset = client.create_dataset(dataset_name=Dataset_name)
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )

def run_graph(inputs: dict) -> dict:
    graph = make_graph()
    try:
        result = graph.invoke(
            {"messages": [{"role": "user", "content": inputs['question']}]},
            config={"env": "test"},
        )
        response = result["messages"][-1].content
        return {"response": response}
    except Exception as e:
        print(f"Error in run_graph: {e}")
        return {"response": f"Error: {str(e)}"}

experiment_results =  client.evaluate(
    run_graph,
    data=Dataset_name,
    evaluators=[final_answer_correct],
    experiment_prefix="rdf_improvement",
    num_repetitions=1,
    max_concurrency=1,
)
