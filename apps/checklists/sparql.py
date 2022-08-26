from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import logging

def get_deslist(epType):

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dcterms:<http://purl.org/dc/terms/>

    SELECT ?graph ?title 
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
    results_title = list()
    for result in converted_results["results"]["bindings"]:
        results_graph.append(str(result['graph']['value']))
        results_title.append(str(result['title']['value']))

    return results_graph, results_title

def get_lld_list(gpm_graph_uri):
    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dcterms:<http://purl.org/dc/terms/>

    SELECT ?lld_graph_uri ?lld_graph_title
    WHERE{
        GRAPH ?g{
            ?lld_graph_uri pd3:epUses <""" + gpm_graph_uri + """>;
                         dcterms:title ?lld_graph_title.
            }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()

    results_graph = list()
    results_title = list()
    for result in converted_results["results"]["bindings"]:
        results_graph.append(str(result['lld_graph_uri']['value']))
        results_title.append(str(result['lld_graph_title']['value']))

    return results_graph, results_title

def get_GPM_entity(gpm_graph_uri):
    #LLD作成のために、必要な要素を全て獲得
    query="""PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dcterms:<http://purl.org/dc/terms/>
    
    SELECT ?s ?p ?o
    WHERE{
        GRAPH <""" + gpm_graph_uri + """>{
            {
                ?s rdf:type pd3:Action.
                {
                    ?s ?p ?o
                    FILTER (?p = rdf:type || ?p = pd3:actionType || ?p = pd3:expansion || ?p = pd3:layer || ?p = pd3:output || ?p = pd3:value || ?p = pd3:attribution)
                }
                UNION
                {
                    ?s ?p ?o
                    FILTER (?p = pd3:input)
                    {?o rdf:type pd3:Flow}
                    UNION
                    {?o rdf:type pd3:ContainerFlow}
                }
            }
            UNION
            {
                ?s rdf:type pd3:Flow.
                ?s ?p ?o.
                FILTER (?p = rdf:type || ?p = pd3:arcType || ?p = pd3:layer || ?p = pd3:source || ?p = pd3:target || ?p = pd3:value)
            }
            UNION
            {
                ?s rdf:type pd3:Container.
                    {
                        ?s ?p ?o
                        FILTER (?p = rdf:type || ?p = pd3:containerType || ?p = pd3:contraction || ?p = pd3:layer || ?p = pd3:output || ?p = pd3:value)
                    }
                    UNION
                    {
                        ?s ?p ?o
                        FILTER (?p = pd3:member)
                        {?o rdf:type pd3:Action}
                        UNION
                        {?o rdf:type pd3:Flow}
                    }
            }
            UNION
            {
                ?s rdf:type pd3:ContainerFlow.
                ?s ?p ?o
                FILTER(?p = rdf:type || ?p = pd3:arcType || ?p = pd3:layer || ?p = pd3:source || ?p = pd3:target || ?p = pd3:value)
            }           
        }
    } 
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()
    result = list()
    for conresult in converted_results["results"]["bindings"]:
        if(conresult['s']['type']=='uri'):
            s = URIRef(conresult['s']['value'])
        elif(conresult['s']['type']=='literal'):
            s = Literal(conresult['s']['value'])

        if(conresult['p']['type']=='uri'):
            p = URIRef(conresult['p']['value'])
        elif(conresult['p']['type']=='literal'):
            p = Literal(conresult['p']['value'])

        if(conresult['o']['type']=='uri'):
            o = URIRef(conresult['o']['value'])
        elif(conresult['o']['type']=='literal'):
            o = Literal(conresult['o']['value'])
                
        result.append([s, p, o])
    
    urilist = list(set([elem[0] for elem in result]))
    
    return result, urilist



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



def get_detail_action(action, gpm_graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?target ?value
        WHERE {
            GRAPH<""" + str(gpm_graph_uri) + """>{
        
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


#value, intention, toolknowledge, annotation, rationale, outputのuriとvalueを取得
def action_supinfo(action_uri, graph_uri):
    #valueの取得
    query_value = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?value
            WHERE {
                GRAPH <""" + graph_uri +""">{
            
            <""" + action_uri + """> pd3:value ?value.
            }
            }"""
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_value)
    sparql.setReturnFormat(JSON)
    conresult = sparql.query().convert()["results"]["bindings"]
    if(len(conresult) != 0):
        action_result = {'action_uri': action_uri, 'action_value': conresult[0]["value"]["value"]}
    else:
        action_result = {'action_uri': '', 'action_value': ''}

    #意図の取得
    query_intention = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?intention_uri ?intention_value
        WHERE {
            GRAPH <""" + graph_uri +""">{
        
        <""" + action_uri + """> pd3:input ?intention_uri.
        ?intention_uri pd3:arcType "intention";
            pd3:value ?intention_value.
        
        }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_intention)
    sparql.setReturnFormat(JSON)
    conresult = sparql.query().convert()["results"]["bindings"]
    if(len(conresult) != 0):
        intention_result = {'intention_uri': conresult[0]["intention_uri"]["value"] ,'intention_value': conresult[0]["intention_value"]["value"]}
    else:
        intention_result = {'intention_uri': '', 'intention_value': ''}

    #知識道具の取得
    query_toolknowledge = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?toolknowledge_uri ?toolknowledge_value
        WHERE {
            GRAPH <""" + graph_uri +""">{
        
        <""" + action_uri + """> pd3:input ?toolknowledge_uri.
        ?toolknowledge_uri pd3:arcType "tool/knowledge";
            pd3:value ?toolknowledge_value.
        
        }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_toolknowledge)
    sparql.setReturnFormat(JSON)
    conresult = sparql.query().convert()["results"]["bindings"]
    if(len(conresult) != 0):
        toolknowledge_result = {'toolknowledge_uri': conresult[0]["toolknowledge_uri"]["value"] ,'toolknowledge_value': conresult[0]["toolknowledge_value"]["value"]}
    else:
        toolknowledge_result = {'toolknowledge_uri': '', 'toolknowledge_value': ''}

    #注釈の取得
    query_annotation = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?annotation_uri ?annotation_value
        WHERE {
            GRAPH <""" + graph_uri +""">{
        
        <""" + action_uri + """> pd3:input ?annotation_uri.
        ?annotation_uri pd3:arcType "annotation";
            pd3:value ?annotation_value.
        
        }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_annotation)
    sparql.setReturnFormat(JSON)
    conresult = sparql.query().convert()["results"]["bindings"]
    if(len(conresult) != 0):
        annotation_result = {'annotation_uri': conresult[0]["annotation_uri"]["value"] ,'annotation_value': conresult[0]["annotation_value"]["value"]}
    else:
        annotation_result = {'annotation_uri': '', 'annotation_value': ''}

    #導出根拠の取得
    query_rationale = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?rationale_uri ?rationale_value
        WHERE {
            GRAPH <""" + graph_uri +""">{
        
        <""" + action_uri + """> pd3:input ?rationale_uri.
        ?rationale_uri pd3:arcType "rationale";
            pd3:value ?rationale_value.
        
        }
        }"""

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_rationale)
    sparql.setReturnFormat(JSON)
    conresult = sparql.query().convert()["results"]["bindings"]
    if(len(conresult) != 0):
        rationale_result = {'rationale_uri': conresult[0]["rationale_uri"]["value"] ,'rationale_value': conresult[0]["rationale_value"]["value"]}
    else:
        rationale_result = {'rationale_uri': '', 'rationale_value': ''}

    #出力の取得
    query_output = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
             PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?output_uri ?output_value
        WHERE {
            GRAPH<""" + graph_uri + """>{
        
        <""" + action_uri + """> pd3:output ?output_uri.
        ?output_uri pd3:value ?output_value.
        }
        }"""
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query_output)
    sparql.setReturnFormat(JSON)
    conresult = sparql.query().convert()["results"]["bindings"]
    if(len(conresult) != 0):
        output_result = {'output_uri': conresult[0]["output_uri"]["value"], 'output_value':conresult[0]["output_value"]["value"]}
    else:
        output_result = {'output_uri': '', 'output_value': ''}

    return action_result, intention_result, toolknowledge_result, annotation_result, rationale_result, output_result



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

