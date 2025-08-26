# eval_langfuse_run.py
import os, re, time, json
from pathlib import Path
from dotenv import load_dotenv

from langfuse import get_client

# --- your project bits ---
from brick_assistant.config.configs import AgentConfig
from brick_assistant.graphs.wuerth_vanilla_graph_dev_rdf import WuerthVanillaGraphRDF

from brick_assistant.evals.dataset_ttl import Examples
from brick_assistant.evals.grader import final_answer_correct  



from typing import Annotated, TypedDict
from langchain.chat_models import init_chat_model

# ---------- config ----------
DATASET_NAME = "wuerth_ttl_RDF_optimization"   # reuse across runs
RUN_NAME     = "rdf_improvement_2025_08_25"     # change per experiment
# ----------------------------

# ---------- env / clients ----------
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

lf = get_client()  # uses LANGFUSE_* env vars

# ---------- your agent ----------
def make_graph():
    cfg = AgentConfig(
        database_uri="postgresql+psycopg2://user:password@localhost:25432/store_data",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        metadata_file=Path("data/metadataloc.json"),
        ttl_files_path=Path("data/ttl_files"),
    )
    return WuerthVanillaGraphRDF(keys=cfg)._compiled_graph()

def run_graph(question: str) -> str:
    g = make_graph()
    result = g.invoke({"messages": [{"role": "user", "content": question}]},
                      config={"env": "test"})
    # assumes LangGraph returns messages list
    return result["messages"][-1].content

# ---------- helpers ----------
def ensure_dataset_exists():
    """Get dataset; if missing, create and populate from your Examples once."""
    try:
        return lf.get_dataset(name=DATASET_NAME)
    except Exception:
        ds = lf.create_dataset(name=DATASET_NAME, description="Auto-created from script")
        for ex in Examples:
            q = ex["inputs"]["question"]
            exp = ex["outputs"]["response"]
            lf.create_dataset_item(
                dataset_name=DATASET_NAME,
                input={"question": q},
                expected_output={"response": exp},
                metadata={"source": "Examples_literal"}
            )
        return lf.get_dataset(name=DATASET_NAME)

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

# ---------- main eval ----------
def main():
    dataset = ensure_dataset_exists()

    for item in dataset.items:
        q = item.input.get("question") if isinstance(item.input, dict) else item.input
        expected = ""
        if item.expected_output:
            expected = item.expected_output.get("response") or ""

        with item.run(
            run_name=RUN_NAME,
            run_description="Eval of RDF agent with LLM grader",
            run_metadata={"agent":"wuerth_vanilla_graph_devRDF"}
        ) as root:
            # canonical input on TRACE
            root.update_trace(input={"question": q}, metadata={"dataset_item_id": item.id})

            # 1) agent generation
            t0 = time.time()
            with lf.start_as_current_generation(
                name="agent_call",
                input={"question": q},
                model="agent:wuerth_vanilla_graph_devRDF"
            ) as gen:
                try:
                    pred = run_graph(q)
                    gen.update(output={"response": pred})
                    gen.score(name="latency_ms", value=int((time.time()-t0)*1000), data_type="NUMERIC")
                except Exception as e:
                    gen.update(output={"error": str(e)})
                    gen.score(name="generation_error", value=True, data_type="BOOLEAN")
                    root.update_trace(output={"error": str(e)})
                    root.score_trace(name="run_failed", value=True, data_type="BOOLEAN")
                    continue

            # 2) LLM judge generation (your LangChain grader)
            with lf.start_as_current_generation(
                name="llm_judge",
                input={"question": q, "ground_truth": expected, "student": pred},
                model="gpt-4o-mini",
                metadata={"role":"evaluator"}
            ) as judge_gen:
                grade = final_answer_correct(q, expected, pred)  # -> {"reasoning":..., "is_correct":...}
                judge_gen.update(output=grade)

            # put final output on TRACE
            root.update_trace(output={"response": pred})

            # 3) trace-level scores for aggregation
            root.score_trace(name="final_answer_correct_bool", value=bool(grade), data_type="BOOLEAN")
            root.score_trace(name="final_answer_correct", value=1.0 if grade else 0.0, data_type="NUMERIC")
            #root.update_trace(metadata={"judge_reasoning": grade["reasoning"]})

    lf.flush()

if __name__ == "__main__":
    main()
