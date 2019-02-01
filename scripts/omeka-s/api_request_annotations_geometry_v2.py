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
import shapefile
from pygeoif import geometry

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

def search_in_dict(dict_or_list, key_to_search, search_for_first_only=False):

    search_result = set()
    if isinstance(dict_or_list, dict):
        for key in dict_or_list:
            key_value = dict_or_list[key]
            if key == key_to_search:
                if search_for_first_only:
                    return key_value
                else:
                    search_result.add(key_value)
            if isinstance(key_value, dict) or isinstance(key_value, list) or isinstance(key_value, set):
                _search_result = search_in_dict(key_value, key_to_search, search_for_first_only)
                if _search_result and search_for_first_only:
                    return _search_result
                elif _search_result:
                    for result in _search_result:
                        search_result.add(result)
    elif isinstance(dict_or_list, list) or isinstance(dict_or_list, set):
        for element in dict_or_list:
            if isinstance(element, list) or isinstance(element, set) or isinstance(element, dict):
                _search_result = search_in_dict(element, key_to_search, search_result)
                if _search_result and search_for_first_only:
                    return _search_result
                elif _search_result:
                    for result in _search_result:
                        search_result.add(result)
    return search_result if search_result else None

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

#START HERE

_http = httplib2.Http()

nb_pages = 190
nb_item_per_page = 1500
nb_annot = 100

# URL Omeka-s API
base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"

G = nx.Graph()

dir = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\'

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

    filename = dir + '\\scripts\\out\\export_annotations_for_geometries.json'
    with open(filename, 'w') as f:
        json.dump(x,
                  f, indent=4, )

    # Pour écrire dans un fichier Shapefile
    dir_out = dir + '..\\out\\'

    w_points = shapefile.Writer(dir_out + 'shape_all_geom_omeka_points' + '.shp')
    w_points.field('id', 'N')
    w_points.field('name', 'C')
    w_points.field('collection', 'C', size=255)

    w_lines = shapefile.Writer(dir_out + 'shape_all_geom_omeka_lines' + '.shp')
    w_lines.field('id', 'N')
    w_lines.field('name', 'C')
    w_lines.field('collection', 'C', size=255)

    w_polygons = shapefile.Writer(dir_out + 'shape_all_geom_omeka_polygons' + '.shp')
    w_polygons.field('id', 'N')
    w_polygons.field('name', 'C')
    w_polygons.field('collection', 'C', size=255)

    w_bbox = shapefile.Writer(dir_out + 'shape_all_geom_omeka_bbox' + '.shp')
    w_bbox.field('id', 'N')
    w_bbox.field('name', 'C')
    w_bbox.field('collection', 'C', size=255)

    w_centroid = shapefile.Writer(dir_out + 'shape_all_geom_omeka_centroid' + '.shp')
    w_centroid.field('id', 'N')
    w_centroid.field('name', 'C')
    w_centroid.field('collection', 'C', size=255)

    i = 0
    for item in range(0, nb_annot):
        print 'id = ' + str(i)
        #print 'keys top ' + str(x[item])
        print 'annotation #' + str(x[item]['o:id'])
        name = ''
        collection = ''

        if 'oa:hasTarget' in x[item]:
            #print 'oa:hasTarget -> ' + str(x[item]['oa:hasTarget'])
            if 'oa:hasSelector' in x[item]['oa:hasTarget'][0]:

                #get name here TODO
                #name = x[item]['oa:hasTarget'][0]['']['']
                #get collection here TODO
                #collection = x[item]['oa:hasTarget'][0]['']['']

                #print '     oa:hasSelector -> ' + str(x[item]['oa:hasTarget'][0]['oa:hasSelector'])
                if 'rdf:value' in x[item]['oa:hasTarget'][0]['oa:hasSelector']:

                    #print '         rdf:value' + str(x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'])
                    if 'type' in x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'][0] and x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'][0]['type'] == "geometry:geometry":

                        geom_wkt = x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'][0]['@value']
                        #print 'geometry found : ' + geom_wkt

                        p = geometry.from_wkt(geom_wkt)

                        #print p.__geo_interface__

                        if p.__geo_interface__['type'] == 'Point':
                            print "it's a point : " + str(p.__geo_interface__['coordinates'][0]) + ' ' + str(p.__geo_interface__['coordinates'][1])
                            w_points.point(p.__geo_interface__['coordinates'][0], p.__geo_interface__['coordinates'][1])
                            w_points.record(i, name, collection)

                        if p.__geo_interface__['type'] == 'LineString':
                            print "it's a line : " + str(p.__geo_interface__['coordinates'])
                            w_lines.line(p.__geo_interface__['coordinates'])
                            w_lines.record(i, name, collection)

                        if p.__geo_interface__['type'] == 'Polygon':
                            print "it's a polygon : " + str(p.__geo_interface__['coordinates'])
                            w_polygons.poly(p.__geo_interface__['coordinates'])
                            w_polygons.record(i, name, collection)

                        print 'bounding box'
                        w_bbox.poly(p.__geo_interface__['bbox'])
                        w_bbox.record(i, name, collection)

                        print 'centroid'
                        minx, miny, maxx, maxy = p.bounds()
                        w_centroid.point(mean([minx, maxx]), mean([miny, maxy]) )
                        w_centroid.record(i, name, collection)

        i += 1

    w_points.close()
    w_lines.close()
    w_polygons.close()
    w_centroid.close()

        # print 'searching for POINT'
        # results_searching_points = pretty_search(x[item], 'POINT', False)
        # print results_searching_points
        #
        # print 'searching for LINESTRING'
        # results_searching_points = pretty_search(x[item], 'LINESTRING', False)
        # print results_searching_points
        #
        # print 'searching for POLYGON'
        # results_searching_points = pretty_search(x[item], 'POLYGON', False)
        # print results_searching_points

