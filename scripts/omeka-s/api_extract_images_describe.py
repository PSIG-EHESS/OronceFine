#!/usr/bin/env python
# coding: utf8

import json
import httplib2
import numpy
from PIL import Image, ImageDraw
from pygeoif import geometry
import requests

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

def clip_image (imArray, geom, dir_out, item_id, annotation_id, bounds, subtitle_annotation):

    print 'in clip image'
    # create mask

    polygon = geom
    minx = bounds[0]
    miny = bounds[1]
    maxx = bounds[2]
    maxy = bounds[3]

    #print str(minx) + " " + str(miny) + " " + str(maxx) + " " + str(maxy)

    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape, dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:, :, :3] = imArray[:, :, :3]

    # transparency (4th column)
    newImArray[:, :, 3] = mask * 255

    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGBA")

    # clip in bounds
    cropped_image = newIm.crop(bounds)

    # flip image
    imReflipped = cropped_image.transpose(Image.FLIP_TOP_BOTTOM)

    imReflipped.save(dir_out+"out_"+str(item_id)+"_"+str(annotation_id)+"_"+subtitle_annotation[0:10]+".png")

#START HERE

_http = httplib2.Http()

nb_item_per_page = 50
nb_annot = 6577
nb_last_items = 6577 % 25

#nb_pages_max = int(math.ceil(nb_annot / nb_item_per_page)) + 1
nb_pages_max = 1

#print 'pages max = ' + str(nb_pages_max)
#print 'reste dernière page = ' + str(nb_last_items)

# URL Omeka-s API
# collection Creuse : 641829
# collection Bertin : 9
id_collection = 9

#base_url_pages = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id="+str(id_collection)

collection_cartes_anciennes = 717270
#collection_carte_topo = 711991
base_url_pages = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id="+str(collection_cartes_anciennes)
#base_url_items_collection2 = "http://psig.huma-num.fr/omeka-s/api/items?item_set_id="+str(collection_carte_topo)

#base_url_pages = [base_url_items_collection, base_url_items_collection2]

dir = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\'
dir_out = 'C:\\Users\\Eric\\PycharmProjects\\OronceFine\\scripts\\out\\img\\'

for iter_page in range(1, nb_pages_max+1):

    base_url_pages_num = base_url_pages #+ str(iter_page)

    #iter_page = page + 1

    #iter_base_url = base_url
    iter_base_url = base_url_pages_num

    x = request_api(iter_base_url)

    filename = dir + '\\scripts\\out\\export_annotations_for_geometries_pacha.json'
    with open(filename, 'w') as f:
        json.dump(x,
                  f, indent=4, )

    # change range for the last page
    #if iter_page == nb_pages_max:
    #    print 'last page !!'
    #    nb_item_per_page = nb_last_items

    i = 0

    for item in range(0, nb_item_per_page):
        print 'page = ' + str(iter_page)
        #print 'id = ' + str(i)
        #print 'keys top ' + str(x[item])
        item_id = x[item]['o:id']
        print 'item #' + str(item_id) + " id i = " + str(i)
        x_item = x[item]
        collection_item = ''
        type_item = ''
        url_item = ''
        url_media = ''
        url_media_jpg = ''
        date = '1-2000'

        #get media for item:
        #print x_item
        #print x_item['o:media']
        if 'o:media' in  x_item and len(x_item['o:media']) > 0:
            if '@id' in x_item['o:media'][0]:
                #print 'pass'
                url_media = x_item['o:media'][0]['@id']
                #print url_media
                # get item via API
                url_media_jpg = ''
                x_media = request_api(url_media)
                print x_media
                if 'o:original_url' in x_media:
                    #print url_media_jpg
                    url_media_jpg = str(x_media['o:original_url'])
                print 'url media =              ' + str(url_media_jpg)
        else:
            #pas d'image on passe à l'objet suivant
            print "pas d'image"
            continue

        # read image as RGB and add alpha (transparency)

        r = requests.get(url_media_jpg, stream=True)
        r.raw.decode_content = True
        im = Image.open(r.raw).convert("RGBA")
        #im = Image.open("crop.jpg").convert("RGBA")
        #print(im.format, im.mode, im.size)

        # flip image
        imArrayFlipped = im.transpose(Image.FLIP_TOP_BOTTOM)

        # convert to numpy (for convenience)
        imArray = numpy.asarray(imArrayFlipped)

        if 'oa:Annotation' in x[item]:

            for annotation in x[item]['oa:Annotation']:

                #print 'has annotation ' + str(annotation)
                x_annotation = request_api(annotation['@id'])
                annotation_id = annotation['o:id']

                subtitle_annotation = ''
                if 'oa:hasBody' in x_annotation:
                    for rdf_value in x_annotation['oa:hasBody']:
                        #print rdf_value['rdf:value'][0]
                        if '@value' in rdf_value['rdf:value'][0]:
                            print rdf_value['rdf:value'][0]['@value']
                            subtitle_annotation = subtitle_annotation + rdf_value['rdf:value'][0]['@value'] + '_'

                #print x_annotation
                if 'oa:hasTarget' in x_annotation:
                    if 'oa:hasSelector' in x_annotation['oa:hasTarget'][0]:
                        if 'oa:refinedBy' in x_annotation['oa:hasTarget'][0]['oa:hasSelector']:
                            if 'rdf:value' in x_annotation['oa:hasTarget'][0]['oa:hasSelector']['oa:refinedBy']:
                                if x_annotation['oa:hasTarget'][0]['oa:hasSelector']['oa:refinedBy']['rdf:value'][0]['type'] == "geometry:geometry":
                                    geom_wkt = x_annotation['oa:hasTarget'][0]['oa:hasSelector']['oa:refinedBy']['rdf:value'][0]['@value']
                                    #print geom_wkt

                                    geoms = geometry.from_wkt(geom_wkt)
                                    bounds = geoms.bounds
                                    print bounds

                                    if geoms.__geo_interface__['type'] == 'Polygon':
                                        #print geoms.__geo_interface__['coordinates']

                                        str_geoms = str(geoms.__geo_interface__['coordinates'])
                                        #print str_geoms
                                        str_geoms_temp = str_geoms[2:-3]
                                        str_geoms_temp2 = str_geoms_temp
                                        #print str_geoms_temp2

                                        from ast import literal_eval

                                        list_geom = list(literal_eval(str_geoms_temp2))

                                        print 'subtitle annotation = ' + subtitle_annotation
                                        clip_image(imArray, list_geom, dir_out, item_id, annotation_id, bounds, subtitle_annotation)

    i = i+1