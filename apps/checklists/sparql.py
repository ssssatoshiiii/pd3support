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

#記述のメタデータの取得
def get_description_metainfo(graph_uri):
    query="""PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX dcterms:<http://purl.org/dc/terms/>
    
    SELECT ?title
    WHERE{
        GRAPH<"""+graph_uri+""">{
            <"""+graph_uri+"""> dcterms:title ?title.
        }
    }
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()["results"]["bindings"]
    if(len(result)!=0):
        title = result[0]["title"]["value"]
    else:
        title = ""

    query1="""PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX dcterms:<http://purl.org/dc/terms/>
    
    SELECT ?creator ?description
    WHERE{
        GRAPH<"""+graph_uri+""">{
            <"""+graph_uri+"""> dcterms:creator ?creator.
        }
    }
    """
    sparql1 = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql1.setQuery(query1)
    sparql1.setReturnFormat(JSON)
    result1 = sparql1.query().convert()["results"]["bindings"]
    if(len(result1)!= 0):
        creator = result1[0]["creator"]["value"]
    else:
        creator = ""
    
    query2="""PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dcterms:<http://purl.org/dc/terms/>
    
    SELECT ?creator ?description
    WHERE{
        GRAPH<"""+graph_uri+""">{
            <"""+graph_uri+"""> dcterms:description ?description.
        }
    }
    """
    sparql2 = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql2.setQuery(query2)
    sparql2.setReturnFormat(JSON)
    result2 = sparql2.query().convert()["results"]["bindings"]
    if(len(result2)!=0):
        description = result2[0]["description"]["value"]
    else:
        description = ""
    return title, creator, description

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

#始点となるアクションと終点となるアクションを指定して、その間のアクション、情報矢印、コンテナを全て取得
def get_GPM_part_entity(gpmstart_action_uri, lldend_action_uri, graph_uri):

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?s ?p ?o
        WHERE
        {GRAPH<"""+graph_uri+""">
        {{  ?end_action_uri pd3:isUsedBy <"""+ lldend_action_uri +""">.
            <"""+ gpmstart_action_uri +"""> (pd3:output/pd3:target)* ?action.
            ?action (pd3:output/pd3:target)* ?end_action_uri.
            ?s ?p ?o.
            FILTER (?s = ?action)
            FILTER (?p = rdf:type || ?p = pd3:actionType || ?p = pd3:expansion || ?p = pd3:layer || ?p = pd3:output || ?p = pd3:value || ?p = pd3:attribution)
        }
        UNION{
            ?end_action_uri pd3:isUsedBy <"""+ lldend_action_uri +""">.
            <"""+gpmstart_action_uri+"""> (pd3:output/pd3:target)* ?action.
                ?action (pd3:output/pd3:target)* ?end_action_uri.
            ?action pd3:output ?s.
            ?s rdf:type pd3:Flow.
            ?s ?p ?o.
            FILTER (?p = rdf:type || ?p = pd3:arcType || ?p = pd3:layer || ?p = pd3:source || ?p = pd3:target || ?p = pd3:value)
        }
        UNION{
            ?end_action_uri pd3:isUsedBy <"""+ lldend_action_uri +""">.
            <"""+gpmstart_action_uri+"""> (pd3:output/pd3:target)* ?action.
                ?action (pd3:output/pd3:target)* ?end_action_uri.
            ?action pd3:expansion/(pd3:member/pd3:expansion)* ?s.
            ?s rdf:type pd3:Container.
            {           ?s ?p ?o
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
        UNION{
            ?end_action_uri pd3:isUsedBy <"""+ lldend_action_uri +""">.
            <"""+gpmstart_action_uri+"""> (pd3:output/pd3:target)* ?action.
                ?action (pd3:output/pd3:target)* ?end_action_uri.
            ?action pd3:expansion/(pd3:member/pd3:expansion)* ?container.
            ?container rdf:type pd3:Container;
               pd3:output ?s.
            ?s rdf:type pd3:ContainerFlow.
            ?s ?p ?o.
            FILTER(?p = rdf:type || ?p = pd3:arcType || ?p = pd3:layer || ?p = pd3:source || ?p = pd3:target || ?p = pd3:value)
        }
        UNION{
            ?end_action_uri pd3:isUsedBy <"""+ lldend_action_uri +""">.
            <"""+gpmstart_action_uri+"""> (pd3:output/pd3:target)* ?action.
                ?action (pd3:output/pd3:target)* ?end_action_uri.
            ?action pd3:expansion/(pd3:member/pd3:expansion)* ?container.
            ?container rdf:type pd3:Container.
            ?container pd3:member ?s.
            ?s rdf:type ?type.
            FILTER (?type = pd3:Action)
            ?s ?p ?o.
            FILTER (?p = rdf:type || ?p = pd3:actionType || ?p = pd3:expansion || ?p = pd3:layer || ?p = pd3:output || ?p = pd3:value || ?p = pd3:attribution)
        }
        UNION{
            ?end_action_uri pd3:isUsedBy <"""+ lldend_action_uri +""">.
            <"""+gpmstart_action_uri+"""> (pd3:output/pd3:target)* ?action.
                ?action (pd3:output/pd3:target)* ?end_action_uri.
            ?action pd3:expansion/(pd3:member/pd3:expansion)* ?container.
            ?container rdf:type pd3:Container.
            ?container pd3:member ?s.
            ?s rdf:type ?type.
            FILTER (?type = pd3:Flow)
            ?s ?p ?o.
            FILTER (?p = rdf:type || ?p = pd3:arcType || ?p = pd3:layer || ?p = pd3:source || ?p = pd3:target || ?p = pd3:value)
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

    print("output")
    print(conresult)
    
    output_result = {'output_uri': '', 'output_value': ''}
    # for i in range(len(conresult)):
    #     output_result["output_value"]+= conresult[i]["output_value"]["value"]
    #     if(conresult[i]["output_value"]["value"]):
    #         output_result["output_uri"] = conresult[i]["output_uri"]["value"]
    # output_value1 = output_result["output_value"].replace("[loop]", "")

    # while("[IF" in output_value1):
    #     output_control_value = output_value1[output_value1.find("[IF"):output_value1.find("]")+1]
    #     print(output_control_value)
    #     output_value1 = output_value1.replace(output_control_value, "")
    # output_result["output_value"] = output_value1

    output_uris = []
    output_values = []
    for i in range(len(conresult)):
        output_uris.append(conresult[i]["output_uri"]["value"])
        output_values.append(conresult[i]["output_value"]["value"])

    for i in range(len(output_values)):
        output_values[i] = output_values[i].replace("[loop]","")
        output_control_value = output_values[i][output_values[i].find("[IF"):output_values[i].find("]")+1]
        output_values[i] = output_values[i].replace(output_control_value, "")
        if(output_values[i] != ""):
            output_result["output_uri"] = output_uris[i]
            output_result["output_value"] = output_values[i]
            break
    if(output_result["output_uri"]==""):
        output_uris, output_values = zip(*sorted(zip(output_uris, output_values)))
        output_result["output_uri"] = output_uris[0]
        output_result["output_value"] = output_values[0]

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
    if(len(converted_results)!= 0):
        return converted_results[0]['gpm_action_uri']["value"]
    else:
        return ''



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
    # print(results_action_uri)

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

#次に実施するアクションのURIを取得
def get_nextaction(action_uri, graph_uri):
    print("際")
    print(action_uri, graph_uri)
    query = """
    PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?nextaction (COUNT (?upper) AS ?distance)
    WHERE
    {GRAPH <"""+ graph_uri +"""> {
    {<"""+ action_uri +"""> pd3:output/pd3:target ?nextaction.
    FILTER NOT EXISTS {?nextaction pd3:actionType "end"}}
    UNION
    {<"""+ action_uri +"""> pd3:output/pd3:target ?end.
    ?end pd3:actionType "end".
    ?end (pd3:attribution/pd3:contraction)* ?upper1.
    ?upper1 (pd3:attribution/pd3:contraction)+ ?upper.
    ?upper pd3:output/pd3:target ?nextaction.
    FILTER NOT EXISTS {?nextaction pd3:actionType "end"}
    }
    }}
    GROUP BY ?nextaction
    ORDER BY ?distance
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    print(converted_results)
    if(len(converted_results) != 0):
        nextaction = converted_results[0]['nextaction']['value']
        print(nextaction)
        tmp = nextaction
        while(tmp != ""):
            nextaction = tmp
            query1 = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?nextaction1 
            WHERE
            {
                GRAPH<"""+graph_uri +""">{
                    <"""+ nextaction +"""> pd3:expansion/pd3:member ?start.
                    ?start pd3:actionType "start";
                        pd3:output/pd3:target ?nextaction1.
                }
            }
            
            """
            sparql1 = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
            sparql1.setQuery(query1)
            sparql1.setReturnFormat(JSON)
            converted_results1 = sparql1.query().convert()["results"]["bindings"]
            
            if(len(converted_results1) != 0):
                tmp = converted_results1[0]['nextaction1']['value']
            else:
                tmp = ''
        print("ふらっぐ")
        print(nextaction)
        return nextaction
    else:
        return ''

#gpmからloopの矢印、制御文、targetとなるactionを取得
def get_nextloop(action_uri, gpm_graph_uri, lld_graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?loopcondition ?loopnext
    WHERE
    {GRAPH <"""+ lld_graph_uri + """> {
        <"""+ action_uri +"""> pd3:control "loop";
        pd3:uses ?gpm_action
    }
    GRAPH<"""+gpm_graph_uri+""">{
        ?gpm_action pd3:output ?gpm_flow.
        ?gpm_flow pd3:value ?loopcondition;
        pd3:target ?loopnext.
    }
    }
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results_condition = []
    results_next = []
    for converted_result in converted_results:
        results_condition.append(converted_result['loopcondition']['value'])
        results_next.append(converted_result["loopnext"]["value"])

    if(results_next ==[]):
        query1 = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?loopcondition ?loopnext (COUNT (?inter) AS ?distance)
        WHERE
        {GRAPH <"""+ lld_graph_uri + """> {
            <"""+ action_uri +"""> pd3:output/pd3:target ?end.
            ?end pd3:actionType "end".
            <"""+action_uri+"""> (pd3:attribution/pd3:contraction)* ?inter.
            ?inter (pd3:attribution/pd3:contraction)+ ?upper.
            ?upper pd3:control "loop";
            pd3:uses ?gpm_action.
        }
        GRAPH<"""+gpm_graph_uri+""">{
            ?gpm_action pd3:output ?gpm_flow.
            ?gpm_flow pd3:value ?loopcondition;
            pd3:target ?loopnext.
        }
        }
        GROUP BY ?loopcondition ?loopnext
        ORDER BY ?distance
        """
        sparql1 = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
        sparql1.setQuery(query1)
        sparql1.setReturnFormat(JSON)
        converted_results = sparql1.query().convert()["results"]["bindings"]
        for converted_result in converted_results:
            results_condition.append(converted_result['loopcondition']['value'])
            results_next.append(converted_result["loopnext"]["value"])

    return results_condition, results_next


