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
            print 'nom in fonction : ' + name
        if len(x['o:item_set']) > 0 and 'o:id' in x['o:item_set'][0]:
            collection = x['o:item_set'][0]['o:id']

        return id_node, name, collection
    else:

        return -1, '', -1

_http = httplib2.Http()

nb_pages = 190
nb_item_per_page = 1500
nb_annot = 1272

# URL Omeka-s API
base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"

G = nx.Graph()

for page in range(1):

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

    filename = 'C:\\Users\\Eric\\PycharmProjects\\Omeka_api\\out\\export_annotaions_omeka-s.json'
    with open(filename, 'w') as f:
        json.dump(x,
                  f, indent=4, )

    i = 0
    cpt_nodes = 0
    for item in range(0, nb_annot):
        print 'id = ' + str(i)
        print 'keys top ' + str(x[item].keys())
        print 'annotation #' + str(x[item]['o:id'])
        #print 'target : ' + str(x[item]['target'])
        print '         motivation = ' + str(x[item]['motivation'])
        print 'test 1 ' + str('target' not in x[item])
        print 'test 2 ' + str('source' not in x[item]['target'])
        if 'target' not in x[item] and 'source' not in x[item]['target']:
            continue
        else:
            if 'source' in x[item]['target']:
                node_source, name_source, collection_source = read_node(x[item]['target']['source'])
            else:
                'pass : source is not in target'
                continue
        print '         node name = ' + name_source
        print '         collection = ' + str(collection_source)
        #print '         node source = ' + str(x[item]['target']['source'])
        print '                 node start in int from url = ' + str(node_source)
        #G.add_node(node_source)

        #Extract body case
        if 'body' in x[item]:
            print 'in body'
            #print '             type ' + str(type(x[item]['body']))
            #print '             body ' + str(x[item]['body'])

            if isinstance(x[item]['body'], dict):

                print '             value = ' + x[item]['body']['value']

            if isinstance(x[item]['body'], list):

                print 'len body = ' + str(len(x[item]['body']))

                for nb in range(0, len(x[item]['body'])):

                    if 'value' in x[item]['body'][nb]:

                        #print 'type ' + type(x[item]['body'][nb]['value'])
                        print x[item]['body'][nb]['value']
                        print '             value = ' + x[item]['body'][nb]['value']
                        id_node_target, target_node_name, target_node_collection = read_node(x[item]['body'][nb]['value'])
                        #print '                 name = ' + str(unicode(target_node_name , errors='ignore'))
                        print '                 name = ' + target_node_name#.encode("latin-1"))

                        print '                 node end in int from url = ' + str(id_node_target)
                        #G.add_node(node_target)

                        G.add_edge(node_source, id_node_target, motivation=str(x[item]['motivation']), weight=1.0)

                        G.nodes[node_source]['name'] = target_node_name#.encode("latin-1")) #récupérer le nom de l'item éventuellement
                        G.nodes[node_source]['group'] = target_node_collection  # récupérer le nom de l'item éventuellement
                        G.nodes[node_source]['color'] = target_node_collection  # récupérer le nom de l'item éventuellement

                        G.nodes[id_node_target]['name'] = target_node_name#.encode("latin-1")) #récupérer le nom de l'item éventuellement
                        G.nodes[id_node_target]['group'] = target_node_collection  # récupérer le nom de l'item éventuellement
                        G.nodes[id_node_target]['color'] = target_node_collection  # récupérer le nom de l'item éventuellement

        i += 1

    #plt.subplot(121)

    #nx.draw(G, with_labels=True, font_weight='bold')

    # options = {
    #     'node_color': 'black',
    #     'node_size': 50,
    #     'width': 3,
    # }
    # nx.draw_random(G, **options)
    #
    # plt.show()

    #pos = nx.nx_agraph.graphviz_layout(G)
    #nx.draw(G, pos=pos)
    #write_dot(G, 'C:\\Users\\Eric\\PycharmProjects\\Omeka_api\\out\\network.dot')

    cpt_nodes = 0
    nodes = []
    for i in G.nodes():
        G.nodes[i]['id'] = cpt_nodes
        nodes.append({'id': G.nodes[i]['id'], 'name': G.nodes[i]['name'], 'group': str(G.nodes[i]['group'])})
        cpt_nodes += 1

    print nodes

    #nodes = [{'id': G.nodes[i]['id'], 'name': str(G.nodes[i]['name']), 'group': str(G.nodes[i]['group'])} for i in G.nodes()]
    links = [{'source': G.nodes[u[0]]['id'], 'target': G.nodes[u[1]]['id'],
          'motivation':G.edges[u]['motivation'], 'weight':G.edges[u]['weight']} for u in G.edges()]

    print links

    filename = 'C:\\Users\\Eric\\PycharmProjects\\Omeka_api\\out\\graph_annotations_omeka-s.json'
    #with open(filename, 'w', encoding='utf8') as f:
    with io.open(filename, 'wb') as f:
        json.dump({'nodes': nodes, 'links': links},
                  f, indent=4, )