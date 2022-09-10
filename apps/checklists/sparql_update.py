from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
from pyfuseki import FusekiUpdate
from pyfuseki.utils import RdfUtils
import datetime
from . import sparql

def add_LLDgraph_tofuseki(lld_title, gpm_graph_uri):
    #fusekiへの追加
    fuseki = FusekiUpdate('http://digital-triplet.net:3030', 'test')
    g = Graph()
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')
    dcterms = Namespace('http://purl.org/dc/terms/')

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = '{:%Y%m%d%H%M%S}'.format(now) 

    lld_uri = 'http://digital-triplet.net:3030' + '/' + lld_title + '/' + d + '/'
    
    #記述のメタデータの作成
    insert_data = [[URIRef(lld_uri),rdf.type, pd3.EngineeringProcess], 
    [URIRef(lld_uri), dcterms.title, Literal(lld_title)],
    [URIRef(lld_uri), pd3.epType, Literal("LLD")],
    [URIRef(lld_uri), pd3.epUses, URIRef(gpm_graph_uri)]]

    idset = list()
    useset = list()

    #ログレベルの記述作成のためのエンティティのデータを取得
    triples, urilist = sparql.get_GPM_entity(gpm_graph_uri)
    print(urilist[0:10])

    #新しいURIを生成して置換
    for i in range(len(urilist)):
        new_uri = lld_uri + d + '-' + str(i)
        for j in range(len(triples)):
            for k in range(len(triples[j])):
                if(triples[j][k] == urilist[i]):
                    triples[j][k] = URIRef(new_uri)
        #新しくidとusesを追加
        idset.append([URIRef(new_uri), pd3.id, Literal(d+'-'+str(i))])
        useset.append([URIRef(new_uri), pd3.uses, urilist[i]])

    integrated_data = insert_data + triples + idset + useset

    #アクションのURIに対して、空の詳細情報のentityを追加
    #URIのための番号
    count = len(urilist)

    #詳細情報のエンティティのリスト
    for elem in triples:
        if(elem[1]==rdf.type and elem[2]==pd3.Action):
            new_intention_uri = lld_uri + d + '-' + str(count)
            inte_data = [[URIRef(new_intention_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_intention_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_intention_uri), pd3.value, Literal('')],
            [URIRef(new_intention_uri), pd3.target, elem[0]],
            [URIRef(new_intention_uri), pd3.arcType, Literal('intention')],
            [elem[0], pd3.input, URIRef(new_intention_uri)]]
            count+=1

            new_toolknowledge_uri = lld_uri + d + '-' + str(count)
            tool_data = [[URIRef(new_toolknowledge_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_toolknowledge_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_toolknowledge_uri), pd3.value, Literal('')],
            [URIRef(new_toolknowledge_uri), pd3.target, elem[0]],
            [URIRef(new_toolknowledge_uri), pd3.arcType, Literal('tool/knowledge')],
            [elem[0], pd3.input, URIRef(new_toolknowledge_uri)]]
            count+=1

            new_annotation_uri = lld_uri + d + '-' + str(count)
            anno_data = [[URIRef(new_annotation_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_annotation_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_annotation_uri), pd3.value, Literal('')],
            [URIRef(new_annotation_uri), pd3.target, elem[0]],
            [URIRef(new_annotation_uri), pd3.arcType, Literal('annotation')],
            [elem[0], pd3.input, URIRef(new_annotation_uri)]]
            count+=1

            new_rationale_uri = lld_uri + d + '-' + str(count)
            rati_data = [[URIRef(new_rationale_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_rationale_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_rationale_uri), pd3.value, Literal((''))],
            [URIRef(new_rationale_uri), pd3.target, elem[0]],
            [URIRef(new_rationale_uri), pd3.arcType, Literal('rationale')],
            [elem[0], pd3.input, URIRef(new_rationale_uri)]]
            count+=1

            #リストに追加
            integrated_data += inte_data + tool_data + anno_data + rati_data

    RdfUtils.add_list_to_graph(g, integrated_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g]
    )

    #LLDの追加
    query_lld= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            INSERT DATA{
            GRAPH<""" + lld_uri + """>{""" + spo_str +"""}
            }"""
    query_result = fuseki.run_sparql(query_lld)
    result = query_result.response.read().decode()

    if result.find("Success") >0:
        print(True)
    else:
        print(False)   
    

    episused = [[URIRef(gpm_graph_uri), pd3.epIsUsedBy, URIRef(lld_uri)]]
    usedset = list()
    for elem in useset:
        usedset.append([elem[2], pd3.isUsedBy, elem[0]])
    
    data2 = episused + usedset
    g2 = Graph()
    RdfUtils.add_list_to_graph(g2, data2)
    spo_str2 = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g2]
    ) 

    query_gpm = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            INSERT DATA{
            GRAPH<""" + gpm_graph_uri + """>{""" + spo_str2 +"""}
            }"""
    query_result = fuseki.run_sparql(query_gpm)
    result2 = query_result.response.read().decode()

    if result2.find("Sucess") > 0:
        print(True)
    else:
        print(False)
    


