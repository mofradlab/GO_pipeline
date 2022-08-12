from GO_pipeline.filter_tools import godag
from go_bench.utils import evidence_codes
from go_bench.load_tools import load_protein_annotations
from go_bench.processing import filter_dict, propogate_annotations, get_counts_dict, invert_protein_annotation_dict, enforce_count, enforce_threshold
from go_bench.pipeline import pipeline
from GO_pipeline.app_gen import app

import pandas as pd
import os
import logging
import pickle
import json

from GO_pipeline.load_tools import to_data_num

root_path = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(filename=(os.path.abspath(os.path.dirname(__file__)) + '/app.log'), level=logging.DEBUG)

def construct_tsv(path, prot_dict, prot_ids, term_set):
    print(path, len(prot_dict), len(prot_ids), len(term_set))
    columns = ["Uniprot ID", "GO Associations"]
    with open(path, mode='w') as f:
        f.write("\t".join(columns) + "\n")
        for prot_id in prot_ids:
            if(prot_id in prot_dict):
                terms = term_set.intersection(prot_dict[prot_id])
                if(len(terms) > 0):
                    f.write("{}\t{}\n".format(prot_id, ", ".join(terms)))

def construct_prot_dict(req_dict):
    input_dict = {}
    input_dict["form_content_id"] = req_dict["form_content_id"]
    filter_settings = {}
    filter_settings["evidence_codes"] = [code for code in evidence_codes if code in req_dict]
    if(len(req_dict['max_date']) > 0):
        year, month, day = req_dict['max_date'].split("-")
        filter_settings["max_date"] = to_data_num(year, month, day)
        print("max date num", filter_settings["max_date"])
    
    input_dict["filter_settings"] = filter_settings

    input_dict["propogate_terms"] = "propogate_annotations" in req_dict

    term_filter_data = {}
    term_filter_data["method"] = req_dict["filter_method"]
    term_filter_data["count"] = int(req_dict["selected_count"])

    input_dict["term_filter_data"] = term_filter_data

    namespaces = ["biological_process", "molecular_function", "cellular_component"]
    input_dict["namespaces"] = [namespace for namespace in namespaces if namespace in req_dict]
    input_dict["include_negative_annotations"] = "include_estimated_negative_annotations" in req_dict

    split_type = req_dict["split_method"]

    split_data = {}
    split_data["do_split"] = True
    split_data["types"] = ["training", "validation", "testing"]
    if(split_type == "random"):
        split_data["use_clusters"] = False
    else:
        split_data["use_clusters"] = "50"
    input_dict["split_data"] = split_data
    return input_dict


def run_pipeline(input_dict, analysis_content_dict):
    filter_settings = input_dict["filter_settings"]
    codes = filter_settings["evidence_codes"]
    min_date = None if not "min_date" in filter_settings else filter_settings["min_date"]
    max_date = None if not "max_date" in filter_settings else filter_settings["max_date"]
    goa_path = app.config["GOA_PATH"]

    split_data = input_dict["split_data"]
    split_path = None
    if(split_data["do_split"]):
        if(split_data["use_clusters"] == "50"):
            split_path = "{}/../data/data_splits/cluster50".format(root_path)
        elif(split_data["use_clusters"] == False):
            split_path = "{}/../data/data_splits/random".format(root_path)
    namespaces = input_dict["namespaces"]
    set_types = input_dict["split_data"]["types"]
    propogate_terms = input_dict["propogate_terms"]
    save_dir = "{}/../data/generated_datasets/".format(root_path)

    analysis_content = pipeline(goa_path, split_path, save_dir, godag, codes=codes, 
                            namespaces=namespaces, set_types=set_types, min_date=min_date, max_date=max_date,
                            propogate_terms=propogate_terms)
    
    analysis_content_dict[input_dict["form_content_id"]] = analysis_content
    dash_cache_path = "{}/../data/dash_cache/{}.pkl".format(root_path, input_dict["form_content_id"])
    logging.error("persisting dash info in {}".format(dash_cache_path))
    with open(dash_cache_path, "wb") as f:
        pickle.dump(analysis_content, f)
        