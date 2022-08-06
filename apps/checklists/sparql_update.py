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



def add_LLD_tofuseki(GPMuri, action, intention, toolknowledge, annotation):

    #fusekiへの追加
    fuseki = FusekiUpdate('http://digital-triplet.net:3030', 'test')
    g = Graph()
    pd3= Namespace('http://DigitalTriplet.net/2021/08/ontology#')

    insert_data = [[URIRef("test"), pd3.value, Literal("test")]]
    RdfUtils.add_list_to_graph(g, insert_data)
    spo_str = '\n'.join(
        [f'{s.n3()} {p.n3()} {o.n3()}.' for (s, p, o) in g]
    )
    print(spo_str)

    query= """PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            INSERT DATA{
            GRAPH<http://digital-triplet.net:3030/test_newlog>{""" + spo_str +"""}
            }"""
    query_result = fuseki.run_sparql(query)
    result = query_result.response.read().decode()

    if result.find("Success") >0:
        print(True)
    else:
        print(False)