def get_nextaction1(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?nextaction
    WHERE
    {GRAPH <"""+ graph_uri + """> {
        <"""+ action_uri +"""> pd3:output ?output.
        ?output rdf:type pd3:Flow.
        ?output pd3:target ?nextaction.
        
    }}
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results = []
    for converted_result in converted_results:
        results.append(converted_result['nextaction']['value'])
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

#ログレベルの記述のタイトルを取得
def get_graph_title(graph_uri):
    query = """PREFIX dcterms:<http://purl.org/dc/terms/>
    SELECT ?title
    WHERE{
        GRAPH<"""+ graph_uri +""">{
            <"""+ graph_uri +"""> dcterms:title ?title.
        }
    }
    """
    sparql =  SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    if(len(converted_results) != 0):
        return converted_results[0]["title"]["value"]
    else:
        return ''

#ログレベルの記述の説明を取得
def get_graph_description(graph_uri):
    query = """PREFIX dcterms:<http://purl.org/dc/terms/>
    SELECT ?description
    WHERE{
        GRAPH<"""+ graph_uri +""">{
            <"""+ graph_uri +"""> dcterms:description ?description.
        }
    }
    """
    sparql =  SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    if(len(converted_results) != 0):
        return converted_results[0]["description"]["value"]
    else:
        return ''

#対象アクションが所属するレイヤーの種類を取得
def get_action_layer(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    SELECT ?layertype
    WHERE{
        GRAPH<""" + graph_uri +""">{
            <""" + action_uri +"""> pd3:layer ?layertype
        }
    }
    """
    sparql =  SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    if(len(converted_results) != 0):
        return converted_results[0]["layertype"]["value"]
    else:
        return ''

#実行の有無を確認
def get_done_action(action_uri, graph_uri):
    query= """PREFIX dcterms:<http://purl.org/dc/terms/>
    PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>

    SELECT ?done
    WHERE{
        GRAPH<"""+ graph_uri +""">{
            <"""+ action_uri +"""> pd3:done ?done.
        }
    }
    """
    sparql =  SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    if(len(converted_results) != 0):
        return converted_results[0]["done"]["value"]
    else:
        return 'notdone'

#実行チェックをつけた後に、その階層のアクションを全て実行したの場合、上のアクションを取得
def get_done_hieraction(action_uri, graph_uri):
    query= """PREFIX dcterms:<http://purl.org/dc/terms/>
    PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>

    SELECT ?done_action
    WHERE{
        GRAPH<"""+graph_uri+""">{
            <"""+action_uri+"""> (pd3:attribution/pd3:contraction)* ?last_action.
            ?last_action pd3:output/pd3:target ?end.
            ?end pd3:actionType "end".
            ?last_action pd3:attribution/pd3:contraction ?done_action.
        }
    }
    """
    sparql = SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    results = []
    for converted_result in converted_results:
        results.append(converted_result["done_action"]["value"])
    return results

def get_forloop(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    
    SELECT ?container ?flow ?action ?gpm_end_flow
    WHERE{
        GRAPH<"""+ graph_uri +""">{
            OPTIONAL{<"""+ action_uri +"""> pd3:attribution ?container.}
            <"""+action_uri+"""> pd3:output ?flow.
            ?flow pd3:target ?action;
            pd3:uses ?gpm_end_flow
        }
    }
    """
    sparql =  SPARQLWrapper("http://digital-triplet.net:3030/test/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    converted_results = sparql.query().convert()["results"]["bindings"]
    if(len(converted_results) != 0):
        if("container" in converted_results[0]):
            return converted_results[0]["container"]["value"], converted_results[0]["flow"]["value"], converted_results[0]["action"]["value"], converted_results[0]["gpm_end_flow"]["value"]
        else:
            return "", converted_results[0]["flow"]["value"], converted_results[0]["action"]["value"], converted_results[0]["gpm_end_flow"]["value"]
        
def get_expansion(action_uri, graph_uri):
    query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
    SELECT ?container
    WHERE{
        GRAPH<"""+graph_uri+""">{
            <"""+action_uri+"""> pd3:expansion ?container.
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