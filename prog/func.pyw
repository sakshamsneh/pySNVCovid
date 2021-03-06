import colorsys
import datetime as dt
import json
import re
import urllib.request as request

import networkx as nx
import pandas as pd


class Covid():
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
        dataframe = dataframe.reindex(columns=list(dataframe.columns))
        df = dataframe[list(dataframe.columns)].copy()
        df.index = df['patientnumber']
        df['dateannounced'] = df['dateannounced'].apply(lambda x: dt.datetime.today().strftime("%d/%m/%Y") if pd.isnull(pd.to_datetime(x)) else x)
        df['dateannounced'] = pd.to_datetime(df['dateannounced'], format="%d/%m/%Y")
        df['dateannounced'] = df['dateannounced'].apply(lambda x: x.strftime("%Y-%m-%d"))

        df['statuschangedate'] = pd.to_datetime(df['statuschangedate'], format="%d/%m/%Y", errors='coerce')
        df['statuschangedate'] = df['statuschangedate'].apply(lambda x: x.strftime("%Y-%m-%d") if not pd.isnull(x) else x)
        df.loc[(df.dateannounced > df.statuschangedate),'statuschangedate'] = pd.NaT

        df['contractedfromwhichpatientsuspected'] = df['contractedfromwhichpatientsuspected'].apply(lambda x: re.sub('P', '', str(x)))
        df['contractedfromwhichpatientsuspected'] = df['contractedfromwhichpatientsuspected'].apply(lambda x: x.split(",")[0] if ", " in x else x)
        df['contractedfromwhichpatientsuspected'] = df['contractedfromwhichpatientsuspected'].apply(lambda x: abs(int(x)) if x.isnumeric() else '')
        self.df = df

    def get_color_field(self):
        # Generates color field list from dataframe columns, sans non colorable columns
        color_field = []
        color_field.append("SELECT")
        if not self.df.empty:
            color_field = list(self.df.columns)
            color_field.remove('patientnumber')
            color_field.remove('contractedfromwhichpatientsuspected')
            color_field.remove('dateannounced')
            color_field.remove('statuschangedate')
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

    def hex2rgb(self, colord):
        for k, v in colord.items():
            c = {}
            v = v.lstrip('#')
            lenv = len(v)
            v = list(int(v[i:i+2], 16) for i in (0, 2, 4))
            c['r'] = v[0]
            c['g'] = v[1]
            c['b'] = v[2]
            c['a'] = 1
            colord[k] = c
        return colord

    def gen_graph(self, graph_type, color_select, start_date, end_date, *arg):
        # Generates nx graph from dataframe, color values generated from set_color method
        # Each id values are nodes, edges are formed from graph_type column value
        # Subsitute empty date values with end date
        df = self.df
        starts = start_date.strftime("%Y-%m-%d")
        ends = end_date.strftime("%Y-%m-%d")
        mask = (df['dateannounced'] > starts) & (df['dateannounced'] <= ends)
        df = df.loc[mask]
        if arg[0] is not '0':
            colord = eval(arg[0])
        else:
            colord = self.set_color(df[color_select].unique())
        colord = self.hex2rgb(colord)

        edgelist = []
        for index, row in df.iterrows():
            f = row[graph_type]
            if f:
                t = row['patientnumber']
                edgelist.append([t, f])

        for index, row in df.iterrows():
            s = row['dateannounced']
            e = row['statuschangedate']
            if pd.isnull(e):
                e = end_date
            else:
                e = row['statuschangedate']
            viz = {'color': colord.get(row[color_select], 'black')}
            self.G.add_node(row['patientnumber'], start=s, end=e, viz=viz)

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
            return self.get_graph_field()
        elif chk == 1:
            G = nx.read_gexf(filename)
            return nx.info(G)

    def get_df(self, graph_fields, selection):
        # Creates static graph from gtype and args
        # Selects dataframe using passed mask
        # Returns values to generate and show graph
        df = self.df
        masklist = []
        if selection:
            for k, v in selection.items():
                masklist.append(df[k].isin(v))
            s = masklist[0]
            for m in masklist[1:]:
                s &= m
            df = df[s][graph_fields].copy()
        else:
            df = df[graph_fields].copy()
        return df

    def get_daterange(self):
        # Returns daterange of data
        s = self.df.iloc[0]['dateannounced']
        s = dt.datetime.strptime(s, "%Y-%m-%d")
        e = self.df.iloc[-1]['dateannounced']
        e = dt.datetime.strptime(e, "%Y-%m-%d")
        return s, e

    def get_unique_val(self, col):
        # Returns list of unique values in param col
        return list(self.df[col].dropna().unique())
