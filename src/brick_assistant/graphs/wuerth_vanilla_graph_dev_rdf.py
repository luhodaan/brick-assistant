from langgraph.graph import StateGraph, START
from brick_assistant.tools.functions import MessagesState
from typing import Any, Dict, List, Union
from langchain.chat_models.base import BaseChatModel
from brick_assistant.config.configs import GraphConfig
from langgraph.checkpoint.memory import MemorySaver
from brick_assistant.graphs.abstract_rdf import AbstractWuerthGraphRDF

from brick_assistant.config.configs import AgentConfig

class WuerthVanillaGraphRDF(AbstractWuerthGraphRDF):
    def __init__(self, keys: AgentConfig, llm: Union[str, BaseChatModel] = "openai", checkpointer: MemorySaver = None):
        super().__init__(keys, llm, checkpointer)
        self.build_graph()
        self.compile_graph()
       
    def build_graph(self):
        self.workflow = StateGraph(MessagesState, config_schema=GraphConfig)
        
        # Db Nodes loading
        db_nodes = self.db_tool_nodes
        static_nodes = self.static_tool_nodes
        
        # Add all nodes
        node_funcs = self.node_functions
        
        # Add nodes - mix of functions and direct tool nodes
        self.workflow.add_node("evaluate_user_query", node_funcs['evaluate_user_query'])
        self.workflow.add_node("metadata_keys_call", node_funcs['metadata_keys_call'])
        self.workflow.add_node("tables_or_rdf", node_funcs['tables_or_rdf'])
        self.workflow.add_node("rdf_toolkit", static_nodes['rdf_toolkit'])
        self.workflow.add_node("tables_or_end", node_funcs['tables_or_end'])
        self.workflow.add_node("list_tables_tool", db_nodes['sql_db_list_tables'])
        self.workflow.add_node("call_get_schema", node_funcs['call_get_schema'])
        self.workflow.add_node("get_schema", db_nodes['sql_db_schema'])
        self.workflow.add_node("generate_query", node_funcs['generate_query'])
        self.workflow.add_node("check_query", node_funcs['check_query'])
        self.workflow.add_node("run_query", db_nodes['sql_db_query'])
        
        # Add ONLY the edges that are NOT handled by Commands
        # Start with the entry point - these are fixed sequential flows
        self.workflow.add_edge(START, "metadata_keys_call")
        self.workflow.add_edge("metadata_keys_call", "evaluate_user_query")
        
        # After brick_explore_tool, always go to tables_or_end (fixed flow)
        self.workflow.add_edge("rdf_toolkit", "tables_or_end")
        
        # After list_tables_tool, always proceed through schema retrieval (fixed flow)
        self.workflow.add_edge("list_tables_tool", "call_get_schema")
        self.workflow.add_edge("call_get_schema", "get_schema")
        self.workflow.add_edge("get_schema", "generate_query")
        
        # After check_query, always run the query (fixed flow)
        self.workflow.add_edge("check_query", "run_query")
        self.workflow.add_edge("run_query", "generate_query")
        
        # REMOVED ALL EDGES THAT ARE HANDLED BY COMMANDS:
        # - evaluate_user_query -> tables_or_rdf or END (handled by Command)
        # - tables_or_rdf -> list_tables_tool, brick_explore_tool, or END (handled by Command)
        # - tables_or_end -> list_tables_tool, brick_explore_tool, or END (handled by Command)
        # - generate_query -> check_query, brick_explore_tool, or END (handled by Command)
   
    def run(
        self, input_data: Dict[str, Any], stream: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if "user_prompt" not in input_data:
            raise ValueError("Input data must contain a 'user_prompt' key.")
        
        # Ensure we have messages in the input
        if "messages" not in input_data:
            input_data["messages"] = [{"role": "user", "content": input_data["user_prompt"]}]
        
        if stream:
            events = []
            for event in self.graph.stream(
                input_data, self.config, stream_mode="updates"
            ):
                events.append(event)
            self.result = events[-1] if events else None
            return events
        else:
            self.result = self.graph.invoke(input_data, self.config)
            return self.result