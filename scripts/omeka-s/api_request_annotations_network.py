#!/usr/bin/env python
# coding: utf8

import json
import requests
import httplib2
import networkx as nx
import matplotlib.pyplot as plt

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

_http = httplib2.Http()

nb_pages = 1
nb_item_per_page = 190
nb_annot = 434

# URL Omeka-s API
base_url_collections = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id=630970&per_page=200"
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"
base_url_annot = "http://psig.huma-num.fr/omeka-s/api/annotations/"

iter_base_url = base_url_collections

#Request URL
json_item = request(iter_base_url)

i=0
for item in range(0, nb_item_per_page):
    i += 1
    print str(i) + " " + str(json_item[item]['o:id'])
    nb_annot = len(json_item[item]['o-module-annotate:annotation'])
    print 'nb annots : ' + str(nb_annot)
    #print '   ' + str(json_item[item]['o-module-annotate:annotation'])

    for id_annotation in range(0, nb_annot):

        url_annot = json_item[item]['o-module-annotate:annotation'][id_annotation]['@id']
        #print '     url annot = ' + str(url_annot)
        json_annot = request(url_annot)

        print "         " + str(id_annotation) + " " + str(json_annot['o:id'])

        # if 'locating' not in json_annot['motivation']:
        #     print 'pas locating'
        #     continue
        # else:
        if 'selector' not in json_annot['target']:
            print 'no selector'
            continue
        else:
            #locate ?
            if 'value' not in  json_annot['target']['selector']['value']:
                print 'no value in selector'
            else:
                print '         geometry locate = ' + json_annot['target']['selector']['value']
            #describe ?
            if 'refinedBy' not in json_annot['target']['selector']:
                print '         pas de refinedBy'
                continue
            else:
                print '         geometry describe = ' + json_annot['target']['selector']['refinedBy']['value']