from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import logging

def get_graph():
    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?target (SAMPLE(?value1) AS ?value)  (COUNT (?inter_action) AS ?distance)
    WHERE{
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
        
        <""" + action + """> pd3:expansion/pd3:member ?start.
        ?start pd3:actionType "start".
        
        ?start (pd3:output/pd3:target)+ ?target.
        ?target pd3:value ?value.
        MINUS{
            ?target pd3:actionType "end".
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

