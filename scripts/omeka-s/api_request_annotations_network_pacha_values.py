#!/usr/bin/env python
# coding: utf8

import json
import io
import httplib2
import networkx as nx
from networkx.readwrite import json_graph

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


# Collection Pontoise
# http://psig.huma-num.fr/omeka-s/api/items?item_set_id=630970

def request(url):
    # print '____ querying : ' + url
    resp, content = _http.request(url, "GET")  # , body=data, headers=headers)
    x = json.loads(content)

    return x


def add_link(id_node_source, name_node_source, collection_source, id_node_target, target_node_name,
             target_node_collection, motivation, poids, radius_source, radius_target):

    if id_node_source not in G:
        G.add_node(id_node_source)
        G.nodes[id_node_source]['name'] = name_node_source  # .encode("latin-1")) #récupérer le nom de l'item
        G.nodes[id_node_source]['id_item'] = id_node_source  # .encode("latin-1")) #récupérer l id de l'item
        G.nodes[id_node_source]['group'] = collection_source  # récupérer le groupe de l'item
        G.nodes[id_node_source]['color'] = collection_source  # récupérer la couleur de l'item
        G.nodes[id_node_source]['radius'] = radius_source  # récupérer le rayon de l'item

    if id_node_target not in G:
        G.add_node(id_node_target)
        G.nodes[id_node_target]['name'] = target_node_name  # .encode("latin-1")) #récupérer le nom de l'item
        G.nodes[id_node_target]['id_item'] = id_node_target  # .encode("latin-1")) #récupérer l id de l'item
        G.nodes[id_node_target]['group'] = target_node_collection  # récupérer le groupe de l'item
        G.nodes[id_node_target]['color'] = target_node_collection  # récupérer la couleur de l'item
        G.nodes[id_node_target]['radius'] = radius_target  # récupérer le rayon de l'item

    G.add_edge(id_node_source, id_node_target, motivation=str(motivation), weight=poids)


def read_node(url):
    if "http://" in url:
        resp_node, content_node = _http.request(url, "GET")  # , body=data, headers=headers)
        x = json.loads(content_node)

        id_node = x['o:id']
        name = ''
        collection = -1

        # print x['dcterms:title']
        # print 'longueur title ' + str(len(x['dcterms:title']))
        # print 'longueur item_set ' + str(len(x['o:item_set']))

        if 'dcterms:title' in x:
            if len(x['dcterms:title']) > 0 and '@value' in x['dcterms:title'][0]:
                name = x['dcterms:title'][0]['@value']
                # print 'nom in fonction : ' + name
        elif 'dcterms:description' in x:
            if len(x['dcterms:description']) > 0 and '@value' in x['dcterms:description'][0]:
                name = x['dcterms:description'][0]['@value']
                # print 'nom in fonction : ' + name
        if len(x['o:item_set']) > 0 and 'o:id' in x['o:item_set'][0]:
            collection = x['o:item_set'][0]['o:id']
        if 'crm:E28_Conceptual_Object' in x:
            collection = 2
        if 'dcterms:LocationPeriodOrJurisdiction' in x:
            collection = 3

        return id_node, name, collection
    else:

        return -1, '', -1

#Config genere type graph
total_graph = 1
graph_concept = 0
graph_concept_low = 0

_http = httplib2.Http()

nb_pages = 1
nb_item_per_page = 190
nb_annot = 1181

# URL Omeka-s API
# base_url_collections = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id=717270&per_page=200"
# base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
# base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"
base_url_annot = "http://psig.huma-num.fr/omeka-s/api/annotations/"

collection_cartes_anciennes = 717270
collection_carte_topo = 711991
base_url_items_collection = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id=" + str(collection_cartes_anciennes)
base_url_items_collection2 = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id=" + str(collection_carte_topo)

base_url_list = [base_url_items_collection, base_url_items_collection2]

print(base_url_items_collection)

G = nx.Graph()
i = 0

