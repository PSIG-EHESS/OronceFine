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

def request_api(url):
    print '____ querying ' + url

    # Assemble the URL and query the web service
    # r = requests.get(base_url)#, params=payload)
    # prepared = r.prepare()
    # print prepared

    resp, content = _http.request(url, "GET")  # , body=data, headers=headers)

    # print '--resp--'
    # print resp
    # print '--content--'
    # print content

    x_json = json.loads(content)

    return x_json

def getWKT_PRJ (epsg_code):
    import urllib
    wkt = urllib.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code))
    remove_spaces = wkt.read().replace(" ","")
    output = remove_spaces.replace("\n", "")
    return output

def create_shapefile(dir_out, name):
    # Puis gérer la projection, qui n'est pas gérée par la lib pyshp
    prj = open(dir_out + name + '.prj', "w")
    epsg = getWKT_PRJ("4326")
    prj.write(epsg)
    prj.close()

    w = shapefile.Writer(dir_out + name + '.shp')
    w.field('id', 'N')
    w.field('id_item', 'N')
    w.field('name_item', 'C', size=255)
    w.field('type_item', 'C', size=100)
    w.field('collection', 'C', size=255)
    w.field('url_item', 'C', size=255)
    w.field('url_media', 'C', size=255)
    w.field('url_media_jpg', 'C', size=255)
    w.field('date', 'C')

    return w

#START HERE

_http = httplib2.Http()

nb_pages = 190
nb_item_per_page = 1500
nb_annot = 1353

# URL Omeka-s API
base_url = "http://psig.huma-num.fr/omeka-s/api/annotations?per_page="+str(nb_item_per_page)
#base_url = "http://psig.huma-num.fr/omeka-s/api/annotations/634695"
base_url_items = "http://psig.huma-num.fr/omeka-s/api/items/"

G = nx.Graph()

dir = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\'
dir_out = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\scripts\\out\\shp\\'

