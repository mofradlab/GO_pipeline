# -*- coding: utf-8 -*-
from logging import PlaceHolder
import dash
import dash_html_components as html
import dash_core_components as dcc
from pipeline_app.app_gen import app, db, root_path, Submission, SubmissionMetrics, SubmissionDescription
import time
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pickle
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
root_path = os.path.abspath(os.path.dirname(__file__))


dataset_results_layout = html.Div([html.H1(children='Dataset Results'),
    dcc.Dropdown(
        id="dropdown",
        options=[{"label": "biological_process", "value": "biological_process"}],
        value="biological_process",
        clearable=False,
    ),
    dcc.Graph(id="bar-chart")
])

model_results_layout = html.Div([
    html.Div([
        dcc.Dropdown(
        id="model-namespace", placeholder="Namespace", 
        options=[{"label": "Biological Process", "value": "biological_process"},
            {"label": "Molecular Function", "value": "molecular_function"},
            {"label": "Cellular Component", "value": "cellular_component"}]
        ), 
        dcc.Dropdown(
        id="model-testing_set", placeholder="Testing Set", 
        options=[{"label": "Cluster 50", "value": "cluster50"},
            {"label": "Random", "value": "random"}]
        ), 
        dcc.Dropdown(
        id="model-testing_quality", placeholder="Testing Quality", 
        options=[{"label": "Experimental", "value": "exp"},
            {"label": "non-Electronic", "value": "non_IEA"}]
        )
    ]),
    dcc.Dropdown(
        id="model-metric", placeholder="Metric", 
        options=[{"label": "Max F1", "value": "max_f1"}, 
            {"label": "S-Min", "value": "s_min"},
            {"label": "Max Recall Metric", "value": "max_rm"}]
    ), 
    dcc.Dropdown(
        id="model-dropdown",
        options=[], 
        multi=True, 
        clearable=True
    ),
    dcc.Graph(id="model-chart")
])

def initialize_dash_app(name, server, analysis_content_dict, **kwargs):
    #assets_url_path="static"
    dash_app = dash.Dash(name, server=server, **kwargs)
    #print("dash app config", dash_app.config)
    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    @dash_app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
    def display_page(pathname):
        dash_info = pathname[pathname.find("results"):-1].split("/")
        print("dash_info", dash_info)
        if(len(dash_info) <= 1 or dash_info[1] == "models"):
            return model_results_layout
        else:
            return dataset_results_layout

    @dash_app.callback(
        Output("model-dropdown", "options"), 
        [Input("model-namespace", "value"), Input("model-testing_set", "value"), 
        Input("model-testing_quality", "value")]
    )
    def update_model_dropdown(namespace, testing_set, testing_quality):
        print("updating model dropdown with", namespace, testing_set, testing_quality)

        submissions = Submission.query.filter_by(namespace=namespace)\
        .filter_by(testing_set=testing_set).filter_by(testing_quality=testing_quality)\
        .order_by(Submission.max_f1.desc()).all()
        return [{'label': "{}".format(submission.model), 'value': submission.id} for submission in submissions]

    @dash_app.callback(
    Output("model-chart", "figure"), 
    [Input("model-dropdown", "value"), Input("model-metric", "value")])
    def update_model_graph(model_ids, metric):
        fig = go.Figure()
        fig.update_layout(title="No data available")
        # fig.layout.plot_bgcolor = '#090909'
        fig.layout.paper_bgcolor = '#99D3DF'
        if(not model_ids):
            model_ids = [5, 4, 1]
            metric = "max_f1"
            # return fig
        for model_id in model_ids:
            submissions = Submission.query.filter_by(id=model_id).all()
            if(len(submissions) <= 0 or not metric):
                continue
            model_submission = submissions[0]
            all_metrics = model_submission.metrics
            if(len(all_metrics) <= 0):
                continue
            model_metrics = pickle.loads(all_metrics[0].metrics)
            
            if(metric == "max_f1"):
                precs = model_metrics["prec"]
                recs = model_metrics["rec"]
                fig.add_trace(go.Scatter(x=recs, y=precs,
                        mode='lines',
                        name="{} (Max-F1 {})".format(model_submission.model, model_submission.max_f1)))
                fig.update_layout(title='Precision-Recall',
                    xaxis_title='Recall',
                    yaxis_title='Precision')
            elif(metric == "s_min"):
                mi = model_metrics["mi"]
                ru = model_metrics["ru"]
                fig.add_trace(go.Scatter(x=mi, y=ru,
                        mode='lines',
                        name="{} (S-min {})".format(model_submission.model, model_submission.s_min)))
                fig.update_layout(title='Missing Information - Remaining Uncertainty',
                    xaxis_title='Remaining Uncertainty',
                    yaxis_title='Missing Information')
            else:
                rms = model_metrics["rm"]
                fig.add_trace(go.Scatter(y=rms,
                        mode='lines',
                        name="{} (Recall Metric {})".format(model_submission.model, model_submission.max_rm)))
                fig.update_layout(title='Missing Information - Remaining Uncertainty',
                    xaxis_title='Threshold',
                    yaxis_title='Recall Metric')
        return fig

    @dash_app.callback(
        Output("bar-chart", "figure"), 
        [Input("dropdown", "value"), Input("url", "pathname")])
    def update_bar_chart(namespace, pathname):
        data_id = pathname.split("/")[-1]
        if(data_id in analysis_content_dict):
            df = analysis_content_dict[data_id][namespace]
            fig = px.bar(df, x="GO_term", y="count", title="GO Term Occurrences")
            return fig
        else:
            return px.bar(title="Data Not Available")
        
    
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