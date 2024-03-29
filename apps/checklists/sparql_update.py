from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from django.http import JsonResponse
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
from pyfuseki import FusekiUpdate
from pyfuseki.utils import RdfUtils
from django.conf import settings
import datetime
from . import sparql

def add_LLDgraph_tofuseki(lld_title, gpm_graph_uri):
    #fusekiへの追加
    fuseki = FusekiUpdate(f"http://{settings.DB_DOMAIN}:3030", settings.DATASET)
    g = Graph()
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')
    dcterms = Namespace('http://purl.org/dc/terms/')

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = '{:%Y%m%d%H%M%S}'.format(now) 

    lld_uri = f"http://{settings.DB_DOMAIN}:3030" + '/' + lld_title + '/' + d + '/'
    
    #記述のメタデータの作成
    insert_data = [[URIRef(lld_uri),rdf.type, pd3.EngineeringProcess], 
    [URIRef(lld_uri), dcterms.title, Literal(lld_title)],
    [URIRef(lld_uri), pd3.epType, Literal("LLD")],
    [URIRef(lld_uri), pd3.epUses, URIRef(gpm_graph_uri)]]

    idset = list()
    useset = list()

    #ログレベルの記述作成のためのエンティティのデータを取得
    triples, urilist = sparql.get_GPM_entity(gpm_graph_uri)
    
    print("ぶべ")
    #ループのために更新
    triples, urilist = update_forloopif(triples, urilist, gpm_graph_uri)
    print("ばび")
    new_urilist = []

    #新しいURIを生成して置換
    for i in range(len(urilist)):
        new_uri = lld_uri + d + '-' + str(i)
        for j in range(len(triples)):
            for k in range(len(triples[j])):
                if(triples[j][k] == urilist[i]):
                    triples[j][k] = URIRef(new_uri)
        new_urilist.append(URIRef(new_uri))
        #新しくidとusesを追加
        idset.append([URIRef(new_uri), pd3.id, Literal(d+'-'+str(i))])
        useset.append([URIRef(new_uri), pd3.uses, urilist[i]])

    print("ぱ")

    integrated_data = insert_data + triples + idset + useset

    #アクションのURIに対して、空の詳細情報のentityを追加
    #URIのための番号
    count = len(urilist)

    print(len(triples))
    #詳細情報のエンティティのリスト
    for elem in triples:
        if(elem[1]==rdf.type and elem[2]==pd3.Action and not([elem[0], pd3.actionType, Literal("end")] in triples)):
            #new_urilistの中でelem[0]に対応するindexを獲得、その後urilistの同じindexには変換前のアクションuriがあるので、それを元に詳細情報の検索をかける
            old_action_uri = str(urilist[new_urilist.index(elem[0])])
            action_result, intention_result, toolknowledge_result, annotation_result, rationale_result, output_result = sparql.action_supinfo(old_action_uri, gpm_graph_uri)

            new_intention_uri = lld_uri + d + '-' + str(count)
            inte_data = [[URIRef(new_intention_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_intention_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_intention_uri), pd3.target, elem[0]],
            [URIRef(new_intention_uri), pd3.arcType, Literal('intention')],
            [elem[0], pd3.input, URIRef(new_intention_uri)]]
            if(intention_result['intention_value']==''):
                inte_data.append([URIRef(new_intention_uri), pd3.value, Literal('')])
            else:
                inte_data.append([URIRef(new_intention_uri), pd3.value, Literal(intention_result['intention_value'])])
            count+=1

            new_toolknowledge_uri = lld_uri + d + '-' + str(count)
            tool_data = [[URIRef(new_toolknowledge_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_toolknowledge_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_toolknowledge_uri), pd3.target, elem[0]],
            [URIRef(new_toolknowledge_uri), pd3.arcType, Literal('tool/knowledge')],
            [elem[0], pd3.input, URIRef(new_toolknowledge_uri)]]
            if(toolknowledge_result['toolknowledge_value']==''):
                tool_data.append([URIRef(new_toolknowledge_uri), pd3.value, Literal('')])
            else:
                tool_data.append([URIRef(new_toolknowledge_uri), pd3.value, Literal(toolknowledge_result['toolknowledge_value'])])
            count+=1

            new_annotation_uri = lld_uri + d + '-' + str(count)
            anno_data = [[URIRef(new_annotation_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_annotation_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_annotation_uri), pd3.target, elem[0]],
            [URIRef(new_annotation_uri), pd3.arcType, Literal('annotation')],
            [elem[0], pd3.input, URIRef(new_annotation_uri)]]
            if(annotation_result['annotation_value']==''):
                anno_data.append([URIRef(new_annotation_uri), pd3.value, Literal('')])
            else:
                anno_data.append([URIRef(new_annotation_uri), pd3.value, Literal(annotation_result['annotation_value'])])
            count+=1

            new_rationale_uri = lld_uri + d + '-' + str(count)
            rati_data = [[URIRef(new_rationale_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_rationale_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_rationale_uri), pd3.target, elem[0]],
            [URIRef(new_rationale_uri), pd3.arcType, Literal('rationale')],
            [elem[0], pd3.input, URIRef(new_rationale_uri)]]
            if(rationale_result['rationale_value']==''):
                rati_data.append([URIRef(new_rationale_uri), pd3.value, Literal('')])
            else:
                rati_data.append([URIRef(new_rationale_uri), pd3.value, Literal(rationale_result['rationale_value'])])
            count+=1

            #リストに追加
            integrated_data += inte_data + tool_data + anno_data + rati_data

    RdfUtils.add_list_to_graph(g, integrated_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g]
    )

    print("らりる")
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
    print("れろ")

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
    
