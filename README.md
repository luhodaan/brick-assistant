# 🧱🔗 Brick Assistant 

## Brick Assistant is an AI-powered tool designed to help you query and interact with your building datasources using natural language

![Brick Assistant Logo](pics/brick-assistant.png)

## 📖 Overview
The Brick Assistant can answer questions like:

- *"What is the average temperature in the building X over the last week?"*
- *"How many VAVs are there in the building?"*
- *"What is the building with the biggest area?"*
- *"List all the AHUs in the building and their associated zones."*

---

## ⚙️ Installation

This project uses **UV** for dependency management.  

**``Clone the repository``**.

Then:

1. Install UV.  
2. Sync dependencies:

```bash
uv sync
```

Syncing ensures that all project dependencies are installed and up-to-date with the lockfile.
If the project virtual environment (.venv) does not exist, it will be created.

Given that the project also import its own package and modules, you need to install it in editable mode:

```bash
uv pip install -e .
```

## Examples of usage:
### You can find some examples of usage in the notebook: **`basic_usage_examples.ipynb`**.

````python
from compiled_graphs import wuerth_vanilla_graph_devRDF, wuerth_vanilla_graph_devRDF_compiled

g = wuerth_vanilla_graph_devRDF
question = """what building has the smallest area"""
answers = g.run(input_data = {"user_prompt":question}, stream=True) 
for answer in answers:
    print(answer)
````

# 🗂️ Project structure and workflow

![workflow](pics/workflow.png)

**This project was built to be modular and extensible. Let's dive in into the main components:**

### 📁 config
- **`configs.py`**:
This module contains configuration settings for the project, including API keys and other constants.
The necessary fields are visibile in the '***'.env.example file which must be copied and renamed to .env*** and filled with the appropriate values.

### 📁 helpers

- **`llm_models.py`**:
This module contains helper functions to initialize and configure LLM models.  
Currently, it supports OpenAI models, but it can be easily extended to include other providers.  
  

### 📁 tools

This package contains the nodes of the graph along with the tools and edges that connect them.  
Edges are embedded directly in tool definitions via the new **LangGraph Command** module, allowing the agent to reason about data in a structured way.

#### Files

- **`functions.py`**  
  Core function nodes of the graph.  
  Each function represents a specific operation (e.g., database query, data processing).  
  Workflow:  
  1. Receive input (from a previous node or user).  
  2. Process it (logic, query, or calculation).  
  3. Return output (to the next node or the user).  

- **`prompts.py`**  
  Prompt templates to guide AI responses.

- **`rdf_query.py`**  
  Handles **SPARQL query generation**.  
  - Uses a library of predefined queries (expandable).  
  - The LLM only decides *which query to run* and *with which parameters*.  
  - Queries executed via `rdflib` with a safe-lock mechanism to prevent concurrent graph access.

- **`tools.py`**  
  Early prototype of a `BrickExploration` tool for graph exploration & querying.  
  - **Not used in the current implementation** (kept for reference).  
  - May be reintroduced if predefined queries are insufficient.


### 📁 graphs
Chore module of the project. This is where the workflow is defined and all the other pieces are glued toghether. 

#### Files

- **`abstract_rdf.py`**  
  This is the skeleton of our graph. Its main purpose is to make the tools available for the actual graph.  
  Specifically it instantiates the SQL set of tools and the RDF query tool. The workflow is yet not defined here to leave the possibility to build different graphs with different workflows using the same set of tools.

- **`wuerth_graph_rdf.py`**  
  This is the actual graph that is used in the project. It inherits from the abstract_rdf.py and defines the workflow using the tools defined there.

---

### 📁 evals
This module contains evaluation scripts to test the performance and accuracy of the Brick Assistant.

#### Files
- **`dataset_ttl.py`**  
  A series of questions and answers to test the graph on some specific predifined questions, regarding the Würth buildings in this case.

- **`grader.py`**  
  A simple evaluation script that uses a separate LLM to grade the answers provided by the Brick Assistant against the reference answers in the dataset in the form of a pass/fail grade where the LLM is isntructed as if it was a teacher correcting a student's exam.


> ▶️ To actually perform the evaluation, it is needed to launch the eval scrip named `eval_rdf.py` which will load the graph, the dataset and run the grader on each question/answer pair.

## 🚀 How to use the Brick Assistant

### 🏃 Running the assistant 

1. **Set up environment variables**  
   - Copy the provided `.env.example` file to `.env`.  
   - Fill in the required values.  
   - Currently, the only supported LLM provider is **OpenAI**, so make sure to set your **OpenAI API key** in the `.env` file.  


   > 💡 You can also add your **LangSmith API key** (recommended) for debugging and tracing graph execution.  
   > Get it from [LangSmith](https://langchain.com/langsmith) after creating an account.  

---

2. **Run the assistant**  
   You have two options:  

   **a. Run with LangGraph Studio**  
   - After activating the virtual environment:  
     ```bash
     langgraph dev
     ```  
   - Or without activating the environment, using `uv`:  
     ```bash
     uv run langgraph dev
     ```  

   This will start a local web server for LangGraph Studio where you can:  
   - Interact with the graph visually.  
   - Send prompts.  
   - View real-time execution traces.  

   **b. Run directly in Python**  
   - You can also run the assistant from a **Python script** or a **Jupyter Notebook**.  
   - Usage examples are also provided in the notebook: **`basic_usage_examples.ipynb`**.  

## Development Notes

📦 **Packaging and File Paths**
When preparing to make Brick Assistant installable as a package, it’s critical to respect file paths that the system relies on.
This ensures the assistant can work not only with Würth data but also with any dataset.

Key paths to maintain:

- **Database connection string**:  
  ```python
  database_uri: str = Field(..., description="Database connection URI")
  ```
- **Metadata file**:  
  ```python
  METADATA_FILE = "data/metadataloc.json"
  ```
- **TTL files path**:  
  ```python
  TTL_FILES_PATH = Path("data/ttl_files")
  ```

## 🔮 Future Work

- 📚 **Expand RDF query library**  
  Cover a broader range of use cases with additional predefined queries.  

- 🛠️ **Introduce fallback mechanism**  
  Re-enable the `BrickExploration` tool when predefined queries cannot answer a user’s question.  

- 👩‍🏫 **Add human-in-the-loop feedback**  
  Incorporate user feedback for continuous refinement and improvement.  

- 🤖 **Support additional LLM providers**  
  Extend compatibility beyond OpenAI for more flexibility.  

- 📦 **Make it a package**

- 🌐 **Update the web-app depending on the assistant**  
  Currently it uses the old token-expensive, inefficient version, which can be found [here](https://gitlab.inf.unibz.it/eeb/wuerth-agent). 
   
- 🧪 **MCP server exploration**
See how to build an mcp server on top of the assistant.
