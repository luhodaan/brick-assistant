from brick_assistant.config import settings
from brick_assistant.tools import prompts
from pydantic import BaseModel, Field
from typing import Optional

from langgraph.graph import MessagesState as BaseMessagesState
from langchain.chat_models.base import BaseChatModel

from langchain_core.messages import AIMessage, ToolMessage

# REFACTOR FROM EDGES TO COMMANDS
from langgraph.graph import END
from typing import Literal
from langgraph.types import Command, interrupt 

from rdflib import Graph, BNode

class QueryEvaluation(BaseModel):
    is_valid: bool = Field(description="Whether the query is valid")
    clarified_query: str = Field(description="Clarified version of the query")
    explanation: str = Field(description="Explanation of the evaluation")

class MessagesState(BaseMessagesState):
    query_evaluation: Optional[QueryEvaluation] = None 
    
def evaluate_user_query(state: MessagesState, llm_instance: BaseChatModel) -> Command[Literal["tables_or_rdf", END]]:
    system_message = {
        "role": "system",
        "content": prompts.EVALUATE_USER_QUERY_PROMPT
    }   
    structured_llm = llm_instance.with_structured_output(QueryEvaluation)
    evaluation_result = structured_llm.invoke([system_message] + state["messages"])
    query_eval = evaluation_result

    if query_eval and query_eval.is_valid:
        goto = "tables_or_rdf"
    else:
        goto = END
    update = {
        "messages": [{"role": "assistant", "content": f"Query evaluation: {evaluation_result.explanation}"}],
        "query_evaluation": evaluation_result  
    }
    
    return Command(update=update, goto=goto)

def call_get_schema(state: MessagesState,llm_instance: BaseChatModel, get_schema_tool):
    llm_with_tools =llm_instance.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def generate_query(state: MessagesState, llm_instance: BaseChatModel, run_query_tool, rdf_toolkit) -> Command[Literal["check_query","rdf_toolkit", END]]:
    system_message = {
        "role": "system",
        "content": prompts.GENERATE_QUERY_SYSTEM_PROMPT.format(
            dialect="postgresql",
            top_k=settings.TOP_K_RESULTS
        ),
    }
    llm_with_tools = llm_instance.bind_tools([run_query_tool,rdf_toolkit])
    response = llm_with_tools.invoke([system_message] + state["messages"])

    # Fix: Initialize goto to END by default
    goto = END
    
    # Check if there are tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call.get("name") == "sql_db_query":
            goto = "check_query"
        elif tool_call.get("name") == "rdf_toolkit":
            goto = "rdf_toolkit"
        # else remains END

    update = {"messages": [response]}
    return Command(update=update, goto=goto)



def check_query(state: MessagesState, llm_instance: BaseChatModel, run_query_tool):
    system_message = {
        "role": "system",
        "content": prompts.CHECK_QUERY_SYSTEM_PROMPT.format(
            dialect="postgresql",
        ),
    }
    # Generate an artificial user message to check
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm_instance.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message, user_message])
    response.id = state["messages"][-1].id

    return {"messages": [response]}

def tables_or_rdf(state: MessagesState, llm_instance: BaseChatModel, list_tables_tool, rdf_toolkit) -> Command[Literal["list_tables_tool", "rdf_toolkit", END]]:
    system_message = {
        "role": "system",
        "content": prompts.RDF_DB_PROMPT,
    }
    
    llm_with_tools = llm_instance.bind_tools([list_tables_tool, rdf_toolkit])
    response = llm_with_tools.invoke([system_message] + state["messages"]) 

    goto = END
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call.get("name") == "rdf_toolkit":
            goto = "rdf_toolkit"    
        if tool_call.get("name") == "list_tables_tool" or tool_call.get("name") == "list_tables" or tool_call.get("name") == "sql_db_list_tables":
            goto = "list_tables_tool"

    update = {"messages": [response]}
    return Command(update=update, goto=goto)  


def tables_or_end(state: MessagesState, llm_instance: BaseChatModel, list_tables_tool, rdf_toolkit) -> Command[Literal["list_tables_tool", "rdf_toolkit", END]]:
    system_message = {
        "role": "system",
        "content": prompts.TABLES_OR_END_PROMPT,
    }    
    llm_with_tools = llm_instance.bind_tools([list_tables_tool, rdf_toolkit])
    response = llm_with_tools.invoke([system_message] + state["messages"])

    goto = END
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call.get("name") == "rdf_toolkit":
            goto = "rdf_toolkit"    
        if tool_call.get("name") == "list_tables_tool" or tool_call.get("name") == "list_tables" or tool_call.get("name") == "sql_db_list_tables":
            goto = "list_tables_tool"

    update = {"messages": [response]}
    return Command(update=update, goto=goto)

# ============================================
# Functional interfaces for use in graph nodes
# ============================================

from typing import Dict, Optional, List, Tuple
import json
import os
from functools import lru_cache
from langchain_core.messages import AIMessage
from brick_assistant.config import settings
from brick_assistant.config.configs import AgentConfig
from pathlib import Path

@lru_cache(maxsize=1)
def load_metadata(path_str: str) -> Dict:
    """Load and cache metadata from file."""
    with open(path_str, 'r') as file:
        return json.load(file)

def enforced_metadata_keys_call(state: MessagesState,path: Path) -> Dict[str, List]:
    """
    Functional interface for metadata keys retrieval.
    Used directly in graph nodes.
    """
    metadata = load_metadata(str(path))
    buildings = {
        outer_key: metadata[outer_key]["location"] 
        for outer_key in metadata.keys()
    }
    
    # Return in a format consistent with other nodes
    message = AIMessage(
        content=f"Available buildings and locations: {json.dumps(buildings, indent=2)}"
    )
    return {"messages": [message]}

   
# def create_rdf_toolkit(state: MessagesState, llm_instance: BaseChatModel, rdf_toolkit) -> ToolMessage: 
#     system_message = {
#         "role": "system",
#         "content": prompts.rdf_toolkit_PROMPT
#     }

#     llm_with_tools = llm_instance.bind_tools([rdf_toolkit], tool_choice="any")
#     response = llm_with_tools.invoke([system_message] + state["messages"])  

#     return {"messages": [response]}
