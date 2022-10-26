import csv
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from tqdm import tqdm

class Graph():
    """Creates data visualizations."""

    def __init__(self, users, fields, rows, csvfile, app):
        self._users = users
        self._fields = fields
        self._rows = rows
        self._csvfile = csvfile
        self._app = app
        self._df = None
        self._figlst = []
        self._children = []


    def create_csv(self):
        with open(self._csvfile, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = self._fields) 
            writer.writeheader() 
            writer.writerows(self._rows)

    def get_df(self):
        self._df = pd.read_csv(self._csvfile)

    def create_json(self):
        pass

    def get_default_figures(self):
        for field in tqdm(self._fields[1:], desc='Getting figs'):
            self._figlst.append(px.bar(self._df, x='user', y=f'{field}'))

    def get_graphs(self):
            self._children.append(html.Div(dcc.Graph(id='graph1', figure= px.bar(self._df, x='user', y=f'{self._fields[1]}', title ="Number of logs per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph2', figure= px.bar(self._df, x='user', y=f'{self._fields[2]}', title ="Browsing time per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph3', figure= px.bar(self._df, x='user', y=f'{self._fields[3]}', title ="Number of sessions per user\n(where one session == a group of logs with the same URL and TabID)."))))
            self._children.append(html.Div(dcc.Graph(id='graph4', figure= px.bar(self._df, x='user', y=f'{self._fields[4]}', title ="Average session time per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph5', figure= px.bar(self._df, x='user', y=f'{self._fields[5]}', title ="Average download time per session."))))
            self._children.append(html.Div(dcc.Graph(id='graph6', figure= px.bar(self._df, x='user', y=f'{self._fields[6]}', title ="Number of downloads per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph7', figure= px.pie(self._df, names='user', values=f'{self._fields[7]}', title ="Percent of user logs that consist of a download."))))
            self._children.append(html.Div(dcc.Graph(id='graph8', figure= px.bar(self._df, x='user', y=f'{self._fields[8]}', title ="URLs per download."))))
            self._children.append(html.Div(dcc.Graph(id='graph9', figure= px.bar(self._df, x='user', y=f'{self._fields[9]}', title ="Number of URLs visited per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph10', figure= px.bar(self._df, x='user', y=f'{self._fields[10]}', title ="URLs visited per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph11', figure= px.bar(self._df, x='user', y=f'{self._fields[11]}', title ="Average download time per URL."))))
            self._children.append(html.Div(dcc.Graph(id='graph12', figure= px.bar(self._df, x='user', y=f'{self._fields[12]}', title ="Number of overlaps per user."))))
            self._children.append(html.Div(dcc.Graph(id='graph13', figure= px.pie(self._df, names='user', values=f'{self._fields[13]}', title ="Percent of user logs that involve an overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph14', figure= px.bar(self._df, x='user', y=f'{self._fields[14]}', title ="Overlap duration per overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph15', figure= px.bar(self._df, x='user', y=f'{self._fields[15]}', title ="Average overlap duration."))))
            self._children.append(html.Div(dcc.Graph(id='graph16', figure= px.bar(self._df, x='user', y=f'{self._fields[16]}', title ="URLs involved per overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph17', figure= px.bar(self._df, x='user', y=f'{self._fields[17]}', title ="URLs per all of users' overlaps."))))
            # num_urls_per_overlap
            self._children.append(html.Div(dcc.Graph(id='graph18', figure= px.bar(self._df, x='user', y=f'{self._fields[18]}', title ="Number of URLs per overlap."))))
            # avg_num_urls_per_overlaps
            self._children.append(html.Div(dcc.Graph(id='graph19', figure= px.bar(self._df, x='user', y=f'{self._fields[19]}', title ="Average number of URLs per overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph20', figure= px.bar(self._df, x='user', y=f'{self._fields[20]}', title ="URL that begins the overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph21', figure= px.bar(self._df, x='user', y=f'{self._fields[21]}', title ="Most common URL that begins the overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph22', figure= px.bar(self._df, x='user', y=f'{self._fields[22]}', title ="Time before overlap starts per overlap."))))
            self._children.append(html.Div(dcc.Graph(id='graph23', figure= px.bar(self._df, x='user', y=f'{self._fields[23]}', title ="Average time before overlap starts."))))
            self._children.append(html.Div(dcc.Graph(id='graph24', figure= px.bar(self._df, x='user', y=f'{self._fields[24]}', title ="Overlaps in visualized form."))))
            # visualized_overlaps
            self._children.append(html.Div(dcc.Graph(id='graph25', figure=self._figlst[24]))) 

    def init_app(self):
        self._app.layout = html.Div(self._children)
    