def update_forloopif(triples, urilist, gpm_graph_uri):
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')  
    #ループの情報矢印を取得
    loop_arrows = list()
    if_arrows = list()
    for i in range(len(triples)):
        if(triples[i][1] == pd3.value):
            if("[loop]" in triples[i][2]):
                loop_arrows.append(triples[i][0])
            elif("[IF" in triples[i][2] and "]" in triples[i][2]):
                if_arrows.append(triples[i][0])

    #ループの情報矢印に関わる情報を取得
    loop_arrows_source = list()

    for i in range(len(loop_arrows)):
        for j in range(len(triples)):
            if(triples[j][0] == loop_arrows[i]):
                if(triples[j][1] == pd3.source):
                    loop_arrows_source.append(triples[j][2])
    
    if_arrows_source = list()
    if_arrows_value = list()

    for i in range(len(if_arrows)):
        for j in range(len(triples)):
            if(triples[j][0] == if_arrows[i]):
                if(triples[j][1] == pd3.source):
                    if_arrows_source.append(triples[j][2])
                elif(triples[j][1] == pd3.value):
                    if_arrows_value.append(triples[j][2])

    #ループの情報矢印に関する情報をtripleとurilistから消去する
    for loop_arrow in loop_arrows:
        urilist.remove(loop_arrow)
        for triple in triples:
            if(loop_arrow in triple):
                triples.remove(triple)
    
    #ループ矢印のsourceにpd3:control "loop"を追加する
    for i in range(len(loop_arrows)):
        triples.append([loop_arrows_source[i], pd3.control, Literal("loop")])

    #if矢印のラベル情報のうち、制御構文を消す
        #if矢印の情報を制御構文とアクションの出力情報に分ける
    for i in range(len(if_arrows)):
        str_value = str(if_arrows_value[i])
        control_value = str_value[str_value.find("[IF") : str_value.find("]")+1]
        # if_control_values.append(Literal(control_value))
        output_value = Literal(str_value.replace(control_value, ""))
        triples.remove([if_arrows[i], pd3.value, if_arrows_value[i]])
        triples.append([if_arrows[i], pd3.value, output_value])
    
    #if矢印のうち，sourceがif_arrows_sourceの中に複数ある（同じ分岐構造でif矢印が並列している）ものに対して，if矢印〜endまでの消去を行う
    for i in range(len(if_arrows)):
        if(if_arrows_source.count(if_arrows_source[i]) != 1):
            # urilist.remove(if_arrows[i])
            # for triple in triples:
            #     if(if_arrows[i] in triple):
            #         triples.remove(triple)
            triples.append([if_arrows_source[i], pd3.control, Literal("if")])

            query = """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?if_start_action ?end
            WHERE{
                GRAPH<"""+gpm_graph_uri+""">{
                    <"""+str(if_arrows[i])+"""> pd3:target ?if_start_action.
                    ?if_start_action (pd3:output/pd3:target)* ?end.
                    ?end pd3:actionType "end".
                }
            }
            """
            sparql1 = SPARQLWrapper(f"http://{settings.DB_DOMAIN}:3030/{settings.DATASET}/sparql")
            sparql1.setQuery(query)
            sparql1.setReturnFormat(JSON)
            converted_results = sparql1.query().convert()["results"]["bindings"]
            print("conver")
            print(converted_results)
            if(len(converted_results)!=0):
                triples_forif, urilist_forif = sparql.get_GPM_part_entity(converted_results[0]["if_start_action"]["value"], converted_results[0]["end"]["value"], gpm_graph_uri)
                print(triples_forif)
                print(urilist_forif)
                triples = [tuple(i) for i in triples]
                triples_forif = [tuple(i) for i in triples_forif]
                triples = list(set(triples)-set(triples_forif))
                urilist = list(set(urilist) - set(urilist_forif))
                triples = [list(i) for i in triples]
                print(triples)
    print(len(triples))
    return triples, urilist

