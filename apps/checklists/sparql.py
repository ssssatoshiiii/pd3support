from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import logging

def get_graph():
    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?target (SAMPLE(?value1) AS ?value)  (COUNT (?inter_action) AS ?distance)
    WHERE{
        GRAPH <http://digital-triplet.net:3030/test>{
            ?start pd3:actionType "start";
        MINUS{
        ?start pd3:attribution ?o.
        }
        
        ?start (pd3:output/pd3:target)* ?inter_action.
        ?inter_action (pd3:output/pd3:target)+ ?target.
        ?target pd3:value ?value1.
        MINUS{
            ?target pd3:actionType "end".
        }
        }
    }
    GROUP BY ?target
    ORDER BY ?distance
        """
    
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()
    results_uri = list()
    results_value = list()
    for result in converted_results["results"]["bindings"]:
        results_uri.append(str(result['target']['value']))
        results_value.append(str(result['value']['value']))

    return results_value,results_uri



def get_detail_action(action):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?target ?value
        WHERE {
            GRAPH<http://digital-triplet.net:3030/test>{
        
        <""" + action + """> pd3:expansion/pd3:member ?start.
        ?start pd3:actionType "start".
        
        ?start (pd3:output/pd3:target)+ ?target.
        ?target pd3:value ?value.
        MINUS{
            ?target pd3:actionType "end".
        }
        }
        }"""
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()
    results_uri = list()
    results_value = list()
    # results = list()
    for result in converted_results["results"]["bindings"]:
        results_uri.append(str(result['target']['value']))
        results_value.append(str(result['value']['value']))

    return results_value, results_uri

def action_supinfo(uri):
    #意図の取得
    query_intention = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?intention
        WHERE {
            GRAPH <http://digital-triplet.net:3030/test>{
        
        <""" + uri + """> pd3:input ?input.
        ?input pd3:arcType "intention";
            pd3:value ?intention.
        
        }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_intention)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()["results"]["bindings"]
    if(len(result)!= 0):
        intention = result[0]["intention"]["value"]
    else:
        intention = ""

    #知識道具の取得
    query_toolknowledge = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?toolknowledge
        WHERE {
        GRAPH <http://digital-triplet.net:3030/test>{
        <""" + uri + """> pd3:input ?input.
        ?input pd3:arcType "tool/knowledge";
            pd3:value ?toolknowledge.
        }
        }"""
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_toolknowledge)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()["results"]["bindings"]
    if(len(result)!= 0):
        toolknowledge = result[0]["toolknowledge"]["value"]
    else:
        toolknowledge = ""

    query_annotation = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?annotation
        WHERE {
            GRAPH<http://digital-triplet.net:3030/test>{
        
        <""" + uri + """> pd3:input ?input.
        ?input pd3:arcType "annotation";
            pd3:value ?annotation.
        }
        }"""
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_annotation)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()["results"]["bindings"]
    if(len(result)!=0):
        annotation = result[0]["annotation"]["value"]
    else:
        annotation = ""

    return intention, toolknowledge, annotation