def add_LLD_tofuseki(action_uri, action, intention, toolknowledge, annotation, rationale, output, gpm_graph_uri, lld_graph_uri):

    #fusekiへの追加
    fuseki = FusekiUpdate('http://digital-triplet.net:3030', 'test')
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    action_result, intention_result, toolknowledge_result, annotation_result, rationale_result, output_result = sparql.action_supinfo(action_uri, lld_graph_uri)
    
    delete_data = [[URIRef(action_result['action_uri']), pd3.value, Literal(action_result['action_value'])],
    [URIRef(intention_result['intention_uri']), pd3.value, Literal(intention_result['intention_value'])],
    [URIRef(toolknowledge_result['toolknowledge_uri']), pd3.value, Literal(toolknowledge_result['toolknowledge_value'])],
    [URIRef(annotation_result['annotation_uri']), pd3.value, Literal(annotation_result['annotation_value'])],
    [URIRef(rationale_result['rationale_uri']), pd3.value, Literal(rationale_result['rationale_value'])],
    [URIRef(output_result['output_uri']), pd3.value, Literal(output_result['output_value'])]]

    insert_data = [[URIRef(action_result['action_uri']), pd3.value, Literal(action)],
    [URIRef(intention_result['intention_uri']), pd3.value, Literal(intention)],
    [URIRef(toolknowledge_result['toolknowledge_uri']), pd3.value, Literal(toolknowledge)],
    [URIRef(annotation_result['annotation_uri']), pd3.value, Literal(annotation)],
    [URIRef(rationale_result['rationale_uri']), pd3.value, Literal(rationale)],
    [URIRef(output_result['output_uri']), pd3.value, Literal(output)]]

    g_delete = Graph()
    g_insert = Graph()
    RdfUtils.add_list_to_graph(g_delete, delete_data)
    spo_str_delete = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_delete]
    )
    RdfUtils.add_list_to_graph(g_insert, insert_data)
    spo_str_insert = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_insert]
    )

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            DELETE DATA{
            GRAPH<"""+ lld_graph_uri +""">{""" + spo_str_delete + """}
            };

            INSERT DATA{
            GRAPH<""" + lld_graph_uri + """>{""" + spo_str_insert +"""}
            }"""
    query_result = fuseki.run_sparql(query)
    result = query_result.response.read().decode()

    if result.find("Success") >0:
        print(True)
    else:
        print(False)


def add_LLDaction_tofuseki(added_action, base_action_uri, lld_graph_uri, flag):
    #fusekiへの追加
    fuseki = FusekiUpdate('http://digital-triplet.net:3030', 'test')
    g = Graph()
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = '{:%Y%m%d%H%M%S}'.format(now) 

    added_action_uri = lld_graph_uri + d + '-1'
    added_flow_uri = lld_graph_uri + d + '-2'
    added_intention_uri = lld_graph_uri + d + '-3'
    added_toolknowledge_uri = lld_graph_uri + d + '-4'
    added_annotation_uri = lld_graph_uri + d + '-5'
    added_rationale_uri = lld_graph_uri + d + '-6'
    
    #containerがない場合は空白文字が入る
    container_uri = sparql.get_container(base_action_uri, lld_graph_uri)
    delete_data = []
    flow_data =[]

    new_data = [[URIRef(added_action_uri), rdf.type, pd3.Action],
    [URIRef(added_action_uri), pd3.id, Literal(d + '-1')],
    [URIRef(added_action_uri), pd3.value, Literal(added_action)],
    [URIRef(added_flow_uri), rdf.type, pd3.Flow],
    [URIRef(added_flow_uri), pd3.id, Literal(d + '-2')],
    [URIRef(added_flow_uri), pd3.value, Literal('')],
    [URIRef(added_flow_uri), pd3.arcType, Literal('information')],
    [URIRef(added_flow_uri), pd3.source, URIRef(added_action_uri)],
    [URIRef(added_action_uri), pd3.output, URIRef(added_flow_uri)]]

    if(flag== "above"):
        inflows_uri = sparql.get_input_flow(base_action_uri, lld_graph_uri)
        for i in range(len(inflows_uri)):
            delete_data.append([URIRef(inflows_uri[i]), pd3.target, URIRef(base_action_uri)])
            delete_data.append([URIRef(base_action_uri), pd3.input, URIRef(inflows_uri[i])])
            flow_data.append([URIRef(inflows_uri[i]), pd3.target, URIRef(added_action_uri)])
            flow_data.append([URIRef(added_action_uri), pd3.input, URIRef(inflows_uri[i])])

        new_data += [[URIRef(added_flow_uri), pd3.target, URIRef(base_action_uri)],
            [URIRef(base_action_uri), pd3.input, URIRef(added_flow_uri)]]

    elif(flag == "below"):
        outflows_uri = sparql.get_output_flow(base_action_uri, lld_graph_uri)
        nextactions_uri = sparql.get_nextaction1(base_action_uri, lld_graph_uri)

        for i in range(len(outflows_uri)):
            delete_data.append([URIRef(outflows_uri[i]), pd3.target, URIRef(nextactions_uri[i])])
            delete_data.append([URIRef(nextactions_uri[i]), pd3.input, URIRef(outflows_uri[i])])
            flow_data.append([URIRef(outflows_uri[i]), pd3.target, URIRef(added_action_uri)])
            flow_data.append([URIRef(added_action_uri), pd3.input, URIRef(outflows_uri[i])])
            new_data += [[URIRef(added_flow_uri), pd3.target, URIRef(nextactions_uri[i])],
                [URIRef(nextactions_uri[i]), pd3.input, URIRef(added_flow_uri)]]

    
    supinfo_data = [[URIRef(added_intention_uri), rdf.type, pd3.SupFlow],
            [URIRef(added_intention_uri), pd3.id, Literal(d+'-3')],
            [URIRef(added_intention_uri), pd3.value, Literal('')],
            [URIRef(added_intention_uri), pd3.target, URIRef(added_action_uri)],
            [URIRef(added_intention_uri), pd3.arcType, Literal('intention')],
            [URIRef(added_action_uri), pd3.input, URIRef(added_intention_uri)],
            [URIRef(added_toolknowledge_uri), rdf.type, pd3.SupFlow],
            [URIRef(added_toolknowledge_uri), pd3.id, Literal(d+'-4')],
            [URIRef(added_toolknowledge_uri), pd3.value, Literal('')],
            [URIRef(added_toolknowledge_uri), pd3.target, URIRef(added_action_uri)],
            [URIRef(added_toolknowledge_uri), pd3.arcType, Literal('tool/knowledge')],
            [URIRef(added_action_uri), pd3.input, URIRef(added_toolknowledge_uri)],
            [URIRef(added_annotation_uri), rdf.type, pd3.SupFlow],
            [URIRef(added_annotation_uri), pd3.id, Literal(d+'-5')],
            [URIRef(added_annotation_uri), pd3.value, Literal('')],
            [URIRef(added_annotation_uri), pd3.target, URIRef(added_action_uri)],
            [URIRef(added_annotation_uri), pd3.arcType, Literal('annotation')],
            [URIRef(added_action_uri), pd3.input, URIRef(added_annotation_uri)],
            [URIRef(added_rationale_uri), rdf.type, pd3.SupFlow],
            [URIRef(added_rationale_uri), pd3.id, Literal(d+'-6')],
            [URIRef(added_rationale_uri), pd3.value, Literal('')],
            [URIRef(added_rationale_uri), pd3.target, URIRef(added_action_uri)],
            [URIRef(added_rationale_uri), pd3.arcType, Literal('rationale')],
            [URIRef(added_action_uri), pd3.input, URIRef(added_rationale_uri)]]

    insert_data = new_data + flow_data + supinfo_data

    if container_uri != '':
        insert_data += [[URIRef(added_action_uri), pd3.attribution, URIRef(container_uri)],
        [URIRef(added_flow_uri), pd3.attribution, URIRef(container_uri)],
        [URIRef(added_intention_uri), pd3.attribution, URIRef(container_uri)],
        [URIRef(added_toolknowledge_uri), pd3.attribution, URIRef(container_uri)],
        [URIRef(added_annotation_uri), pd3.attribution, URIRef(container_uri)],
        [URIRef(added_rationale_uri), pd3.attribution, URIRef(container_uri)],
        [URIRef(container_uri), pd3.member, URIRef(added_action_uri)],
        [URIRef(container_uri), pd3.member, URIRef(added_flow_uri)],
        [URIRef(container_uri), pd3.member, URIRef(added_intention_uri)],
        [URIRef(container_uri), pd3.member, URIRef(added_toolknowledge_uri)],
        [URIRef(container_uri), pd3.member, URIRef(added_annotation_uri)],
        [URIRef(container_uri), pd3.member, URIRef(added_rationale_uri)]]

    g_delete = Graph()
    g_insert = Graph()
    RdfUtils.add_list_to_graph(g_delete, delete_data)
    spo_str_delete = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_delete]
    )
    RdfUtils.add_list_to_graph(g_insert, insert_data)
    spo_str_insert = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_insert]
    )

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            DELETE DATA{
            GRAPH<"""+ lld_graph_uri +""">{""" + spo_str_delete + """}
            };

            INSERT DATA{
            GRAPH<""" + lld_graph_uri + """>{""" + spo_str_insert +"""}
            }"""
    query_result = fuseki.run_sparql(query)
    result = query_result.response.read().decode()

    if result.find("Success") >0:
        print(True)
    else:
        print(False)
    





    

