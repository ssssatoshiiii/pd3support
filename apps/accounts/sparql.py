from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import logging

def get_graph():
    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        select ?s ?o
        where {
            ?s pd3:value ?o.
        }
        LIMIT 100"""
    
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/LF/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results["results"]["bindings"]