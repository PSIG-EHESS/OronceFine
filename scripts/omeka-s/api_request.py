#!/usr/bin/env python
# coding: utf8

import json
import requests
import httplib2

_http = httplib2.Http()

# URL Omeka-s API
base_url = "http://psig.huma-num.fr/omeka-s/api/items?per_page=100&page="
base_url_ok = "http://psig.huma-num.fr/omeka-s/api/items"

nb_pages = 1
nb_item_per_page = 100

for page in range(nb_pages):

    iter_page = page + 1

    iter_base_url = base_url + str(iter_page)

    print '____ querying ' + iter_base_url

    # Assemble the URL and query the web service
    #r = requests.get(base_url)#, params=payload)
    # prepared = r.prepare()
    # print prepared

    resp, content = _http.request(iter_base_url, "GET")#, body=data, headers=headers)

    print '--resp--'
    print resp
    print '--content--'
    #print content

    x = json.loads(content)

    #print x

    # # Check the HTTP status code returned by the server. Only process the response,
    # # if the status code is 200 (OK in HTTP terms).
    # if r.status_code != 200:
    #     print('HTTP status code {} received, program terminated.'.format(r.status_code))
    # else:
    #     x = json.loads(r.text)
    #     print r.text

    for item in range(3, nb_item_per_page):
        #print x[item]
        print 'vertex : ' + str(x[item]['o:id'])
        print 'dcterms:title : ' + str(x[item]['dcterms:title'][0]["@value"])
        print 'annotation : ' + str(x[item]['o-module-annotate:annotation'])
