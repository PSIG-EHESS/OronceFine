#!/usr/bin/env python
# coding: utf8

import os
import httplib2
from xml.dom.minidom import parseString
#c:\Python27\Scripts\pip2.7.exe install pyshp
import shapefile
#c:\Python27\Scripts\pip2.7.exe install pyproj
from pyproj import Proj, transform
#c:\Python27\Scripts\pip2.7.exe install gsconfig
from geoserver.catalog import Catalog
import zipfile

#Paramètres
prenom_nom = 'EricMermet'
dir = 'C:\\Users\Eric\\PycharmProjects\\Omeka_api\\'
research_string = 'pontoise'

base_url_search = "http://api.geonames.org/search?q="+research_string+"&south=40&north=50&west=0&east=100&maxRows=408&username=puck"

def request(url):
    print '____ querying : ' + url
    resp, content = _http.request(url, "GET")  # , body=data, headers=headers)
    parser = parseString(content)
    return parser

def get_element(dict,string):
    return dict.getElementsByTagName(string)[0].firstChild.data

def getWKT_PRJ (epsg_code):
    import urllib
    wkt = urllib.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code))
    remove_spaces = wkt.read().replace(" ","")
    output = remove_spaces.replace("\n", "")
    return output

#Début du programme
_http = httplib2.Http()

xml_items = request(base_url_search)
#print xml_items

nb_elements = int(xml_items.getElementsByTagName('totalResultsCount')[0].firstChild.data)
#nb_elements = int(get_element(xml_items, 'toponymName'))
print "le nombre d'éléments est de " + str(nb_elements)

if nb_elements == 0:
    print 'pas de géométrie : exit'
    exit()

data = dict()
geonames = xml_items.getElementsByTagName('geoname')
for geoname in geonames:
    toponymName = get_element(geoname,'toponymName')
    name = get_element(geoname, 'name')
    lat = get_element(geoname, 'lat')
    lng = get_element(geoname, 'lng')
    geonameid = get_element(geoname, 'geonameId')
    countrycode = get_element(geoname, 'countryCode')
    countryname = get_element(geoname, 'countryName')
    fcl = get_element(geoname, 'fcl')
    fcode = get_element(geoname, 'fcode')
    data[geonameid] = {'toponymName': toponymName, 'name': name, 'lat': lat, 'lng': lng, 'countryCode': countrycode,
                        'countryName': countryname, 'fcl': fcl, 'fcode': fcode}

print data

dir_out = dir+'out\\'

#Pour écrire dans un fichier Shapefile
w = shapefile.Writer(dir_out+'geonames'+prenom_nom+'.shp')
w.field('name', 'C')

for lieu in data:
    #print lieu['name'] + ' ' + str(lieu['lat']) + ' ' + str(lieu['long'])
    print data[lieu]['name'] + ' ' + str(data[lieu]['lat']) + ' ' + str(data[lieu]['lng'])
    #w.point(data[lieu]['lng'], data[lieu]['lat'])
    w.point(float(data[lieu]['lng']), float(data[lieu]['lat']))
    w.record(data[lieu]['name'])

#Fermer le fichier shapefile, lorsque les données sont écrites
w.close()

#Puis gérer la projection, qui n'est pas gérée par la lib pyshp
prj = open(dir_out+'geonames'+prenom_nom+'.prj', "w")
epsg = getWKT_PRJ("4326")
prj.write(epsg)
prj.close()

#On zippe les fichiers du shp
print 'zip files'
print dir_out+'geonames.zip'
os.chdir(dir_out)
with zipfile.ZipFile(dir_out+'geonames'+prenom_nom+'.zip', 'w') as myzip:
    for item in os.listdir(dir_out):
        print item
        if item.startswith('geonames'+prenom_nom+'.zip'):
            continue
        if item.startswith('geonames'+prenom_nom+'.'):
            print '___zip'
            myzip.write(item)
print 'zip ok'

print 'publie la couche sur geoserver'

# geoserver post parameters
url = 'http://psig.huma-num.fr/geoserver/rest'
cat = Catalog(url, username="TAIS", password="TAIS2019")
workspace = cat.get_workspace("TAIS")

print 'url du workspace ' + str(workspace)

shapefile_plus_sidecars = dir_out+'geonames'+prenom_nom+'.zip'
print shapefile_plus_sidecars

print 'export shp to geoserver'
layer_name = 'geonamesTP'+prenom_nom

#un peu de ménage avant dans geoserver : on efface l'entrepot et la couche si la couche est déjà présente

layer = cat.get_layer('TAIS:geonames'+prenom_nom)
print 'layer is ' + str(layer)
if layer:
    cat.delete(layer)
    cat.reload()

store = cat.get_store('w_'+layer_name)
print 'store is ' + str(store)
if store:
    print 'del store ' + str(store)
    cat.delete(store)
    cat.reload()

print 'create layer ' + layer_name
ft = cat.create_featurestore('w_'+layer_name, workspace=workspace, data=shapefile_plus_sidecars)
print 'create layer : ok'