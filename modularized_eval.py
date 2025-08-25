from wuerth_agent.evals.dataset_ttl import Examples
from wuerth_agent.evals.grader import final_answer_correct
from compiled_graphs import wuerth_vanilla_graph_dev as graph
from langsmith import Client

examples = Examples
ghraph = graph
client = Client()


dataset_name = "wuerth_vanilla_ttl_dataset"
if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )

def run_graph(inputs: dict) -> dict:
    """Run graph and track the trajectory it takes along with the final response."""
    try:
        result = graph.invoke({"messages": [
            { "role": "user", "content": inputs['question']},
        ]}, config={"env": "test"})
        
        # Fix: Access .content attribute instead of ["content"] key
        response = result["messages"][-1].content
        
        return {"response": response}
    
    except Exception as e:
        print(f"Error in run_graph: {e}")
        return {"response": f"Error: {str(e)}"}

experiment_results =  client.evaluate(
    run_graph,
    data=dataset_name,
    evaluators=[final_answer_correct],
    experiment_prefix="sql-agent-gpt4o-e2e",
    num_repetitions=1,
    max_concurrency=1,
)
