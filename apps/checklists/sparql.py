from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import logging

def get_deslist(epType):

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dcterms:<http://purl.org/dc/terms/>

    SELECT ?graph ?description ?title 
    WHERE{
        GRAPH ?graph{
            ?description pd3:epType '""" + epType + """';
                         dcterms:title ?title.
            }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()
    results_graph = list()
    results_description = list()
    results_title = list()
    for result in converted_results["results"]["bindings"]:
        results_graph.append(str(result['graph']['value']))
        results_description.append(str(result['description']['value']))
        results_title.append(str(result['title']['value']))

    return results_graph, results_description, results_title



def get_graph(gpm_graph_uri):
    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?target (SAMPLE(?value1) AS ?value)  (COUNT (?inter_action) AS ?distance)
    WHERE{
        GRAPH <""" + str(gpm_graph_uri) + """>{
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
    
    print(results_value)

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

def action_supinfo(uri, gpm_graph_uri):
    #意図の取得
    query_intention = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?intention
        WHERE {
            GRAPH <""" + gpm_graph_uri +""">{
        
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

def get_hier_actions(uri, gpm_graph_uri):
    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?contractedActionUri (COUNT (?inter_action) AS ?distance)
    WHERE{
        GRAPH <""" + str(gpm_graph_uri) + """>{
            <""" + uri + """> (pd3:attribution/pd3:contraction)* ?inter_action.
            ?inter_action (pd3:attribution/pd3:contraction)* ?contractedActionUri.
        }
    }
    GROUP BY ?contractedActionUri
    ORDER BY DESC(?distance)    
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results =[]
    for converted_result in converted_results:
        results.append(converted_result["contractedActionUri"]["value"])

    return results