#現在作成中のログレベルの記述に紐づいたGPMのアクションを取得
def get_gpm_action(action_uri, gpm_graph_uri):

    print(type(action_uri))
    query="""PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    
    SELECT ?gpm_action_uri
    WHERE{
        GRAPH <""" + str(gpm_graph_uri) + """>{
            ?gpm_action_uri pd3:isUsedBy <""" + action_uri + """>.
        }
    }
    """

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    converted_results = sparql.query().convert()["results"]["bindings"]
    return converted_results[0]['gpm_action_uri']["value"]

#GPMのアクションと紐づいたアクションを全て取得
def get_lld_action2(action_uri, gpm_graph_uri):
    query="""PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    
    SELECT ?g ?lld_action_uri
    WHERE{
        GRAPH ?g{
            {?lld_action_uri pd3:uses <""" + action_uri + """>}
            UNION
            {?lld_action_uri pd3:derives <"""+ action_uri +""">}
        }
    }
    """

    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    converted_results = sparql.query().convert()["results"]["bindings"]
    results_graph_uri = []
    results_action_uri =[]
    for converted_result in converted_results:
        results_graph_uri.append(converted_result["g"]["value"])
        results_action_uri.append(converted_result["lld_action_uri"]["value"])
    print(results_action_uri)

    return results_graph_uri, results_action_uri

#アクションの入力の情報矢印のURIを取得
def get_input_flow(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    
    SELECT ?input
    WHERE{
        GRAPH<""" + graph_uri + """>{
            <""" + action_uri + """> pd3:input ?input.
            ?input rdf:type pd3:Flow.
        }
    }
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results = []
    for converted_result in converted_results:
        results.append(converted_result["input"]["value"])
    return results

#アクションの出力の情報矢印のURIを取得
def get_output_flow(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    
    SELECT ?output
    WHERE{
        GRAPH<""" + graph_uri + """>{
            <""" + action_uri + """> pd3:output ?output.
            ?output rdf:type pd3:Flow.
        }
    }
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results = []
    for converted_result in converted_results:
        results.append(converted_result["output"]["value"])
    return results

#アクションの次のアクションのURIを取得
def get_nextaction(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    
    SELECT ?nextaction
    WHERE{
        GRAPH<""" + graph_uri + """>{
            <""" + action_uri + """> pd3:output ?output.
            ?output rdf:type pd3:Flow.
            ?output pd3:target ?nextaction.
        }
    }"""
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results = []
    for converted_result in converted_results:
        results.append(converted_result["nextaction"]["value"])
    return results

#コンテナのURIを取得
def get_container(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    
    SELECT ?container
    WHERE{
        GRAPH<""" + graph_uri + """>{
            <""" + action_uri + """> pd3:attribution ?container.
            ?container rdf:type pd3:Container.
        }
    }
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    if(len(converted_results) != 0):
        return converted_results[0]["container"]["value"]
    else:
        return ''
