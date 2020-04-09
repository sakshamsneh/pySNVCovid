# %%
from networkx.algorithms import community
from operator import itemgetter
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timezone
import urllib.request as request
import networkx as nx
import json
import re

# %%
url = 'https://api.covid19india.org/raw_data.json'

# %%
with request.urlopen(url) as response:
    source = response.read()
    data = json.loads(source)

# %%
# Converting dict to dataframe
dataframe = pd.DataFrame.from_dict(
    data['raw_data'], orient='columns')
dataframe = dataframe.rename(
    columns={'contractedfromwhichpatientsuspected': 'contractedFrom'})

# %%
df = dataframe[['currentstatus', 'dateannounced',
                'contractedFrom', 'agebracket', 'detectedcity', 'detecteddistrict', 'detectedstate', 'gender', 'patientnumber', 'statuschangedate']].copy()
df.columns = ['status', 'start', 'from', 'age',
              'city', 'district', 'state', 'gender', 'id', 'end']
df.index = df['id']
df['start'] = pd.to_datetime(df['start'])
df['end'] = pd.to_datetime(df['end'])
df['from'] = df['from'].apply(lambda x: re.sub('P', '', str(x)))
df['from'] = df['from'].apply(lambda x: x.split(",")[0] if ", " in x else x)
df = df[['id', 'from',  'start', 'end', 'status',
         'gender', 'age', 'city', 'district', 'state']]
df['from'] = df['from'].apply(lambda x: abs(int(x)) if x.isnumeric() else '')

# %%
color = df['status'].unique()
colord = {}
colord[color[0]] = 'green'
colord[color[1]] = 'orange'
colord[color[2]] = 'red'
colord[color[3]] = 'blue'

# %%
edgelistp2p = []
for index, row in df.iterrows():
    t = row['id']
    f = row['from']
    s = row['start']
    e = row['end']
    if f:
        edgelistp2p.append([t, f, s, e])

# %%
G = nx.Graph()
for index, row in df.iterrows():
    s = row['start']
    if pd.isnull(s):
        e = dt.datetime.now().timestamp()
    else:
        s = row['start'].timestamp()
    e = row['end']
    if pd.isnull(e):
        e = dt.datetime.now().timestamp()
    else:
        e = row['end'].timestamp()
    G.add_node(row['id'], start=s, end=e,
               color=colord.get(row['status'], 'orange'))

data = pd.DataFrame(edgelistp2p, columns=['u1', 'u2', 's', 'e'])
for index, row in data.iterrows():
    G.add_edge(row['u2'], row['u1'])
nx.write_gexf(G, "../output/7_4p2p.gexf")
# Main program ends

# %%
age = {}
city = {}
district = {}
state = {}
gender = {}
for i, r in df.iterrows():
    age[r['id']] = r['age']
    city[r['id']] = r['city']
    district[r['id']] = r['district']
    state[r['id']] = r['state']
    gender[r['id']] = r['gender']
degree_dict = dict(G.degree(G.nodes()))

nx.set_node_attributes(G, age, 'age')
nx.set_node_attributes(G, city, 'city')
nx.set_node_attributes(G, district, 'district')
nx.set_node_attributes(G, state, 'state')
nx.set_node_attributes(G, gender, 'gender')
nx.set_node_attributes(G, degree_dict, 'degree')

# sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)
# for d in sorted_degree[:20]:
#     print(d)

# communities = community.greedy_modularity_communities(G)
# for i, c in enumerate(communities):  # Loop through the list of communities
#     if len(c) > 2:  # Filter out modularity classes with 2 or fewer nodes
#         # Print out the classes and their members
#         print('Class '+str(i)+':', list(c))

# %%
# Reverse dict
age_r = {}
city_r = {}
district_r = {}
state_r = {}
gender_r = {}

for key, value in sorted(age.items()):
    age_r.setdefault(value, []).append(key)
for key, value in sorted(city.items()):
    city_r.setdefault(value, []).append(key)
for key, value in sorted(district.items()):
    district_r.setdefault(value, []).append(key)
for key, value in sorted(state.items()):
    state_r.setdefault(value, []).append(key)
for key, value in sorted(gender.items()):
    gender_r.setdefault(value, []).append(key)
