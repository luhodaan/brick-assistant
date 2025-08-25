import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional

from langchain.chat_models.base import BaseChatModel
from langgraph.graph import StateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import ToolNode

from wuerth_agent.helpers.llm_models import _get_llm
from wuerth_agent.tools.tools import BrickExploration
from wuerth_agent.config import settings

class AbstractWuerthGraph(ABC):
    def __init__(self, llm: Union[str, BaseChatModel] = "openai", checkpointer: Optional[BaseCheckpointSaver]= None):
        self.model = _get_llm(llm)
        self.workflow = None
        self.graph = None
        self.checkpointer = checkpointer
        self.config = {"configurable": {"thread_id":"1","llm_model":self.model}}
        self.result = None
        self._db_toolkit = None
        self._db_tool_nodes = None
        self._db_tools_func = None
        self._static_tool_nodes = None
        self._node_functions = None

    @property
    def db_toolkit(self):
        """Lazy load the SQLDatabaseToolkit."""
        if self._db_toolkit is None:
            #try:
            db = SQLDatabase.from_uri("postgresql+psycopg2://user:password@localhost:25432/store_data")
                #db = SQLDatabase.from_uri(settings.get_database_uri())
            # except ValueError as e:
            #     # Fallback for local development if DATABASE_URI is not set
            #     print(f"Warning: {e}. Using fallback database connection.")
                #db = SQLDatabase.from_uri("postgresql+psycopg2://user:password@localhost:25432/store_data")
            self._db_toolkit = SQLDatabaseToolkit(db=db, llm=self.model)
        return self._db_toolkit
    
    @property
    def db_tools(self):
        """
        Get the tools from the SQLDatabaseToolkit.
        
        Returns:
            List: A list of tools available in the SQLDatabaseToolkit.
        """
        return self.db_toolkit.get_tools()
    
    @property
    def db_tool_nodes(self) -> Dict[str, ToolNode]:
        """Get tool nodes for database tools indexed by tool name."""
        if self._db_tool_nodes is None:
            self._db_tool_nodes = {}
        if self._db_tools_func is None:
            self._db_tools_func = {}
            for tool in self.db_tools:
                self._db_tool_nodes[tool.name] = ToolNode([tool], name=tool.name)
                self._db_tools_func[tool.name] = tool
        return self._db_tool_nodes
    
    @property
    def static_tool_nodes(self) -> Dict[str, ToolNode]:
        """Get tool nodes for static tools."""
        if self._static_tool_nodes is None:
            brick_explore_tool=BrickExploration()
            self._static_tool_nodes = {
                'brick_explore_tool': ToolNode([brick_explore_tool], name="brick_explore_tool")
            }
        return self._static_tool_nodes
    
    @property
    def node_functions(self) -> Dict[str, callable]:
        """Create and cache node functions with dependencies injected."""
        if self._node_functions is None:
            self._node_functions = self._create_node_functions()
        return self._node_functions
    
    def _create_node_functions(self) -> Dict[str, callable]:
        """Create wrapper functions with LLM and ToolNode instances bound."""
        
        # Import your functions
        from wuerth_agent.tools.functions import (
            evaluate_user_query,
            call_get_schema,
            generate_query,
            check_query,
            tables_or_rdf,
            tables_or_end,
            enforced_metadata_keys_call
        )
        
        # Get tool nodes
        db_tools = self._db_tools_func
        db_nodes = self.db_tool_nodes
        static_nodes = self.static_tool_nodes
        
        # Create wrapper functions with dependencies injected
        def evaluate_user_query_wrapper(state):
            return evaluate_user_query(state, self.model)
        
        def call_get_schema_wrapper(state):
            return call_get_schema(state, self.model, db_tools['sql_db_schema'])
        
        def generate_query_wrapper(state):
            return generate_query(
                state, 
                self.model, 
                db_tools['sql_db_query'], 
                BrickExploration() 
            )
        
        def check_query_wrapper(state):
            return check_query(state, self.model, db_tools['sql_db_query'])
        
        def tables_or_rdf_wrapper(state):
            return tables_or_rdf(
                state, 
                self.model, 
                db_tools['sql_db_list_tables'], 
                BrickExploration() 
            )
        
        def tables_or_end_wrapper(state):
            return tables_or_end(
                state, 
                self.model, 
                db_tools['sql_db_list_tables'], 
                BrickExploration() 
            )
        
        def metadata_keys_call_wrapper(state):
            return enforced_metadata_keys_call(
                state
            )
        
        return {
            'evaluate_user_query': evaluate_user_query_wrapper,
            'call_get_schema': call_get_schema_wrapper,
            'generate_query': generate_query_wrapper,
            'check_query': check_query_wrapper,
            'tables_or_rdf': tables_or_rdf_wrapper,
            'tables_or_end': tables_or_end_wrapper,
            'metadata_keys_call': metadata_keys_call_wrapper,
        }

        
    @abstractmethod
    def build_graph(self):
        """
        Abstract method to build the graph. This should be implemented by subclasses.
        """
        pass

    def compile_graph(self):
        """
        Compile the graph using the workflow and configuration.
        """
        try:
            if self.checkpointer:
                self.graph = self.workflow.compile(checkpointer=self.checkpointer)
            else:
                self.graph = self.workflow.compile()
        except Exception as e:
            raise ValueError(f"Failed to compile the graph: {e}")
        
    def _compiled_graph(self) -> StateGraph:
        """
        Returns the compiled graph.
        
        Returns:
            StateGraph: The compiled state graph. 
        """
        if self.graph is None:
            raise ValueError("Graph has not been compiled yet. Call compile_graph() first.")
        return self.graph
    
    def _set_up_development_environment(self):
        """
        Set up the development environment for the graph.
        This method can be overridden by subclasses to customize the setup.
        """
        # Default implementation does nothing
        os.getenv
        
    @abstractmethod
    def run(self, input_data: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run the graph with the provided input data.
        
        Args:
            input_data (Dict[str, Any]): The input data for the graph.
        
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: The output data and the history of states.
        """
        pass