from typing import Dict, Optional, List, Tuple
import json
import os
from rdflib import Graph, BNode
from langchain.tools import BaseTool  
from brick_assistant.config import settings

class BrickExploration(BaseTool):
    name: str = "brick_explore_tool"
    description: str = """
Analyzes Brick schema TTL files to extract blank node patterns and predicate usage, enabling structured SPARQL query generation. Automatically detects nested RDF structures (e.g., 'brick:hasLocation → [brick:value]') and provides schema insights. Essential for querying building automation data with complex blank node relationships. Always includes required Brick and building prefixes in outputs.

Key capabilities:
- Identifies all classes and predicates in Brick schema files
- Identifies blank nodes and extracts their inner predicates and objects
- Reveals nested property patterns for query formulation
- Handles building-specific TTL file paths dynamically

Use this tool to:
1. Understand the structure of Brick schema TTL files
2. Generate proper SPARQL queries 
3. Get schema metadata before constructing complex queries

Example patterns detected:
- brick:hasLocation → {brick:value}
- brick:hasCoordinates → {brick:latitude, brick:longitude}
"""

    def _run(self, building: str) -> str:
        file_path = settings.TTL_FILES_PATH / f"bui_{building.upper()}.ttl"        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TTL file not found: {file_path}")
        
        g = Graph()
        g.parse(file_path, format="turtle")
        
        results: List[Tuple[str, str, str]] = []
        for subj, predicate, obj in g:
            if isinstance(obj,BNode):
                for inner_subj, inner_pred, inner_obj in g.triples((obj,None,None)):
                    results.append((f"This is the inner subject {inner_subj}", f"This is the inner predicate {inner_pred}", f"This is the object {inner_obj}"))
            results.append((f"This is the subject {subj}", f"This is the predicate {predicate}", f"This is the object {obj}"))
            output = json.dumps(results)
            
        return output