for page in range(1):

    #iter_page = page + 1

    iter_base_url = base_url

    x = request_api(iter_base_url)

    filename = dir + '\\scripts\\out\\export_annotations_for_geometries.json'
    with open(filename, 'w') as f:
        json.dump(x,
                  f, indent=4, )

    # Pour écrire dans un fichier Shapefile

    w_points = create_shapefile(dir_out, 'shape_all_geom_omeka_points')
    w_lines = create_shapefile(dir_out, 'shape_all_geom_omeka_lines')
    w_polygons = create_shapefile(dir_out, 'shape_all_geom_omeka_polygons')
    w_bbox = create_shapefile(dir_out, 'shape_all_geom_omeka_bbox')
    w_centroid = create_shapefile(dir_out, 'shape_all_geom_omeka_centroid')

    print w_polygons

    # w_lines = shapefile.Writer(dir_out + 'shape_all_geom_omeka_lines' + '.shp')
    # w_lines.field('id', 'N')
    # w_lines.field('id_item', 'N')
    # w_lines.field('name_item', 'C', size=255)
    # w_lines.field('type_item', 'C', size=100)
    # w_lines.field('collection', 'C', size=255)
    # w_lines.field('url_item', 'C', size=255)
    # w_lines.field('url_media', 'C', size=255)
    # w_lines.field('url_media_jpg', 'C', size=255)
    # w_lines.field('date', 'C')
    #
    # w_polygons = shapefile.Writer(dir_out + 'shape_all_geom_omeka_polygons' + '.shp')
    # w_polygons.field('id', 'N')
    # w_polygons.field('id_item', 'N')
    # w_polygons.field('name_item', 'C', size=255)
    # w_polygons.field('type_item', 'C', size=100)
    # w_polygons.field('collection', 'C', size=255)
    # w_polygons.field('url_item', 'C', size=255)
    # w_polygons.field('url_media', 'C', size=255)
    # w_polygons.field('url_media_jpg', 'C', size=255)
    # w_polygons.field('date', 'C')
    #
    # w_bbox = shapefile.Writer(dir_out + 'shape_all_geom_omeka_bbox' + '.shp')
    # w_bbox.field('id', 'N')
    # w_bbox.field('id_item', 'N')
    # w_bbox.field('name_item', 'C', size=255)
    # w_bbox.field('type_item', 'C', size=100)
    # w_bbox.field('collection', 'C', size=255)
    # w_bbox.field('url_item', 'C', size=255)
    # w_bbox.field('url_media', 'C', size=255)
    # w_bbox.field('url_media_jpg', 'C', size=255)
    # w_bbox.field('date', 'C')
    #
    # w_centroid = shapefile.Writer(dir_out + 'shape_all_geom_omeka_centroid' + '.shp')
    # w_centroid.field('id', 'N')
    # w_centroid.field('id_item', 'N')
    # w_centroid.field('name_item', 'C', size=255)
    # w_centroid.field('type_item', 'C', size=100)
    # w_centroid.field('collection', 'C', size=255)
    # w_centroid.field('url_item', 'C', size=255)
    # w_centroid.field('url_media', 'C', size=255)
    # w_centroid.field('url_media_jpg', 'C', size=255)
    # w_centroid.field('date', 'C')

    i = 0
    cpt_points = 0
    cpt_lines = 0
    cpt_poly = 0
    cpt_bbox = 0
    cpt_centroid = 0
    for item in range(0, nb_annot):
        print 'id = ' + str(i)
        #print 'keys top ' + str(x[item])
        print 'annotation #' + str(x[item]['o:id'])
        name_item = ''
        id_item = 0
        collection_item = ''
        type_item = ''
        url_item = ''
        url_media = ''
        url_media_jpg = ''
        date = '1-2000'

        if 'oa:hasTarget' in x[item]:
            #print 'oa:hasTarget -> ' + str(x[item]['oa:hasTarget'])
            if 'oa:hasSelector' in x[item]['oa:hasTarget'][0]:

                if 'oa:hasSource' in x[item]['oa:hasTarget'][0]:
                    # get name here
                    name_item = x[item]['oa:hasTarget'][0]['oa:hasSource'][0]['display_title']
                    # get id here
                    id_item = x[item]['oa:hasTarget'][0]['oa:hasSource'][0]['value_resource_id']
                    #get type value_resource_name
                    type_item = x[item]['oa:hasTarget'][0]['oa:hasSource'][0]['value_resource_name']
                    #get url item
                    url_item = x[item]['oa:hasTarget'][0]['oa:hasSource'][0]['@id' \
                                                                             '']
                    #get item via API
                    x_item = request_api(base_url_items+str(id_item))

                    # get collection here TODO
                    if len(x_item['o:item_set']) > 0 and 'o:id' in x_item['o:item_set'][0]:
                        collection_item = x_item['o:item_set'][0]['o:id']

                    if len(x_item['o:media']) > 0 and '@id' in x_item['o:media'][0]:
                        url_media = x_item['o:media'][0]['@id']

                        # get item via API
                        x_media = request_api(url_media)
                        if 'medium' in x_media['o:thumbnail_urls']:
                            print url_media_jpg
                            url_media_jpg = str(x_media['o:thumbnail_urls']['medium'])

                #print '     oa:hasSelector -> ' + str(x[item]['oa:hasTarget'][0]['oa:hasSelector'])
                if 'rdf:value' in x[item]['oa:hasTarget'][0]['oa:hasSelector']:

                    #print '         rdf:value' + str(x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'])
                    if 'type' in x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'][0] and x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'][0]['type'] == "geometry:geography":

                        geom_wkt = x[item]['oa:hasTarget'][0]['oa:hasSelector']['rdf:value'][0]['@value']
                        print 'geometry found : ' + geom_wkt

                        p = geometry.from_wkt(geom_wkt)

                        print p.__geo_interface__

                        if p.__geo_interface__['type'] == 'Point':
                            print "it's a point : " + str(p.__geo_interface__['coordinates'][0]) + ' ' + str(p.__geo_interface__['coordinates'][1])
                            w_points.point(p.__geo_interface__['coordinates'][0], p.__geo_interface__['coordinates'][1])
                            w_points.record(i, id_item, name_item, type_item, collection_item, url_item, url_media, url_media_jpg, date)
                            cpt_points += 1

                        if p.__geo_interface__['type'] == 'LineString':
                            print "it's a line : " + str(p.__geo_interface__['coordinates'])
                            part_line = []
                            line = []
                            for point in p.__geo_interface__['coordinates']:
                                print point
                                point_tab = [point[0], point[1]]
                                line.append(point_tab)
                            print line
                            part_line.append(line)
                            w_lines.line(part_line)
                            w_lines.record(i, id_item, name_item, type_item, collection_item, url_item, url_media, url_media_jpg, date)
                            cpt_lines += 1

                        if p.__geo_interface__['type'] == 'Polygon':
                            print "it's a polygon : " + str(p.__geo_interface__['coordinates'])
                            w_polygons.poly(p.__geo_interface__['coordinates'])
                            w_polygons.record(i, id_item, name_item, type_item, collection_item, url_item, url_media, url_media_jpg, date)
                            cpt_poly += 1

                        print 'bounding box / centroid'
                        pointx_centroid = 0
                        pointy_centroid = 0

                        if p.__geo_interface__['type'] != 'Point':
                            minx = min(p.__geo_interface__['bbox'][0], p.__geo_interface__['bbox'][2])
                            maxx = max(p.__geo_interface__['bbox'][0], p.__geo_interface__['bbox'][2])
                            miny = min(p.__geo_interface__['bbox'][1], p.__geo_interface__['bbox'][3])
                            maxy = max(p.__geo_interface__['bbox'][1], p.__geo_interface__['bbox'][3])

                            point1 = [minx, miny]
                            point2 = [minx, maxy]
                            point3 = [maxx, maxy]
                            point4 = [maxx, miny]

                            pointx_centroid = mean([minx, maxx])
                            pointy_centroid = mean([miny, maxy])

                            poly = [point1, point2, point3, point4]
                            print poly
                            w_bbox.poly([[point1, point2, point3, point4, point1]])
                            w_bbox.record(i, id_item, name_item, type_item, collection_item, url_item, url_media, url_media_jpg, date)
                            cpt_bbox += 1

                        else:

                            pointx_centroid = p.__geo_interface__['coordinates'][0]
                            pointy_centroid = p.__geo_interface__['coordinates'][1]

                        print 'centroid'
                        w_centroid.point(pointx_centroid, pointy_centroid )
                        w_centroid.record(i, id_item, name_item, type_item, collection_item, url_item, url_media, url_media_jpg, date)
                        cpt_centroid += 1

        i += 1

    w_points.close()
    w_lines.close()
    w_polygons.close()
    w_centroid.close()

    print 'nb records ' + str(i)
    print 'nb records points ' + str(cpt_points)
    print 'nb records lines ' + str(cpt_lines)
    print 'nb records polys ' + str(cpt_poly)
    print 'nb records bbox ' + str(cpt_bbox)
    print 'nb records centroid ' + str(cpt_centroid)

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