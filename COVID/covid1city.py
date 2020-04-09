# %%
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timezone
import urllib.request as request
import networkx as nx
import json
import re

# %%
url = 'https://api.rootnet.in/covid19-in/unofficial/covid19india.org'

# %%
# Downloading json
# df=pd.read_json(url, orient='columns')
with request.urlopen(url) as response:
    source = response.read()
    data = json.loads(source)

# %%
# Converting dict to dataframe
dataframe = pd.DataFrame.from_dict(
    data['data']['rawPatientData'], orient='columns')

# %%
# Formatting dataframe to required format:
#       index to from date status age
df = dataframe[['status', 'reportedOn',
                'city', 'ageEstimate']].copy()
df.columns = ['status', 'date', 'city', 'age']
df['date'] = pd.to_datetime(df['date'])
df.index = range(1, len(df)+1)
df['to'] = df.index
df = df[['to', 'city', 'date', 'status', 'age']]
df = df.iloc[:1619]

# %%
color = df['status'].unique()
colord = {}
colord[color[0]] = 'green'
colord[color[1]] = 'orange'
colord[color[2]] = 'red'
colord[color[3]] = 'blue'

# %%
edgelistcity = []
for index, row in df.iterrows():
    t = row['to']
    d = row['city']
    if d == '           ':
        continue
    if not pd.isna(d):
        print(d+" "+str(t))
        edgelistcity.append([t, d, row['date']])

# %%
G = nx.DiGraph()
citylist = df['city'].unique()
citylist = citylist[citylist != '           ']
citylist = citylist[citylist != 'nan']
G.add_nodes_from(citylist, color='black')
for index, row in df.iterrows():
    t = row['date'].timestamp()
    G.add_node(row['to'], start=t,
               color=colord.get(row['status'], 'orange'))
data = pd.DataFrame(edgelistcity, columns=['u1', 'u2', 't'])
for index, row in data.iterrows():
    G.add_edge(row['u2'], row['u1'])
nx.write_gexf(G, "output/1_4city.gexf")
