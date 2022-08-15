from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
from pyfuseki import FusekiUpdate
from pyfuseki.utils import RdfUtils
import datetime

def add_LLDgraph_tofuseki(lld_title):
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
    insert_data = [[URIRef(lld_uri),rdf.type, pd3.EngineeringProcess], [URIRef(lld_uri), dcterms.title, Literal(lld_title)], [URIRef(lld_uri), pd3.epType, Literal("LLD")]]
    #insert_data = [[URIRef(lld_uri),rdf.type, pd3.EngineeringProcess]]
    RdfUtils.add_list_to_graph(g, insert_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g]
    )
    print(spo_str)

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX dcterms:<http://purl.org/dc/terms/>

            INSERT DATA{
            GRAPH<""" + lld_uri + """>{""" + spo_str +"""}
            }"""
    query_result = fuseki.run_sparql(query)
    result = query_result.response.read().decode()

    if result.find("Success") >0:
        print(True)
    else:
        print(False)



def add_LLD_tofuseki(action_uri, action, intention, toolknowledge, annotation, output, gpm_graph_uri, lld_graph_uri):

    #fusekiへの追加
    fuseki = FusekiUpdate('http://digital-triplet.net:3030', 'test')
    g = Graph()
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    #新しいエンティティのuriを生成
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = '{:%Y%m%d%H%M%S}'.format(now) 

    new_action_uri = lld_graph_uri + '/' + d + 'action'
    new_intention_uri = lld_graph_uri + '/' + d + 'intention'
    new_toolknowledge_uri = lld_graph_uri + '/' + d + 'toolknowledge'
    new_annotation_uri = lld_graph_uri + '/' + d + 'annotation'
    new_output_uri = lld_graph_uri + '/' + d + 'output'

    #actionType, layer, deriveは未実装
    insert_data = [[URIRef(new_action_uri), rdf.type, pd3.Action],
    [URIRef(new_action_uri), pd3.id, Literal(d+'action')],
    [URIRef(new_action_uri), pd3.value, Literal(action)],
    [URIRef(new_action_uri), pd3.input, URIRef(new_intention_uri)],
    [URIRef(new_action_uri), pd3.input, URIRef(new_toolknowledge_uri)],
    [URIRef(new_action_uri), pd3.input, URIRef(new_annotation_uri)],
    [URIRef(new_action_uri), pd3.output, URIRef(new_output_uri)],
    [URIRef(new_action_uri), pd3.uses, URIRef(action_uri)],
    [URIRef(new_intention_uri), rdf.type, pd3.SupFlow],
    [URIRef(new_intention_uri), pd3.id, Literal(d+'intention')],
    [URIRef(new_intention_uri), pd3.value, Literal(intention)],
    [URIRef(new_intention_uri), pd3.target, URIRef(new_action_uri)],
    [URIRef(new_intention_uri), pd3.arcType, Literal('intention')],
    [URIRef(new_toolknowledge_uri), rdf.type, pd3.SupFlow],
    [URIRef(new_toolknowledge_uri), pd3.id, Literal(d+'toolknowledge')],
    [URIRef(new_toolknowledge_uri), pd3.value, Literal(toolknowledge)],
    [URIRef(new_toolknowledge_uri), pd3.target, URIRef(new_action_uri)],
    [URIRef(new_toolknowledge_uri), pd3.arcType, Literal('tool/knowledge')]
    [URIRef(new_annotation_uri), rdf.type, pd3.SupFlow],
    [URIRef(new_annotation_uri), pd3.id, Literal(d+'annotation')],
    [URIRef(new_annotation_uri), pd3.value, Literal(annotation)],
    [URIRef(new_annotation_uri), pd3.target, URIRef(new_action_uri)],
    [URIRef(new_annotation_uri), pd3.arcType, Literal('annotation')],
    [URIRef(new_output_uri), rdf.type, pd3.Flow],
    [URIRef(new_output_uri), pd3.id, Literal(d+'output')],
    [URIRef(new_output_uri), pd3.value, Literal(output)],
    [URIRef(new_output_uri), pd3.source, URIRef(new_action_uri)],
    [URIRef(new_output_uri), pd3.arcType, Literal('information')]
    ]
    RdfUtils.add_list_to_graph(g, insert_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g]
    )

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            INSERT DATA{
            GRAPH<""" + lld_graph_uri + """>{""" + spo_str +"""}
            }"""
    query_result = fuseki.run_sparql(query)
    result = query_result.response.read().decode()

    if result.find("Success") >0:
        print(True)
    else:
        print(False)

    g2 = Graph()
    #参照元のアクションに対してisUsedByを追加
    insert_data2 = [[URIRef(action_uri), pd3.isUsedBy, URIRef(new_action_uri)]]
    RdfUtils.add_list_to_graph(g2, insert_data2)
    spo_str2 =  '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g2]
    )
    
    query2= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            INSERT DATA{
            GRAPH<""" + gpm_graph_uri + """>{""" + spo_str2 +"""}
            }"""
    query_result2 = fuseki.run_sparql(query2)
    result2 = query_result2.response.read().decode()

    if result2.find("Success") >0:
        print(True)
    else:
        print(False)

