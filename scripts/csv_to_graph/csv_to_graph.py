# -*- coding: utf-8 -*-

# Load the Pandas libraries with alias 'pd'
import pandas as pd
from operator import itemgetter, attrgetter
import json
import io

import networkx as nx

G = nx.Graph()

#Nodes groups

dict_groups = {

"conservation des distances" : "7",
"distorsion" : "7",
"orientation relative" : "7",
"présence de repères perceptifs" : "7",
"présence de repères physiques" : "7",
"carte pour autrui": "2",
"interprétation facile de la localisation": "2",
"interprétation facile de la symbolisation": "2",
"prise de notes personnelles": "2",
"information émotionnelle": "3",
"information perceptive": "3",
"symbolisation intuitive": "4",
"symbolisation personnelle": "4",
"utilisation des règles de sémiologie": "4",
"présence importante du texte pour représenter des objets physiques": "4",
"présence importante du texte pour représenter des informations perceptives": "4",
"organisation spatiale conceptuelle":  "5",
"organisation spatiale de proche en proche":   "5",
"organisation spatiale aérienne":  "5",
"j'aime": "6",
"je n'aime pas": "6",
}

# Read data from file 'filename.csv'
# (in the same directory that your python process is based)
# Control delimiters, rows, column names with read_csv (see later)
data = pd.read_csv("C:\\Users\\Eric\\Desktop\\temp\\cartes_sensibles\\Annotations_cartes_sensibles_2020_3.csv", sep=",")

row_count = len(data.index)
col_count = len(data.columns)
print "nb lignes : " + str(row_count) + " nb col : " + str(col_count)
print data.columns
#columns = len(next(data))

#nodes = data.columns[1:]

columns = data.columns[1:]

nodes_names = []
links = []
for d in data.columns[1:]:
        nodes_names.append(d)
        G.add_node(d)
        G.nodes[d]['name'] = d
        G.nodes[d]['group'] = 1

print nodes_names

for index, row in data.iterrows():
    # access data using column names
    print "ligne " + str(index)
    for col in columns:
        l_col = str(row[col]).split(";")
        print "(" + str(col) + ") : " + str(row[col])
        print "l_col : " + str(l_col)
        for val in l_col:
            if val is not 'nan' and val not in nodes_names:
                G.add_node(val)

                G.nodes[d]['name'] = val
                G.nodes[val]['group'] = 2

                if G.nodes[d]['name'] in dict_groups:
                    G.nodes[val]['group'] = dict_groups.get(val)
                else:
                    G.nodes[val]['group'] = 20

                #test if edge exist, then add +1 weight
                if val != 'nan' :
                    if G.has_edge(col, val):
                        print "get edge : " + col + " -> " + val + " and add +1 weigth"
                        G[col][val]['weight'] = G[col][val]['weight']+1
                    else:
                        print "add edge : " + col + " -> " + val
                        G.add_edge(col, val, weight=1.0)

cpt_nodes = 0
nodes = []
tab_nodes_neo = []
for i in G.nodes():
    G.nodes[i]['id'] = cpt_nodes
    print 'node ' + str(i)
    nodes.append({'id':  i, 'group': str(G.nodes[i]['group'])})
    cpt_nodes += 1

print nodes

links = [{'source': u[0], 'target': u[1], 'weight':G.edges[u]['weight']} for u in G.edges()]

print links

#Export as json graph
print 'export graph as json'
filename = 'C:\\Users\\Eric\\Desktop\\temp\\cartes_sensibles\graph_annotations_sensibles.json'
#with open(filename, 'w', encoding='utf8') as f:
with io.open(filename, 'wb') as f:
    json.dump({'nodes': nodes, 'links': links},
              f, indent=4, )
print 'ok'