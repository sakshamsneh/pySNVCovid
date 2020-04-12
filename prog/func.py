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
import colorsys


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
            self.gen_df(self.dataframe)
        elif i == 1:
            nx.write_gexf(self.G, loc)

    def gen_df(self, dataframe):
        df = dataframe[['currentstatus', 'dateannounced',
                        'contractedFrom', 'agebracket', 'detectedcity', 'detecteddistrict', 'detectedstate', 'gender', 'patientnumber', 'statuschangedate']].copy()
        df.columns = ['status', 'start', 'from', 'age',
                      'city', 'district', 'state', 'gender', 'id', 'end']
        df.index = df['id']
        df['start'] = df['start'].apply(lambda x: dt.datetime.today().strftime("%d/%m/%Y") if pd.isnull(pd.to_datetime(x)) else x)
        df['start'] = pd.to_datetime(df['start'], format="%d/%m/%Y")
        df['start'] = df['start'].apply(lambda x: x.strftime("%Y-%m-%d"))

        df['end'] = pd.to_datetime(
            df['end'], format="%d/%m/%Y", errors='coerce')
        df['end'] = df['end'].apply(lambda x: x.strftime(
            "%Y-%m-%d") if not pd.isnull(x) else x)
        for i, r in df.iterrows():
            if r['start']>r['end']:
                r['end']=pd.NaT

        df['from'] = df['from'].apply(lambda x: re.sub('P', '', str(x)))
        df['from'] = df['from'].apply(
            lambda x: x.split(",")[0] if ", " in x else x)
        df = df[['id', 'from',  'start', 'end', 'status',
                 'gender', 'age', 'city', 'district', 'state']]
        df['from'] = df['from'].apply(
            lambda x: abs(int(x)) if x.isnumeric() else '')
        self.df = df

    def get_color_field(self):
        color_field = []
        color_field.append("SELECT")
        if not self.df.empty:
            color_field = list(self.df.columns)
            color_field.remove('id')
            color_field.remove('from')
            color_field.remove('start')
            color_field.remove('end')
        return color_field

    def get_graph_field(self):
        graph_field = []
        graph_field.append("SELECT")
        if not self.df.empty:
            graph_field = list(self.df.columns)
        return graph_field

    def set_color(self, col_list):
        colord = {}
        N = len(col_list)
        HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        rgb = []
        for val in RGB_tuples:
            v = [255*x for x in val]
            vals = '#' + ''.join(['{:02X}'.format(int(round(x))) for x in v])
            rgb.append(vals)
        for i in range(N):
            colord[col_list[i]] = rgb[i]
        return colord

    def gen_graph(self, graph_type, color_select):
        df = self.df
        color = df[color_select].unique()
        colord = self.set_color(color)

        edgelist = []
        for index, row in df.iterrows():
            s = row['start']
            e = row['end']
            t = row['id']
            f = row[graph_type]
            if f:
                edgelist.append([t, f, s, e])

        for index, row in df.iterrows():
            s = row['start']
            if pd.isnull(s):
                e = dt.datetime.today().strftime("%Y-%m-%d")
            else:
                s = row['start']
            e = row['end']
            if pd.isnull(e):
                e = dt.datetime.today().strftime("%Y-%m-%d")
            else:
                e = row['end']
            self.G.add_node(row['id'], start=s, end=e,
                            color=colord.get(row[color_select], 'black'))

        data = pd.DataFrame(edgelist, columns=['u1', 'u2', 's', 'e'])
        for index, row in data.iterrows():
            self.G.add_edge(row['u2'], row['u1'])
        return colord

    def get_info(self):
        return nx.info(self.G)

    def open_file(self, filename, chk):
        if chk == 0:
            dataframe = pd.read_csv(filename, index_col=0)
            self.gen_df(dataframe)
        elif chk == 1:
            G = nx.read_gexf(filename)
            return nx.info(G)
