import csv
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from tqdm import tqdm

class Graph():
    """Creates data visualizations."""

    def __init__(self, objs, fields, rows, csvfile, app):
        self._objs = objs
        self._fields = fields
        self._rows = rows
        self._csvfile = csvfile
        self._app = app
        self._df = None
        self._figlst = []
        self._children = []


    def create_format1_csv(self):
        with open(self._csvfile, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = self._fields)
            writer.writeheader() 
            writer.writerows(self._rows)

    def create_format2_csv(self):
        with open(self._csvfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self._fields)
            for k,v in self._rows.items():
                writer.writerow([k, *v])

    def create_format3_csv(self):
        with open(self._csvfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self._fields)
            writer.writerow(self._rows)

    def get_df(self):
        self._df = pd.read_csv(self._csvfile)

    def create_json(self):
        pass


    def get_user_graphs(self):
        self._children.append(html.Div(dcc.Graph(id='graph1', figure= px.bar(self._df, x='user', y=f'{self._fields[1]}', title ="Number of logs per user."))))
        self._children.append(html.Div(dcc.Graph(id='graph2', figure= px.bar(self._df, x='user', y=f'{self._fields[2]}', title ="Browsing time per user (hours)."))))
        self._children.append(html.Div(dcc.Graph(id='graph3', figure= px.bar(self._df, x='user', y=f'{self._fields[3]}', title ="Number of sessions per user\n(where one session == a group of logs with the same URL and TabID)."))))
        self._children.append(html.Div(dcc.Graph(id='graph4', figure= px.bar(self._df, x='user', y=f'{self._fields[4]}', title ="Average session time per user (hours)."))))
        self._children.append(html.Div(dcc.Graph(id='graph6', figure= px.bar(self._df, x='user', y=f'{self._fields[5]}', title ="Number of downloads per user."))))
        self._children.append(html.Div(dcc.Graph(id='graph7', figure= px.pie(self._df, names='user', values=f'{self._fields[6]}', title ="Percent of user logs that consist of a download."))))
        self._children.append(html.Div(dcc.Graph(id='graph8', figure= px.bar(self._df, x='user', y=f'{self._fields[7]}', title ="Number of URLs visited per user."))))
        self._children.append(html.Div(dcc.Graph(id='graph9', figure= px.bar(self._df, x='user', y=f'{self._fields[8]}', title ="Number of overlaps per user."))))
        self._children.append(html.Div(dcc.Graph(id='graph10', figure= px.pie(self._df, names='user', values=f'{self._fields[9]}', title ="Percent of user logs that involve an overlap."))))
        self._children.append(html.Div(dcc.Graph(id='graph11', figure= px.bar(self._df, x='user', y=f'{self._fields[10]}', title ="Average overlap duration per user (seconds)."))))
        self._children.append(html.Div(dcc.Graph(id='graph12', figure= px.bar(self._df, x='user', y=f'{self._fields[11]}', title ="Average time between overlaps per user."))))
        self._children.append(html.Div(dcc.Graph(id='graph13', figure= px.bar(self._df, x='user', y=f'{self._fields[12]}', title ="Average number of URLs per overlap per user."))))
            
    def get_url_graphs(self):
        self._children.append(html.Div(dcc.Graph(id='graph1', figure= px.bar(self._df, x='url', y=f'num_times_dloaded', title ="Number successful downloads per URL."))))
        self._children.append(html.Div(dcc.Graph(id='graph2', figure= px.bar(self._df, x='url', y=f'avg_dload_time (secs)', title ="Average download time per URL (seconds)."))))
        self._children.append(html.Div(dcc.Graph(id='graph3', figure= px.bar(self._df, x='url', y=f'involved_in_an_overlap', title ="URL is involved in an overlap."))))
        self._children.append(html.Div(dcc.Graph(id='graph4', figure= px.bar(self._df, x='url', y=f'begins_an_overlap', title ="URL begins an overlap."))))

    def get_overlap_graphs(self):
        self._children.append(html.Div(dcc.Graph(id='graph1', figure= px.bar(self._df, x='user_for_this_overlap', y=f'{self._fields[1]}', title ="Overlap duration."))))
        self._children.append(html.Div(dcc.Graph(id='graph2', figure= px.bar(self._df, x='user_for_this_overlap', y=f'{self._fields[2]}', title ="Time before overlap starts (seconds)."))))
        self._children.append(html.Div(dcc.Graph(id='graph3', figure= px.bar(self._df, x='user_for_this_overlap', y=f'{self._fields[3]}', title ="URL that begins the overlap"))))
        self._children.append(html.Div(dcc.Graph(id='graph4', figure= px.bar(self._df, x='user_for_this_overlap', y=f'{self._fields[4]}', title ="Number of URLs per overlap"))))

    def get_dload_graphs(self):
        self._children.append(html.Div(dcc.Graph(id='graph1', figure= px.bar(self._df, x='url', y=f'{self._fields[1]}', title ="User of the download."))))
        self._children.append(html.Div(dcc.Graph(id='graph2', figure= px.bar(self._df, x='url', y=f'{self._fields[2]}', title ="Download duration (secs)."))))

    def get_visualized_overlaps(self):
        #self._children.append(html.Div(dcc.Graph(id='graph22', figure= px.bar(self._df, x='user', y=f'{self._fields[21]}', title ="Overlaps in visualized form."))))
        pass

    def init_app(self):
        self._app.layout = html.Div(self._children)
    
