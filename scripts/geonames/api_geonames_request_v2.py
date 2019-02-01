#!/usr/bin/env python
# coding: utf8

import httplib2
from xml.dom.minidom import parseString
import shapefile

#Collection Pontoise
#http://psig.huma-num.fr/omeka-s/api/items?item_set_id=630970

base_url_search = "http://api.geonames.org/search?q=pontoise&south=40&north=50&west=0&east=10&maxRows=10&username=puck"
base_url_wikipedia = "http://api.geonames.org/wikipediaBoundingBox?north=44.1&south=-9.9&east=-22.4&west=55.2&username=puck"

def request(url):
    #print '____ querying : ' + url
    resp, content = _http.request(url, "GET")  # , body=data, headers=headers)
    parser = parseString(content)
    return parser

#Début

_http = httplib2.Http()

xml_items = request(base_url_search)
#print xml_items

nb_elements = xml_items.getElementsByTagName('totalResultsCount')[0].firstChild.data
print "le nombre d'éléments est de " + str(nb_elements)

data = dict()
geonames = xml_items.getElementsByTagName('geoname')
for geoname in geonames:
    toponymName = geoname.getElementsByTagName('toponymName')[0].firstChild.data
    name = geoname.getElementsByTagName('name')[0].firstChild.data
    lat = geoname.getElementsByTagName('lat')[0].firstChild.data
    lng = geoname.getElementsByTagName('lng')[0].firstChild.data
    geonameid = geoname.getElementsByTagName('geonameId')[0].firstChild.data
    countrycode = geoname.getElementsByTagName('countryCode')[0].firstChild.data
    countryname = geoname.getElementsByTagName('countryName')[0].firstChild.data
    fcl = geoname.getElementsByTagName('fcl')[0].firstChild.data
    fcode = geoname.getElementsByTagName('fcode')[0].firstChild.data
    data[geonameid] = {'toponymName': toponymName, 'name': name, 'lat': lat, 'lng': lng, 'countryCode': countrycode,
                        'countryName': countryname, 'fcl': fcl, 'fcode': fcode}

print data

#Pour écrire dans un fichier Shapefile
w = shapefile.Writer('C:\\Users\Eric\\PycharmProjects\\Omeka_api\\out\\geonames.shp')
w.field('name', 'C')

for lieu in data:
    #print lieu['name'] + ' ' + str(lieu['lat']) + ' ' + str(lieu['long'])
    print data[lieu]['name'] + ' ' + str(data[lieu]['lat']) + ' ' + str(data[lieu]['lng'])
    w.point(data[lieu]['lat'], data[lieu]['lng'])
    w.record(data[lieu]['name'])

    w.close()