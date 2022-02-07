# Load the Pandas libraries with alias 'pd'
import pandas as pd
from operator import itemgetter, attrgetter
import json

data_json = {}
data_json['nodes'] = []
data_json['links'] = []

data_simple_json = {}
data_simple_json['nodes'] = []
data_simple_json['links'] = []

# Read data from file 'filename.csv'
# (in the same directory that your python process is based)
# Control delimiters, rows, column names with read_csv (see later)
data = pd.read_csv("C:\\Users\\Eric\\PycharmProjects\\OronceFine\\scripts\\csv_to_json\\distance_stats_export_utf8.csv", sep=";")
# Preview the first 5 lines of the loaded data
#print data.head()

list_source_date = list()
list_target_date = list()

list_links_value = list()

for index, row in data.iterrows():
    # access data using column names
    source_date = [row['DATE'], row['SOURCE']]
    target_date = [row['DATE_1'], row['TARGET']]

    list_source_date.append(source_date)
    list_target_date.append(target_date)

#avoid duplicates

list_totale = list_source_date + list_target_date

list_source_date = list(set(tuple(a) for a in list_source_date))
list_target_date = list(set(tuple(a) for a in list_target_date))
list_totale = list(set(tuple(a) for a in list_totale))

#sort list
list_source_date_sorted_date_village = sorted(list_source_date, key=itemgetter(0,1))
list_target_date_sorted_date_village = sorted(list_target_date, key=itemgetter(0,1))
list_totale_sorted = sorted(list_totale, key=itemgetter(0,1))

print(list_source_date_sorted_date_village)
print(list_target_date_sorted_date_village)
print(list_totale_sorted)

for j in range(0, len(list_totale_sorted)):
     data_json['nodes'].append({
         'node': j,
         'year': list_totale_sorted[j][0],
         'name': list_totale_sorted[j][1]
     })
     print j

#nodes are the same
data_simple_json['nodes'] = data_json['nodes']


#LINKS
n = len(list_totale_sorted)
tab_links_value = [[0] * n for i in range(n)]

for index, row in data.iterrows():
    # access data using column names

    id_source = list_totale_sorted.index((row['DATE'], row['SOURCE']))
    id_target = list_totale_sorted.index((row['DATE_1'], row['TARGET']))

    tab_links_value[id_source][id_target] = tab_links_value[id_source][id_target] + 1

    #person
    data_json['links'].append({
        'id': row['Id'],
        'name': row['Name'],
        'source': id_source,
        'target': id_target,
        'value': 1
    })

for i in range(n):
    for j in range(n):

        value = tab_links_value[i][j]

        if value > 0:

            #agregation
            data_simple_json['links'].append({
                'source': i,
                'target': j,
                'value': tab_links_value[i][j] * 10
            })

with open('data_for_sankey.json', 'w') as outfile:
    json.dump(data_json, outfile)

with open('data_simple_for_sankey.json', 'w') as outfile:
    json.dump(data_simple_json, outfile)
