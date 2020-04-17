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
    """
    Code class provides code for dataframe and nx graph generation.
    This class downloads dataframe and works on them.
    """

    # Two blank dataframes, single nx graph
    def __init__(self):
        self.dataframe = pd.DataFrame()
        self.df = pd.DataFrame()
        self.G = nx.Graph(name="pySNV")

    def getdownload(self, url):
        # Downloads json from url argument, converts into dataframe
        # Returns first 100 rows of the dataframe.
        # Example url = 'https://api.covid19india.org/raw_data.json'
        with request.urlopen(url) as response:
            source = response.read()
            data = json.loads(source)
        # Converting dict to dataframe
        dataframe = pd.DataFrame.from_dict(
            data['raw_data'], orient='columns')
        dataframe = dataframe.rename(
            columns={'contractedfromwhichpatientsuspected': 'contractedFrom'})
        self.dataframe = dataframe
        return dataframe.iloc[:100]

    def save_df(self, loc, i):
        # Saves files using file location argument loc
        # if arg i==0 saves dataframe
        # else saves nx.gexf
        if i == 0:
            self.dataframe.to_csv(loc)
            self.gen_df(self.dataframe)
        elif i == 1:
            nx.write_gexf(self.G, loc)

    def gen_df(self, dataframe):
        # Generates compact dataframe from original dataframe
        # Parses date columns to YYYY-mm-dd format
        dataframe = dataframe.reindex(columns=['agebracket', 'backupnotes', 'contractedFrom', 'currentstatus', 'dateannounced', 'detectedcity', 'detecteddistrict', 'detectedstate',
                                               'estimatedonsetdate', 'gender', 'nationality', 'notes', 'patientnumber', 'source1', 'source2', 'source3', 'statecode', 'statepatientnumber', 'statuschangedate', 'typeoftransmission'])
        df = dataframe[['currentstatus', 'dateannounced', 'contractedFrom', 'agebracket', 'detectedcity',
                        'detecteddistrict', 'detectedstate', 'gender', 'patientnumber', 'statuschangedate']].copy()
        df.columns = ['status', 'start', 'from', 'age',
                      'city', 'district', 'state', 'gender', 'id', 'end']
        df.index = df['id']
        df['start'] = df['start'].apply(lambda x: dt.datetime.today().strftime(
            "%d/%m/%Y") if pd.isnull(pd.to_datetime(x)) else x)
        df['start'] = pd.to_datetime(df['start'], format="%d/%m/%Y")
        df['start'] = df['start'].apply(lambda x: x.strftime("%Y-%m-%d"))

        df['end'] = pd.to_datetime(
            df['end'], format="%d/%m/%Y", errors='coerce')
        df['end'] = df['end'].apply(lambda x: x.strftime(
            "%Y-%m-%d") if not pd.isnull(x) else x)
        for i, r in df.iterrows():
            if r['start'] > r['end']:
                r['end'] = pd.NaT

        df['from'] = df['from'].apply(lambda x: re.sub('P', '', str(x)))
        df['from'] = df['from'].apply(
            lambda x: x.split(",")[0] if ", " in x else x)
        df = df[['id', 'from',  'start', 'end', 'status',
                 'gender', 'age', 'city', 'district', 'state']]
        df['from'] = df['from'].apply(
            lambda x: abs(int(x)) if x.isnumeric() else '')
        self.df = df

    def get_color_field(self):
        # Generates color field list from dataframe columns, sans non colorable columns
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
        # Generates graph field list from dataframe columns
        graph_field = []
        graph_field.append("SELECT")
        if not self.df.empty:
            graph_field = list(self.df.columns)
        return graph_field

    def set_color(self, col_list):
        # Generates color dict for all unique values in argument column
        # Creates HSV value list for unique values, converts in RGB value list
        # Assigns each RGB value to each unique column value
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
        # Generates nx graph from dataframe, color values generated from set_color method
        # Each id values are nodes, edges are formed from graph_type column value
        # Subsitute empty date values with current date
        df = self.df
        color = df[color_select].unique()
        colord = self.set_color(color)

        edgelist = []
        for index, row in df.iterrows():
            f = row[graph_type]
            if f:
                t = row['id']
                edgelist.append([t, f])

        for index, row in df.iterrows():
            s = row['start']
            e = row['end']
            if pd.isnull(e):
                e = dt.datetime.today().strftime("%Y-%m-%d")
            else:
                e = row['end']
            self.G.add_node(row['id'], start=s, end=e,
                            color=colord.get(row[color_select], 'black'))

        data = pd.DataFrame(edgelist, columns=['u1', 'u2'])
        for index, row in data.iterrows():
            self.G.add_edge(row['u2'], row['u1'])
        return colord

    def get_info(self):
        # Returns nx information of graph G
        return nx.info(self.G)

    def open_file(self, filename, chk):
        # Opens file using file location argument filename
        # if arg chk==0 opens dataframe
        # else reads nx.gexf
        if chk == 0:
            dataframe = pd.read_csv(filename, index_col=0, encoding="cp1252")
            self.gen_df(dataframe)
        elif chk == 1:
            G = nx.read_gexf(filename)
            return nx.info(G)
