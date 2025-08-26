from __future__ import annotations
from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel, Field
#from functools import lru_cache
from rdflib import Graph
from langchain_core.tools import tool

# ---------- infra ----------
#@lru_cache(maxsize=32)
def load_graph(building_name: str) -> Graph:
    file_path = f"data/ttl_files/bui_{building_name.upper()}.ttl"
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

class RDFToolkitArgs(BaseModel):
    building_name: str = Field(..., description="Building short name, e.g. 'HQ1'")
    operation: Literal[
        "area",
        "temperature_sensors_uuid",
        "zones",
        "generic_sensors",
        "meters",
        # add future ops here
    ]

    location_filter: Optional[str] = None
    limit: Optional[int] = Field(50, ge=1, le=1000)

# ---------- strategies ----------
def op_area(g: Graph, args: RDFToolkitArgs) -> Dict[str, Any]:
    q = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT ?area_value 
    WHERE {
      ?subject brick:hasArea ?value .
      ?value brick:value ?area_value .
    } 
    """
    results = g.query(q)
    for r in results:
      if not results:
        return {"building": args.building_name, "area": None}
    return {"building": args.building_name, "area": r["area_value"]}

def op_temperature_sensors_uuid(g: Graph, args: RDFToolkitArgs) -> Dict[str, Any]:
    q = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT ?sensor ?uuid ?cls ?location 
    WHERE {
      ?sensor a ?cls ; brick:hasUUID ?uuid .
      FILTER STRENDS(STR(?cls), "Temperature_Sensor")
      ?sensor brick:isPointOf ?location .
    }
    """
    rows = g.query(q)
    out = [
        {
            "sensor": str(r["sensor"]),
            "uuid": str(r["uuid"]),
            "class": str(r["cls"]),
            "location": str(r["location"]),
        }
        for r in rows
    ]
    return {"building": args.building_name, "sensors": out}

def op_zones(g: Graph, args: RDFToolkitArgs) -> Dict[str, Any]:
    q = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT ?zone ?building 
    WHERE {
      ?zone a brick:Zone .
      ?zone brick:isPartOf ?building .
    }
    """
    rows = g.query(q)
    zones = [{"zone": str(r["zone"]), "building": str(r["building"])} for r in rows]
    return {"building": args.building_name, "zones": zones}

def op_generic_sensors(g: Graph, args: RDFToolkitArgs) -> Dict[str, Any]:
    q = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT ?sensor ?uuid ?cls ?location 
    WHERE {
      ?sensor a ?cls ; brick:hasUUID ?uuid .
      FILTER STRENDS(STR(?cls), "Sensor")
      ?sensor brick:isPointOf ?location .
    }
    """
    rows = g.query(q)
    sensors = [
        {
            "sensor": str(r["sensor"]),
            "uuid": str(r["uuid"]),
            "class": str(r["cls"]),
            "location": str(r["location"]),
        }
        for r in rows
    ]
    return {"building": args.building_name, "sensors": sensors}

