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


class covid():
    dataframe = pd.DataFrame()
    df = pd.DataFrame()
    G = nx.Graph(name="pySNV")

    def __init__(self):
        pass

    def getdownload(self, url):
        # url = 'https://api.covid19india.org/raw_data.json'
        with request.urlopen(url) as response:
            source = response.read()
            data = json.loads(source)
        # Converting dict to dataframe
        dataframe = pd.DataFrame.from_dict(
            data['raw_data'], orient='columns')
        dataframe = dataframe.rename(
            columns={'contractedfromwhichpatientsuspected': 'contractedFrom'})
        # dataframe = dataframe.iloc[:1000]
        self.dataframe = dataframe
        return dataframe.iloc[:5]

    def save_df(self, loc, i):
        if i == 0:
            self.dataframe.to_csv(loc)
        elif i == 1:
            nx.write_gexf(self.G, loc)

    def switch(self, val):
        switcher = {
            "P2P": 'from',
            "STATE": 'state',
            "DISTRICT": 'district',
            "CITY": 'city'
        }
        return switcher.get(val, 'from')

    def gen_graph(self, graph_type):
        df = self.dataframe[['currentstatus', 'dateannounced',
                             'contractedFrom', 'agebracket', 'detectedcity', 'detecteddistrict', 'detectedstate', 'gender', 'patientnumber', 'statuschangedate']].copy()
        df.columns = ['status', 'start', 'from', 'age',
                      'city', 'district', 'state', 'gender', 'id', 'end']
        df.index = df['id']
        df['start'] = pd.to_datetime(df['start'])
        df['end'] = pd.to_datetime(df['end'])
        df['from'] = df['from'].apply(lambda x: re.sub('P', '', str(x)))
        df['from'] = df['from'].apply(
            lambda x: x.split(",")[0] if ", " in x else x)
        df = df[['id', 'from',  'start', 'end', 'status',
                 'gender', 'age', 'city', 'district', 'state']]
        df['from'] = df['from'].apply(
            lambda x: abs(int(x)) if x.isnumeric() else '')

        color = df['status'].unique()
        colord = {}
        colord[color[0]] = 'green'
        colord[color[1]] = 'orange'
        colord[color[2]] = 'red'
        colord[color[3]] = 'blue'

        edgelist = []
        for index, row in df.iterrows():
            s = row['start']
            e = row['end']
            t = row['id']
            f = row[self.switch(graph_type)]
            if f:
                edgelist.append([t, f, s, e])

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
            self.G.add_node(row['id'], start=s, end=e,
                            color=colord.get(row['status'], 'orange'))

        data = pd.DataFrame(edgelist, columns=['u1', 'u2', 's', 'e'])
        for index, row in data.iterrows():
            self.G.add_edge(row['u2'], row['u1'])
        return 0

    def get_info(self):
        return nx.info(self.G)
