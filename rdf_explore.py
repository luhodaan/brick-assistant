from rdflib import Graph
import os
from typing import List

#import pkg_resources

def parse_graph(building_name: str) -> Graph:
    """
    Parse the RDF graph for the specified building.
    Args:
        building_name (str): The name of the building to parse.
    Returns:
        Graph: The parsed RDF graph.
    """
    file_path = f"data/ttl_files/bui_{building_name.upper()}.ttl"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TTL file not found: {file_path}")
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

def area_rdf_tool(building_name: str) -> str:
    """
    Create an RDF tool with pre-extracted schema in the docstring.
   
    Args:
        building_name (str): The name of the building to create the tool for.
       
    Returns:
        str: A summary of the schema extraction and tool creation process.
    """    
    g = parse_graph(building_name)

    query = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>

    SELECT ?area_value
    WHERE {
    ?subject brick:hasArea ?value .
    ?value brick:value ?area_value .
    }
    """
    results = g.query(query)

    for row in results:
        if row is None:
            return "No area value found for the building."
        return f"Area of {building_name}: {row['area_value']} square meters."

def temperature_sensors_uuid_rdf_tool(building_name: str) -> str:
    """
    Get the UUID of a specific sensor type in the building.
    Args:
        building_name (str): The name of the building.
        sensor_type (str): The type of sensor to query.
    Returns:
        str: The UUID of the sensor or an error message.
    """
    g = parse_graph(building_name)
    query = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>

    SELECT ?sensor ?uuid ?cls ?location
    WHERE {
    ?sensor a ?cls ;
            brick:hasUUID ?uuid .
    FILTER STRENDS(STR(?cls), "Temperature_Sensor")
    ?sensor brick:isPointOf ?location .
    }
    """
    results = g.query(query)

    sensors: List[str] = []

    if not results:
        return f"No sensor of type temperature found in {building_name}."

    for row in results:
        sensors.append(
            f"Sensor UUID for {row['sensor']} of type {row['cls']} in {building_name}: {row['uuid']} located at: {row['location']}"
        )

    return "\n".join(sensors)


def zones_rdf_tool(building_name: str) -> str:
    """
    Get the zones in the building.
    Args:
        building_name (str): The name of the building.
    Returns:
        str: A list of zones or an error message.
    """
    g = parse_graph(building_name)
    query = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>

    SELECT ?zone ?building
    WHERE {
    ?zone a brick:Zone .
    ?zone brick:isPartOf ?building .
    }
    """
    results = g.query(query)
    zones: List[str] = []

    if not results:
        return f"No zones found in {building_name}."
    for row in results:
        zones.append(f"Zone: {row['zone']} in: {row['building']}")
    return "\n".join(zones)


def generic_sensors_rdf_tool(building_name: str) -> str:
    """
    Get sensors in the building, useful in case we do not know what type of sensors are present specifically.
    Args:   
        building_name (str): The name of the building.
    Returns:
        str: A list of sensors or an error message. 
    """
    g = parse_graph(building_name)
    query = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>

    SELECT ?sensor ?uuid ?cls ?location
    WHERE {
    ?sensor a ?cls ;
            brick:hasUUID ?uuid .
    FILTER STRENDS(STR(?cls), "Sensor")
    ?sensor brick:isPointOf ?location .
    }
    """
    results = g.query(query)
    sensors: List[str] = []
    if not results:
        return f"No sensors found in {building_name}."
    for row in results:
        sensors.append(
            f"Sensor UUID for {row['sensor']} of type {row['cls']} in {building_name}: {row['uuid']} located at: {row['location']}"
        )
    return "\n".join(sensors)

def meters_rdf_tool(building_name: str) -> str:
    """
    Get all meters in the building.
    Args:   
        building_name (str): The name of the building.
    Returns:
        str: A list of sensors or an error message. 
    """
    g = parse_graph(building_name)
    query = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>

    SELECT ?meter ?uuid ?cls ?location
    WHERE {
    ?meter a ?cls ;
            brick:hasUUID ?uuid .
    FILTER STRENDS(STR(?cls), "Meter")
    ?meter brick:feeds ?location .
    }
    """
    results = g.query(query)
    meters: List[str] = []
    if not results:
        return f"No meters found in {building_name}."
    for row in results:
        meters.append(
            f"Meters UUID for {row['meters']} of type {row['cls']} in {building_name}: {row['uuid']} located at: {row['location']}"
        )
    return "\n".join(meters)