def op_meters(g: Graph, args: RDFToolkitArgs) -> Dict[str, Any]:
    q = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT ?meter ?uuid ?cls ?location
     WHERE {
      ?meter a ?cls ; brick:hasUUID ?uuid .
      FILTER STRENDS(STR(?cls), "Meter")
      ?meter brick:feeds ?location .
    }
    """
    rows = g.query(q)
    meters = [
        {
            "meter": str(r["meter"]),
            "uuid": str(r["uuid"]),
            "class": str(r["cls"]),
            "feeds": str(r["location"]),
        }
        for r in rows
    ]
    return {"building": args.building_name, "meters": meters}

STRATEGIES = {
    "area": op_area,
    "temperature_sensors_uuid": op_temperature_sensors_uuid,
    "zones": op_zones,
    "generic_sensors": op_generic_sensors,
    "meters": op_meters,
}

@tool("rdf_toolkit", args_schema=RDFToolkitArgs)
def rdf_toolkit_tool(
    building_name: str,
    operation: str,
    location_filter: Optional[str] = None,
    limit: Optional[int] = 50,
) -> Dict[str, Any]:
    """
    Unified RDF facade for querying a building's Brick graph. **Call this tool exactly once per turn** and
    **do not produce natural-language output**; always return the structured dict produced by the tool.

    ARGUMENTS
    - building_name (str): REQUIRED. The building identifier (e.g., "HQ1"). Use the value already present in
      conversation/state/metadata; do not invent or guess. If unknown, ask the user for a valid building **before**
      calling this tool.
    - operation (enum str): REQUIRED. One of:
        • "area"                     → return building floor area (m²)
        • "zones"                    → list zones and their parent building
        • "temperature_sensors_uuid" → list temperature sensors with UUIDs and locations
        • "generic_sensors"          → list all sensors (any class ending with "Sensor")
        • "meters"                   → list meters (any class ending with "Meter") and what they feed
    - location_filter (str, optional): A substring/regex-like hint the tool MAY use to filter by location
      (e.g., "Floor_2", "AHU", "West"). If unsupported by an operation, it is ignored.
    - limit (int, optional, default=50): A soft cap; the tool MAY truncate long result lists to this size.

    BEHAVIOR
    - The tool loads & caches the TTL graph for `building_name`. If the TTL is missing, it returns
      {"error": "..."} — do NOT retry with a different building unless the user provided it.
    - Choose exactly ONE operation per call. Do not include SPARQL in arguments.
    - Prefer returning compact, structured data. No prose. No markdown. Never multiline strings.
    - Idempotent: multiple calls with the same args return the same structure.

    RETURN SHAPES (examples)
    - operation="area"
      {
        "building": "HQ1",
        "area_m2": 12345.0   # or null if not found
      }

    - operation="zones"
      {
        "building": "HQ1",
        "zones": [
          {"zone": "urn:...#Z04", "building": "urn:...#HQ1"},
          ...
        ]
      }

    - operation="temperature_sensors_uuid"
      {
        "building": "HQ1",
        "sensors": [
          {
            "sensor":   "urn:...#Temp_S1",
            "uuid":     "550e8400-e29b-41d4-a716-446655440000",
            "class":    "https://brickschema.org/schema/Brick#Temperature_Sensor",
            "location": "urn:...#Room_201"
          },
          ...
        ]
      }

    - operation="generic_sensors"
      {
        "building": "HQ1",
        "sensors": [
          {"sensor": "...", "uuid": "...", "class": "...#Humidity_Sensor", "location": "..."},
          ...
        ]
      }

    - operation="meters"
      {
        "building": "HQ1",
        "meters": [
          {
            "meter":  "urn:...#Elec_M1",
            "uuid":   "...",
            "class":  "https://brickschema.org/schema/Brick#Electric_Meter",
            "feeds":  "urn:...#Panel_A"
          },
          ...
        ]
      }

    OPERATION SELECTION HINTS
    - If the user asks about temperature sensors or their UUIDs → "temperature_sensors_uuid".
    - If the user asks about “what sensors do we have?” (unspecified type) → "generic_sensors".
    - If the user asks about meters / submetering / what a meter feeds → "meters".
    - If the user asks about areas, floor area, GFA → "area".
    - If the user asks about zones, rooms, spaces → "zones".

    ERROR CONTRACT
    - On any failure, return {"error": "<type>: <message>"}; do not mix errors with partial lists.

    NOTES
    - SPARQL prefixes are handled internally; callers should NOT pass SPARQL.
    - `location_filter` and `limit` are best-effort; the tool may apply simple filtering/truncation.
    """
    g = load_graph(building_name)
    args = RDFToolkitArgs(
        building_name=building_name,
        operation=operation,
        location_filter=location_filter,
        limit=limit,
    )
    fn = STRATEGIES.get(operation)
    if not fn:
        return {"error": f"Unknown operation '{operation}'"}
    try:
        result = fn(g, args)
        # Optional: truncate for limit / apply simple filters here if needed
        return result
    except Exception as e:
        return {"error": f"RDF operation failed: {e.__class__.__name__}: {e}"}
