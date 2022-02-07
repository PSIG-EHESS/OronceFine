#!/usr/bin/env python
# coding: utf8

import httplib2
from xml.dom.minidom import parseString
import shapefile

#Collection Pontoise
#http://psig.huma-num.fr/omeka-s/api/items?item_set_id=630970

#pontoise
#base_url_wikipedia = "http://api.geonames.org/wikipediaBoundingBox?north=49.06343&south=49.01818&east=2.13905&west=2.06387&lang=fr&maxRows=100&username=puck"

#demo
base_url_wikipedia = "http://api.geonames.org/wikipediaBoundingBox?north=44.1&south=-9.9&east=-22.4&west=55.2&username=puck"

def request(url):
    #print '____ querying : ' + url
    resp, content = _http.request(url, "GET")  # , body=data, headers=headers)
    parser = parseString(content)
    return parser

def get_element(dict,string):
    return dict.getElementsByTagName(string)[0].firstChild.data

#Début

_http = httplib2.Http()

xml_items = request(base_url_wikipedia)
#print xml_items

data = dict()
geonames_wiki = xml_items.getElementsByTagName('entry')

cpt = 0
for geoname in geonames_wiki:
    nom = geoname.getElementsByTagName('title')[0].firstChild.data
    resume = geoname.getElementsByTagName('summary')[0].firstChild.data
    #type = geoname.getElementsByTagName('feature')[0].firstChild.data
    altitude = geoname.getElementsByTagName('elevation')[0].firstChild.data
    lat = geoname.getElementsByTagName('lat')[0].firstChild.data
    lng = geoname.getElementsByTagName('lng')[0].firstChild.data
    url_wikipedia = geoname.getElementsByTagName('wikipediaUrl')[0].firstChild.data
    url_media = ''
    if geoname.getElementsByTagName('thumbnailImg')[0].firstChild:
        print geoname.getElementsByTagName('thumbnailImg')[0].firstChild.data
        url_media = geoname.getElementsByTagName('thumbnailImg')[0].firstChild.data
    #thumbnailImg = geoname.getElementsByTagName('thumbnailImg')[0].firstChild.data
    rank = geoname.getElementsByTagName('rank')[0].firstChild.data
    data[cpt] = {'nom': nom, 'resume': resume, 'altitude' : altitude,'lat': lat, 'lng': lng, 'url': url_wikipedia, 'image' : url_media,
                        'rank': rank}
    cpt+=1

print data

#Pour écrire dans un fichier Shapefile
w = shapefile.Writer('C:\\Users\Eric\\PycharmProjects\\OronceFine\\scripts\out\\wiki\\geonames_wiki.shp')
w.field('name', 'C')
w.field('resume', 'C', size=255)
w.field('altitude', 'C')
w.field('url', 'C', size=255)
w.field('image', 'C', size=255)

for lieu in data:
    #print lieu['name'] + ' ' + str(lieu['lat']) + ' ' + str(lieu['long'])
    print data[lieu]['nom'] + ' ' + str(data[lieu]['lat']) + ' ' + str(data[lieu]['lng'])
    #w.point(data[lieu]['lng'], data[lieu]['lat'])
    w.point(float(data[lieu]['lng']), float(data[lieu]['lat']))
    w.record(data[lieu]['nom'], data[lieu]['resume'], data[lieu]['altitude'], data[lieu]['url'], data[lieu]['image'])

w.close()