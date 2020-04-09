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
dataframe['relationship'] = dataframe['relationship'].apply(
	lambda x: json.loads(x.replace("'", '"'))[0]['link'] if x != '[]' else x)

# %%
# Formatting dataframe to required format:
#       index to from date status age
df = dataframe[['status', 'reportedOn',
				'contractedFrom', 'ageEstimate']].copy()
df.columns = ['status', 'date', 'from', 'age']
df['date'] = pd.to_datetime(df['date'])
df['from'] = df['from'].apply(lambda x: re.sub('P', '', str(x)))
df['from'] = df['from'].apply(lambda x: x.split(",")[0] if ", " in x else x)

# %%
df['from'] = df['from'].apply(lambda x: abs(int(x)) if x.isnumeric() else '')
df.index = range(1, len(df)+1)
df['to'] = df.index
df = df[['to', 'from', 'date', 'status', 'age']]
df = df.iloc[:1619]

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
	t = row['to']
	f = row['from']
	if f:
		edgelistp2p.append([t, f, row['date']])

# %%
G = nx.Graph()
# G.add_nodes_from(df['to'], t=df['date'].isoformat())
for index, row in df.iterrows():
	t = row['date'].timestamp()
	G.add_node(row['to'], start=t,
			   color=colord.get(row['status'], 'orange'))
data = pd.DataFrame(edgelistp2p, columns=['u1', 'u2', 't'])
for index, row in data.iterrows():
	G.add_edge(row['u2'], row['u1'])
nx.write_gexf(G, "output/1_4p2p.gexf")

# %%
# Community List
# from networkx.algorithms import community
# communities = community.greedy_modularity_communities(G)
# for i,c in enumerate(communities): # Loop through the list of communities
#     if len(c) > 2: # Filter out modularity classes with 2 or fewer nodes
#         print('Class '+str(i)+':', list(c)) # Print out the classes and their members
