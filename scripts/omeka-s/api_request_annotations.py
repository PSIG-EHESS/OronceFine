#!/usr/bin/env python
# coding: utf8

import json
import io
import requests
import httplib2
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('Agg')

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

def read_node_source(url):

    if "http://" in url:
        resp_node, content_node = _http.request(url, "GET")  # , body=data, headers=headers)
        x = json.loads(content_node)
        return x['o:id']
    else:
        return -1

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

        if len(x['dcterms:title']) > 0 and '@value' in x['dcterms:title'][0]:
            name = x['dcterms:title'][0]['@value']
            #print 'nom in fonction : ' + name
        if len(x['o:item_set']) > 0 and 'o:id' in x['o:item_set'][0]:
            collection = x['o:item_set'][0]['o:id']

        return id_node, name, collection
    else:

        return -1, '', -1

_http = httplib2.Http()

nb_pages = 190
nb_item_per_page = 1500
nb_annot = 1349

# URL Omeka-s API
base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"

G = nx.Graph()

list_nodes = []

#iter_page = page + 1

iter_base_url = base_url

print '____ querying ' + base_url

# Assemble the URL and query the web service
#r = requests.get(base_url)#, params=payload)
# prepared = r.prepare()
# print prepared

resp, content = _http.request(iter_base_url, "GET")#, body=data, headers=headers)

#print '--resp--'
#print resp
#print '--content--'
#print content

x = json.loads(content)

filename = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\scripts\\out\\export_annotaions_omeka-s.json'
with open(filename, 'w') as f:
    json.dump(x,
              f, indent=4, )

i = 0
cpt_nodes = 0
for item in range(0, nb_annot):
    print '_____________________________'
    this_item = x[item]
    print 'id = ' + str(i)
    print 'keys top ' + str(this_item.keys())
    print 'annotation #' + str(this_item['o:id'])
    id_annotation = this_item['o:id']
    #print 'target : ' + str(x[item]['target'])
    if 'oa:motivatedBy' in this_item:
        motivation = this_item['oa:motivatedBy'][0]['@value']
    else:
        motivation = ''
    print '         motivation = ' + str(motivation)
    #print 'test 1 ' + str('oa:hasTarget' in this_item)
    #print 'test 2 ' + str('oa:hasSource' in this_item['oa:hasTarget'][0])
    if 'oa:hasTarget' not in this_item and 'oa:hasSource' not in this_item['oa:hasTarget'][0]:
        #ni target et/ou ni source
        continue
    else:
        this_item_target = this_item['oa:hasTarget']
        if 'oa:hasSource' in this_item_target[0]:
            print 'has Source and has Target'
            this_item_target_source = this_item_target[0]['oa:hasSource']
            id_node_source, name_node_source, collection_source = read_node(this_item_target_source[0]['@id'])
        else:
            'pass : source is not in target'
            continue
    print '         node name = ' + name_node_source
    print '         collection = ' + str(collection_source)
    #print '         node source = ' + str(x[item]['target']['source'])
    print '                 node start in int from url = ' + str(id_node_source)
    #G.add_node(node_source)

    #Extract body case
    if 'oa:hasBody' in x[item]:
        print 'in body'
        body = x[item]['oa:hasBody']
        #print '             type ' + str(type(x[item]['body']))
        #print '             body ' + str(x[item]['body'])

        if isinstance(body, dict):
            print '             value = ' + body['value']

        if isinstance(body, list):
            print '     len body = ' + str(len(body))

            for nb in range(0, len(body)):

                if '@id' in body[nb]:
                    print '       connection exists !'
                    value_url = body[nb]['@id']
                    #print 'type ' + type(x[item]['body'][nb]['value'])
                    print '             value = ' + value_url
                    id_node_target, target_node_name, target_node_collection = read_node(value_url)
                    #print '                 name = ' + str(unicode(target_node_name , errors='ignore'))
                    print '                 name = ' + target_node_name#.encode("latin-1"))

                    print '                 node end in int from url = ' + str(id_node_target)
                    #G.add_node(node_target)

                    print '                     connect : ' + str(id_node_source) + ' -- ' + str(id_node_target)

                    G.add_edge(id_node_source, id_node_target, motivation=str(motivation), weight=1.0)

                    G.nodes[id_node_source]['name'] = name_node_source#.encode("latin-1")) #récupérer le nom de l'item éventuellement
                    G.nodes[id_node_source]['id_item'] = id_node_source  # .encode("latin-1")) #récupérer le nom de l'item éventuellement
                    G.nodes[id_node_source]['group'] = collection_source  # récupérer le nom de l'item éventuellement
                    G.nodes[id_node_source]['color'] = collection_source  # récupérer le nom de l'item éventuellement

                    G.nodes[id_node_target]['name'] = target_node_name#.encode("latin-1")) #récupérer le nom de l'item éventuellement
                    G.nodes[id_node_target]['id_item'] = id_node_target  # .encode("latin-1")) #récupérer le nom de l'item éventuellement
                    G.nodes[id_node_target]['group'] = target_node_collection  # récupérer le nom de l'item éventuellement
                    G.nodes[id_node_target]['color'] = target_node_collection  # récupérer le nom de l'item éventuellement

    i += 1


#Extract nodes and links for json from Graph
cpt_nodes = 0
nodes = []
for i in G.nodes():
    G.nodes[i]['id'] = cpt_nodes
    nodes.append({'id': G.nodes[i]['id'], 'id_item': G.nodes[i]['id_item'], 'name': G.nodes[i]['name'], 'group': str(G.nodes[i]['group'])})
    cpt_nodes += 1

print nodes

#nodes = [{'id': G.nodes[i]['id'], 'name': str(G.nodes[i]['name']), 'group': str(G.nodes[i]['group'])} for i in G.nodes()]
links = [{'source': G.nodes[u[0]]['id'], 'target': G.nodes[u[1]]['id'],
      'motivation':G.edges[u]['motivation'], 'weight':G.edges[u]['weight']} for u in G.edges()]

print links

print 'export graph as json'
filename = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\scripts\\out\\graph_annotations_omeka-s.json'
#with open(filename, 'w', encoding='utf8') as f:
with io.open(filename, 'wb') as f:
    json.dump({'nodes': nodes, 'links': links},
              f, indent=4, )
print 'ok'