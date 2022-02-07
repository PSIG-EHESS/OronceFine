#!/usr/bin/env python
# coding: utf8

import json
import io
import httplib2
import networkx as nx

try:
    import pygraphviz
    from networkx.drawing.nx_agraph import write_dot
    print("using package pygraphviz")
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import write_dot
        print("using package pydot")
    except ImportError:
        print()
        print("Both pygraphviz and pydot were not found ")
        print("see  https://networkx.github.io/documentation/latest/reference/drawing.html")
        print()
        raise

#Collection Pontoise
#http://psig.huma-num.fr/omeka-s/api/items?item_set_id=630970

def request(url):
    #print '____ querying : ' + url
    resp, content = _http.request(url, "GET")  # , body=data, headers=headers)
    x = json.loads(content)

    return x

def add_link(id_node_source, name_node_source, collection_source, id_node_target, target_node_name, target_node_collection, motivation, poids):

    G.add_edge(id_node_source, id_node_target, motivation=str(motivation), weight=poids)

    G.nodes[id_node_source]['name'] = name_node_source  # .encode("latin-1")) #récupérer le nom de l'item éventuellement
    G.nodes[id_node_source]['id_item'] = id_node_source  # .encode("latin-1")) #récupérer le nom de l'item éventuellement
    G.nodes[id_node_source]['group'] = collection_source  # récupérer le nom de l'item éventuellement
    G.nodes[id_node_source]['color'] = collection_source  # récupérer le nom de l'item éventuellement

    G.nodes[id_node_target]['name'] = target_node_name  # .encode("latin-1")) #récupérer le nom de l'item éventuellement
    G.nodes[id_node_target]['id_item'] = id_node_target  # .encode("latin-1")) #récupérer le nom de l'item éventuellement
    G.nodes[id_node_target]['group'] = target_node_collection  # récupérer le nom de l'item éventuellement
    G.nodes[id_node_target]['color'] = target_node_collection  # récupérer le nom de l'item éventuellement

def read_node(url):

    if "http://" in url:
        resp_node, content_node = _http.request(url, "GET")  # , body=data, headers=headers)
        x = json.loads(content_node)

        id_node = x['o:id']
        name = ''
        collection = -1

        #print x['dcterms:title']
        #print 'longueur title ' + str(len(x['dcterms:title']))
        #print 'longueur item_set ' + str(len(x['o:item_set']))

        if 'dcterms:title' in x:
            if len(x['dcterms:title']) > 0 and '@value' in x['dcterms:title'][0]:
                name = x['dcterms:title'][0]['@value']
                #print 'nom in fonction : ' + name
        elif 'dcterms:description' in x:
            if len(x['dcterms:description']) > 0 and '@value' in x['dcterms:description'][0]:
                name = x['dcterms:description'][0]['@value']
                #print 'nom in fonction : ' + name
        if len(x['o:item_set']) > 0 and 'o:id' in x['o:item_set'][0]:
            collection = x['o:item_set'][0]['o:id']

        return id_node, name, collection
    else:

        return -1, '', -1

_http = httplib2.Http()

nb_pages = 1
nb_item_per_page = 190
nb_annot = 1181

# URL Omeka-s API
#base_url_collections = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id=717270&per_page=200"
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"
base_url_annot = "http://psig.huma-num.fr/omeka-s/api/annotations/"

collection = 717270
base_url_items_collection = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id="+str(collection)

iter_base_url = base_url_items_collection

#Request URL
x = request(iter_base_url)

G = nx.Graph()

i = 0
print "all request : " + str(x)
for item in range(0, 19):
    i += 1

    print "request x : " + str(x[item])

    # attention, pour futur changement, il faut changer le type, par exemple : 'dctype:Image'
    if x[item]['@type'][1] == 'bibo:Map':

        id_node_source = x[item]['o:id']
        name_node_source = x[item]['dcterms:title'][0]['@value'].encode('utf8')
        collection_source = collection

        print '__________________________________________________________________'
        print str(i) + " --- " + str(id_node_source) + " --- " + str(name_node_source)

        #nb_annot = len(json_item[item]['oa:Annotation'])
        #print 'nb annots : ' + str(nb_annot)
        #print '   ' + str(json_item[item]['oa:Annotation'])

        if 'oa:Annotation' in x[item]:
            #print "Annotations found ! " +  " for " + str(id_node_source)

            #for id_annotation in x[item]['oa:Annotation']:
            #    print "in for oa:Annotation"

            url_annot = x[item]['oa:Annotation']

            for annotation in x[item]['oa:Annotation']:

                #print "in for oa:Annotation 2"

                print '     url annotation : ' + annotation['@id']
                x_annotation = request(annotation['@id'])
                annotation_id = annotation['o:id']

                #print x_annotation

                if 'oa:hasTarget' in x_annotation:
                    if 'oa:hasSource' in x_annotation['oa:hasTarget'][0]:
                        #print '         ' + str(x_annotation['oa:hasTarget'][0]['oa:hasSource'][0])
                        #!!! attention, property id peut être @id ?
                        if '@id' in x_annotation['oa:hasTarget'][0]['oa:hasSource'][0]:

                            url = x_annotation['oa:hasTarget'][0]['oa:hasSource'][0]['@id']

                            id_node_target, target_node_name, target_node_collection = read_node(url)

                            print '     annotation n° ' + str(id_node_target)

                            add_link(id_node_source, name_node_source, collection_source,
                                        id_node_target, target_node_name, target_node_collection, '', 1.0)
                            print ' link added ' + '(' + str(id_node_source) + ') -> ' + '(' + str(id_node_target) + ')'
print 'end requests'

cpt_nodes = 0
nodes = []
tab_nodes_neo = []
for i in G.nodes():
    G.nodes[i]['id'] = cpt_nodes
    print 'node ' + str(i)
    nodes.append({'id': G.nodes[i]['id'], 'id_item': G.nodes[i]['id_item'], 'name': G.nodes[i]['name'], 'group': str(G.nodes[i]['group'])})
    cpt_nodes += 1

print nodes
#tx.commit()

#nodes = [{'id': G.nodes[i]['id'], 'name': str(G.nodes[i]['name']), 'group': str(G.nodes[i]['group'])} for i in G.nodes()]
links = [{'source': G.nodes[u[0]]['id'], 'target': G.nodes[u[1]]['id'],
      'motivation':G.edges[u]['motivation'], 'weight':G.edges[u]['weight']} for u in G.edges()]

print 'export graph as json'
filename = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\scripts\\out\\graph_annotations_collection_'+str(collection)+'.json'
#with open(filename, 'w', encoding='utf8') as f:
with io.open(filename, 'wb') as f:
    json.dump({'nodes': nodes, 'links': links},
              f, indent=4, )
print 'ok'