for iter_base_url in base_url_list:

    # iter_base_url = base_url_items_collection

    color_group_node = 0
    color_group_value = 1
    color_group_concept = 2  # objet conceptuel
    color_group_concept_topo = 3  # objet periode lieux juridiction

    # Request URL
    x = request(iter_base_url)

    nb_items = len(x)
    print(' !!!! taille items : ' + str(len(x)))

    print("all request : " + str(x))
    for item in range(0, nb_items):
        i += 1

        print("request x : " + str(x[item]))

        # attention, pour futur changement, il faut changer le type, par exemple : 'dctype:Image'
        if x[item]['@type'][1] == 'bibo:Map':

            # source is an item (not conceptual)
            id_node_source = x[item]['o:id']
            name_node_source = x[item]['dcterms:title'][0]['@value'].encode('utf8')
            collection_source = color_group_node

            print('__________________________________________________________________')
            print(str(i) + " --- " + str(id_node_source) + " --- " + str(name_node_source))

            # nb_annot = len(json_item[item]['oa:Annotation'])
            # print 'nb annots : ' + str(nb_annot)
            # print '   ' + str(json_item[item]['oa:Annotation'])

            if 'oa:Annotation' in x[item]:
                # print "Annotations found ! " +  " for " + str(id_node_source)

                # for id_annotation in x[item]['oa:Annotation']:
                #    print "in for oa:Annotation"

                url_annot = x[item]['oa:Annotation']

                for annotation in x[item]['oa:Annotation']:

                    # print "in for oa:Annotation 2"

                    print('url annotation : ' + annotation['@id'])
                    x_annotation = request(annotation['@id'])
                    annotation_id = annotation['o:id']

                    # print x_annotation

                    if 'oa:hasBody' in x_annotation:

                        target_value_node_name = ''

                        for inbody in x_annotation['oa:hasBody']:
                            if 'rdf:value' in inbody:
                                # print '         ' + str(x_annotation['oa:hasTarget'][0]['oa:hasSource'][0])
                                # !!! attention, property id peut être @id ?

                                print(inbody)

                                # value
                                if '@value' in inbody['rdf:value'][0]:
                                    # if 'rien' in inbody['rdf:value'][0]:

                                    # id_node_target = inbody['rdf:value'][0]['property_id']
                                    target_value_node_name = inbody['rdf:value'][0]['@value']

                                    # id_node_target, target_node_name, target_node_collection = read_node(url)

                                    print('     annotation n° ' + str(annotation_id))
                                    print('     ' + target_value_node_name)

                                    # link item -> value
                                    if total_graph == 1:
                                        add_link(id_node_source, name_node_source, collection_source,
                                                 annotation_id, target_value_node_name, color_group_value, '', 1.0, 8, 4)
                                        print('     link added for value' + '(' + str(id_node_source) + ') -> ' + '(' + str(
                                            annotation_id) + ')')

                                if '@id' in inbody['rdf:value'][0]:
                                    url = inbody['rdf:value'][0]['@id']

                                    id_node_target, target_node_name, target_node_collection = read_node(url)

                                    print('     annotation n° ' + str(id_node_target))

                                    # remove for value - concepts only - for concepts low
                                    if graph_concept_low != 1:
                                        add_link(id_node_source, name_node_source, collection_source,
                                                 id_node_target, target_node_name, color_group_concept, '', 3.0, 4, 4)
                                        print('     link added for ressource' + '(' + str(
                                            id_node_source) + ') -> ' + '(' + str(id_node_target) + ')')

                                    # add_link between value and concept
                                    add_link(id_node_target, target_node_name, color_group_concept,
                                             annotation_id, target_value_node_name, color_group_value, '', 3.0, 4, 4)
                                    print('     link added for value - concept' + '(' + str(
                                        id_node_target) + ' ' + target_node_name + ') -> (' + str(
                                        annotation_id) + ' ' + target_value_node_name + ')')

    print('end requests')

cpt_nodes = 0
nodes = []
tab_nodes_neo = []
for i in G.nodes():
    G.nodes[i]['id'] = cpt_nodes
    print('node ' + str(i))
    nodes.append({'id': G.nodes[i]['id'], 'id_item': G.nodes[i]['id_item'], 'name': G.nodes[i]['name'],
                  'group': str(G.nodes[i]['group']), 'radius': str(G.nodes[i]['radius'])})
    cpt_nodes += 1

print(nodes)
print("nombre de noeuds : " + str(len(nodes)))
# tx.commit()

# nodes = [{'id': G.nodes[i]['id'], 'name': str(G.nodes[i]['name']), 'group': str(G.nodes[i]['group'])} for i in G.nodes()]
links = [{'source': G.nodes[u[0]]['id'], 'target': G.nodes[u[1]]['id'],
          'motivation': G.edges[u]['motivation'], 'weight': G.edges[u]['weight']} for u in G.edges()]

print("nombre de liens : " + str(len(links)))

print('export graph as json')

suffix = ''

date = '_02_2022'

if total_graph:
    suffix = date+ '.json'
if graph_concept:
    suffix = date + '_concepts.json'
if graph_concept_low:
    suffix = date + '_concepts_low.json'

filename = 'C:\\Users\\Eric Mermet\\Desktop\\PycharmProjects\\OronceFine\\scripts\\omeka-sgraph_annotations_collection_' + str(collection_cartes_anciennes) + suffix
# with open(filename, 'w', encoding='utf8') as f:
with io.open(filename, 'wb') as f:
     json.dump({'nodes': nodes, 'links': links},
               f, indent=4, )


print('ok')