#LLDのメタ情報を更新する
def add_LLD_metainfo(request):
    graph_uri = request.POST.get("lld_graph_uri")
    new_title = request.POST.get("selected_LLD_title")
    new_creator = request.POST.get("selected_LLD_creator")
    new_description = request.POST.get("selected_LLD_description")

    #fusekiへの追加
    fuseki = FusekiUpdate(f"http://{settings.DB_DOMAIN}:3030", settings.DATASET)
    dcterms = Namespace('http://purl.org/dc/terms/')

    print("new_title", new_title)
    old_title, old_creator, old_description = sparql.get_description_metainfo(graph_uri)

    delete_data = []
    insert_data = []
    if(new_title != old_title):
        delete_data.append([URIRef(graph_uri), dcterms.title, Literal(old_title)])
        insert_data.append([URIRef(graph_uri), dcterms.title, Literal(new_title)])
    if(new_creator != old_creator):
        delete_data.append([URIRef(graph_uri), dcterms.creator, Literal(old_creator)])
        insert_data.append([URIRef(graph_uri), dcterms.creator, Literal(new_creator)])
    if(new_description != old_description):
        delete_data.append([URIRef(graph_uri), dcterms.description, Literal(old_description)])
        insert_data.append([URIRef(graph_uri), dcterms.description, Literal(new_description)])

    if(delete_data != []):
        print(delete_data, insert_data)
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
                GRAPH<"""+ graph_uri +""">{""" + spo_str_delete + """}
                };

                INSERT DATA{
                GRAPH<""" + graph_uri + """>{""" + spo_str_insert +"""}
                }"""
        query_result = fuseki.run_sparql(query)
        result = query_result.response.read().decode()

        if result.find("Success") >0:
            print(True)
        else:
            print(False)
    a = dict()
    return JsonResponse(a)


#actionおよびその詳細内容を更新する
def add_LLD_tofuseki(action_uri, action, intention, toolknowledge, annotation, rationale, output, gpm_graph_uri, lld_graph_uri):

    print('あいうえお')
    #fusekiへの追加
    fuseki = FusekiUpdate(f"http://{settings.DB_DOMAIN}:3030", settings.DATASET)
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    action_result, intention_result, toolknowledge_result, annotation_result, rationale_result, output_result = sparql.action_supinfo(action_uri, lld_graph_uri)

    print(output_result)
    delete_data = [[URIRef(action_result['action_uri']), pd3.value, Literal(action_result['action_value'])],
    [URIRef(intention_result['intention_uri']), pd3.value, Literal(intention_result['intention_value'])],
    [URIRef(toolknowledge_result['toolknowledge_uri']), pd3.value, Literal(toolknowledge_result['toolknowledge_value'])],
    [URIRef(annotation_result['annotation_uri']), pd3.value, Literal(annotation_result['annotation_value'])],
    [URIRef(rationale_result['rationale_uri']), pd3.value, Literal(rationale_result['rationale_value'])],
    [URIRef(output_result['output_uri']), pd3.value, Literal(output_result['output_value'])]]

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = '{:%Y%m%d%H%M%S}'.format(now) 

    insert_data = [[URIRef(action_result['action_uri']), pd3.value, Literal(action)],
    [URIRef(intention_result['intention_uri']), pd3.value, Literal(intention)],
    [URIRef(toolknowledge_result['toolknowledge_uri']), pd3.value, Literal(toolknowledge)],
    [URIRef(annotation_result['annotation_uri']), pd3.value, Literal(annotation)],
    [URIRef(rationale_result['rationale_uri']), pd3.value, Literal(rationale)],
    [URIRef(output_result['output_uri']), pd3.value, Literal(output)],
    [URIRef(action_result['action_uri']), pd3.time, Literal(d)]]

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


#actionを追加
def add_LLDaction_tofuseki(added_action, base_action_uri, lld_graph_uri, flag):

    #追加したいアクションが既にある場合，重複して追加をしないようにする
    if(flag == "above"):
        part_query = "pd3:input/pd3:source"
    elif(flag == "below"):
        part_query = "pd3:output/pd3:target"
    query="""PREFIX dcterms:<http://purl.org/dc/terms/>
    PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>

    SELECT ?added_action
    WHERE{
        GRAPH<"""+ lld_graph_uri +""">{
            <"""+ base_action_uri +"""> """+ part_query +"""/pd3:value ?added_action.
        }
    }"""
    sparql1 = SPARQLWrapper(f"http://{settings.DB_DOMAIN}:3030/{settings.DATASET}/sparql")
    sparql1.setQuery(query)
    sparql1.setReturnFormat(JSON)
    converted_results = sparql1.query().convert()["results"]["bindings"]

    if(len(converted_results)!= 0):
        if(converted_results[0]["added_action"]["value"] != added_action):
            #fusekiへの追加
            fuseki = FusekiUpdate(f"http://{settings.DB_DOMAIN}:3030", settings.DATASET)
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

#実行済みのアクションに対してcheckをつける
def add_done_action(action_uri, lld_graph_uri):
        #fusekiへの追加
    fuseki = FusekiUpdate(f"http://{settings.DB_DOMAIN}:3030", settings.DATASET)
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    insert_data = [[URIRef(action_uri), pd3.done, Literal("done")]]
    g = Graph()
    RdfUtils.add_list_to_graph(g, insert_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g]
    )
    
    query = """PREFIX pd3:<http://DigitalTriplet.net/2021/08/ontology#>
            INSERT DATA{
                GRAPH<""" + lld_graph_uri + """>{""" + spo_str + """}
            }"""

    query_result=fuseki.run_sparql(query)
    result = query_result.response.read().decode()
    if result.find("Success") >0:
            print(True)
    else:
        print(False)

#loopの内容を更新する
def add_loopgraph(action_uri, gpm_start_action, gpm_end_action, lld_graph_uri, gpm_graph_uri, control):
    #fusekiへの追加
    fuseki = FusekiUpdate(f"http://{settings.DB_DOMAIN}:3030", settings.DATASET)
    g = Graph()
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = '{:%Y%m%d%H%M%S}'.format(now) 
    
    new_urilist = []
    idset = []
    useset = []
    print(action_uri)
    print(gpm_start_action)
    print(gpm_end_action)
    print(lld_graph_uri, gpm_graph_uri)
    triples, urilist = sparql.get_GPM_part_entity(gpm_start_action, gpm_end_action, gpm_graph_uri)
    print(triples, urilist)
    triples, urilist = update_forloopif(triples, urilist, gpm_graph_uri)
    print(triples, urilist)

    #loopが存在する階層のプロセスについて、コンテナと、loop矢印と分岐をなす情報矢印と、その情報矢印の刺さるアクション、loopが始まる最初のアクションの元のGPMのアクションの4つを取得
    #gpm_actionは新規のログレベルの記述のために生成したuriと同じなので、新規のログレベルの記述のループの最後を指定するために使用
    #update_flowとupdate_action,update_containerはログにおけるflowとactionであり，ループ構造によって繰り返されるプロセスが挿入される
    update_container, update_flow, update_action, gpm_end_flow = sparql.get_forloop(action_uri, lld_graph_uri)
    print("flag")
    print(update_container, update_flow, update_action, gpm_end_flow)

    #update_containerに紐づくgpmのコンテナを取得
    gpm_container = sparql.get_gpm_action(update_container, gpm_graph_uri)

    #最上位のコンテナの情報を更新
    container_members = []
    for triple in triples:
        if(triple[1] == pd3.attribution and triple[2] == URIRef(gpm_container)):
            triple[2] = URIRef(update_container)
            container_members.append([URIRef(update_container), pd3.member, triple[0]])

    #情報矢印とアクションを消して追加する
    delete_data = [[URIRef(update_flow), pd3.target, URIRef(update_action)],
    [URIRef(update_action), pd3.input, URIRef(update_flow)]]

    #triplesの中から、gpm_start_actionへの入力と、gpm_end_flowの出力を削除
    for triple in triples:
        if(triple[0] == URIRef(gpm_start_action) and triple[1] == pd3.input):
            triples.remove(triple)
        elif(triple[0] == URIRef(gpm_end_flow) and triple[1] == pd3.target):
            triples.remove(triple)

    for i in range(len(urilist)):
        new_uri = lld_graph_uri + d + '-' + str(i)
        for j in range(len(triples)):
            for k in range(len(triples[j])):
                if(triples[j][k] == urilist[i]):
                    triples[j][k] = URIRef(new_uri)
        new_urilist.append(URIRef(new_uri))
        #新しくidとusesを追加
        idset.append([URIRef(new_uri), pd3.id, Literal(d+'-'+str(i))])
        useset.append([URIRef(new_uri), pd3.uses, urilist[i]])

    integrated_data = triples + idset + useset + container_members

    print("urilist")
    print(urilist)

    insert_data = [[URIRef(update_flow), pd3.target, new_urilist[urilist.index(URIRef(gpm_start_action))]],
    [new_urilist[urilist.index(URIRef(gpm_start_action))], pd3.input, URIRef(update_flow)],
    ]
    if(control == "loop"):
        insert_data += [[new_urilist[urilist.index(URIRef(gpm_end_flow))], pd3.target, URIRef(update_action)],
        [URIRef(update_action), pd3.input, new_urilist[urilist.index(URIRef(gpm_end_flow))]]]
    
    integrated_data += insert_data
    
    #アクションのURIに対して、空の詳細情報のentityを追加
    #URIのための番号
    count = len(urilist)

    #詳細情報のエンティティのリスト
    for elem in triples:
        if(elem[1]==rdf.type and elem[2]==pd3.Action and not([elem[0], pd3.actionType, Literal("end")] in triples)):
            #new_urilistの中でelem[0]に対応するindexを獲得、その後urilistの同じindexには変換前のアクションuriがあるので、それを元に詳細情報の検索をかける
            old_action_uri = str(urilist[new_urilist.index(elem[0])])
            action_result, intention_result, toolknowledge_result, annotation_result, rationale_result, output_result = sparql.action_supinfo(old_action_uri, gpm_graph_uri)

            new_intention_uri = lld_graph_uri + d + '-' + str(count)
            inte_data = [[URIRef(new_intention_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_intention_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_intention_uri), pd3.target, elem[0]],
            [URIRef(new_intention_uri), pd3.arcType, Literal('intention')],
            [elem[0], pd3.input, URIRef(new_intention_uri)]]
            if(intention_result['intention_value']==''):
                inte_data.append([URIRef(new_intention_uri), pd3.value, Literal('')])
            else:
                inte_data.append([URIRef(new_intention_uri), pd3.value, Literal(intention_result['intention_value'])])
            count+=1

            new_toolknowledge_uri = lld_graph_uri + d + '-' + str(count)
            tool_data = [[URIRef(new_toolknowledge_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_toolknowledge_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_toolknowledge_uri), pd3.target, elem[0]],
            [URIRef(new_toolknowledge_uri), pd3.arcType, Literal('tool/knowledge')],
            [elem[0], pd3.input, URIRef(new_toolknowledge_uri)]]
            if(toolknowledge_result['toolknowledge_value']==''):
                tool_data.append([URIRef(new_toolknowledge_uri), pd3.value, Literal('')])
            else:
                tool_data.append([URIRef(new_toolknowledge_uri), pd3.value, Literal(toolknowledge_result['toolknowledge_value'])])
            count+=1

            new_annotation_uri = lld_graph_uri + d + '-' + str(count)
            anno_data = [[URIRef(new_annotation_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_annotation_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_annotation_uri), pd3.target, elem[0]],
            [URIRef(new_annotation_uri), pd3.arcType, Literal('annotation')],
            [elem[0], pd3.input, URIRef(new_annotation_uri)]]
            if(annotation_result['annotation_value']==''):
                anno_data.append([URIRef(new_annotation_uri), pd3.value, Literal('')])
            else:
                anno_data.append([URIRef(new_annotation_uri), pd3.value, Literal(annotation_result['annotation_value'])])
            count+=1

            new_rationale_uri = lld_graph_uri + d + '-' + str(count)
            rati_data = [[URIRef(new_rationale_uri), rdf.type, pd3.SupFlow],
            [URIRef(new_rationale_uri), pd3.id, Literal(d+'-'+str(count))],
            [URIRef(new_rationale_uri), pd3.target, elem[0]],
            [URIRef(new_rationale_uri), pd3.arcType, Literal('rationale')],
            [elem[0], pd3.input, URIRef(new_rationale_uri)]]
            if(rationale_result['rationale_value']==''):
                rati_data.append([URIRef(new_rationale_uri), pd3.value, Literal('')])
            else:
                rati_data.append([URIRef(new_rationale_uri), pd3.value, Literal(rationale_result['rationale_value'])])
            count+=1

            integrated_data += inte_data + tool_data + anno_data + rati_data

    g_insert = Graph()
    RdfUtils.add_list_to_graph(g_insert, integrated_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_insert]
    )
    g_delete = Graph()
    RdfUtils.add_list_to_graph(g_delete, delete_data)
    spo_str_delete = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_delete]
    )
    
    query_lld= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        INSERT DATA{
        GRAPH<"""+ lld_graph_uri +""">{""" + spo_str + """}
        };

        DELETE DATA{
            GRAPH<"""+ lld_graph_uri +""">{""" + spo_str_delete + """}
        };
        """
    query_result = fuseki.run_sparql(query_lld)
    result = query_result.response.read().decode()
    if result.find("Success") >0:
        print(True)
    else:
        print(False)

    usedset = list()
    for elem in useset:
        usedset.append([elem[2], pd3.isUsedBy, elem[0]])

    g_gpm = Graph()
    RdfUtils.add_list_to_graph(g_gpm, usedset)
    spo_str_gpm = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g_gpm]
    )

    #gpmの中の追加
    query_gpm="""PREFIX  pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            INSERT DATA{
                GRAPH<"""+ gpm_graph_uri +""">{""" + spo_str_gpm + """}
            };
        """
    query_result_gpm = fuseki.run_sparql(query_gpm)
    result_gpm = query_result_gpm.response.read().decode()

    if result_gpm.find("Success") >0:
        print(True)
    else:
        print(False)

    