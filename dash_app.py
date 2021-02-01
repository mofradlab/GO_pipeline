# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
import time
import plotly.express as px
from dash.dependencies import Input, Output
import pickle
import os
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
root_path = os.path.abspath(os.path.dirname(__file__))

def initialize_dash_app(name, server, analysis_content_dict, url_base_pathname="/results/"):
    dash_app = dash.Dash(name, server=server, routes_pathname_prefix=url_base_pathname, requests_pathname_prefix = "/results/", external_stylesheets=external_stylesheets)
    print("dash app config", dash_app.config)
    dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1(children='Dataset Results'),
    dcc.Dropdown(
        id="dropdown",
        options=[{"label": "biological_process", "value": "biological_process"}],
        value="biological_process",
        clearable=False,
    ),
    dcc.Graph(id="bar-chart"),
])

    @dash_app.callback(
        Output("bar-chart", "figure"), 
        [Input("dropdown", "value"), Input("url", "pathname")])
    def update_bar_chart(namespace, pathname):
        data_id = pathname.split("/")[-1]
        if(data_id in analysis_content_dict):
            analysis_data = analysis_content_dict[data_id]
            df = analysis_content_dict[data_id][namespace]
            fig = px.bar(df, x="GO_term", y="count", title="GO Term Occurrences")
            return fig
        else:
            return px.bar()
        
    
    @dash_app.callback(
        Output("dropdown", "options"), 
        [Input("url", "pathname")]
    )
    def update_dropdown(pathname):
        print("updating from pathname", pathname)
        data_id = pathname.split("/")[-1]
        analysis_data = {}
        if(data_id in analysis_content_dict):
            analysis_data = analysis_content_dict[data_id]
        else:
            dash_cache_path = "{}/../../data/dash_cache/".format(root_path)
            cache_files = os.listdir(dash_cache_path)
            print("dash cache contents", cache_files)
            for f_name in cache_files:
                if(data_id in f_name):
                    with open(os.path.join(dash_cache_path, f_name), "rb") as f:
                        analysis_data = pickle.load(f)
                    analysis_content_dict[data_id] = analysis_data
                    break
        
        return [{'label': namespace, 'value': namespace} for namespace in analysis_data.keys()]
        
    return dash_app