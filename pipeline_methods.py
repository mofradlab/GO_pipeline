from pipeline_app.filter_tools import godag
from go_bench.utils import evidence_codes
from go_bench.load_tools import load_protein_annotations
from go_bench.processing import filter_dict, propogate_annotations, get_counts_dict, invert_protein_annotation_dict, enforce_count, enforce_threshold
from go_bench.pipeline import pipeline
from pipeline_app.app_gen import app

import pandas as pd
import os
import logging
import pickle
import json

from pipeline_app.load_tools import to_data_num

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
            split_path = "{}/../../data/data_splits/cluster50".format(root_path)
        elif(split_data["use_clusters"] == False):
            split_path = "{}/../../data/data_splits/random".format(root_path)
    namespaces = input_dict["namespaces"]
    set_types = input_dict["split_data"]["types"]
    propogate_terms = input_dict["propogate_terms"]
    save_dir = "{}/../../data/generated_datasets/".format(root_path)

    analysis_content = pipeline(goa_path, split_path, save_dir, godag, codes=codes, 
                            namespaces=namespaces, set_types=set_types, min_date=min_date, max_date=max_date,
                            propogate_terms=propogate_terms)
    
    analysis_content_dict[input_dict["form_content_id"]] = analysis_content
    dash_cache_path = "{}/../../data/dash_cache/{}.pkl".format(root_path, input_dict["form_content_id"])
    logging.error("persisting dash info in {}".format(dash_cache_path))
    with open(dash_cache_path, "wb") as f:
        pickle.dump(analysis_content, f)
    




# #Parses an input dictionary to generate several outputs in the generated_datasets directory. 
# def pipeline(input_dict, analysis_content_dict):
#     analysis_content = {}
#     logging.debug(input_dict)
#     filter_settings = input_dict["filter_settings"]
#     codes = filter_settings["evidence_codes"]
#     min_date = 0 if not "min_date" in filter_settings else filter_settings["min_date"]
#     max_date = 1e10 if not "max_date" in filter_settings else filter_settings["max_date"]
    
#     logging.debug("loading proteins")

#     prot_dict = load_protein_annotations(app.config["GOA_PATH"], codes, min_date=min_date, max_date=max_date) #Read in protein annotations made by specific codes. 
#     prot_dict = filter_dict(prot_dict, godag)
#     logging.debug("propogating terms")
#     #Read in terms
#     term_list = [term for term in godag]
#     logging.debug(sum(len(x) for x in prot_dict.values()))
#     #Count occurences of each GO term
#     if(input_dict["propogate_terms"]):
#         logging.debug("definitely propogating terms")
#         propogate_annotations(prot_dict, term_list, godag)
#     logging.debug(sum(len(x) for x in prot_dict.values()))
#     logging.debug("inverting annotations")
#     annotation_dict = invert_protein_annotation_dict(prot_dict) #Maps GO IDs to lists of protein IDs. 
#     annotation_counts_dict = get_counts_dict(annotation_dict)
#     logging.debug("filtering terms") 
#     print("filtering rare terms")
#     #Filter terms for each namespace
#     term_filter_data = input_dict["term_filter_data"]
#     print("filter data", term_filter_data)
#     if(term_filter_data["method"] == "min_samples"):
#         filter_method = lambda namespace: enforce_threshold(annotation_counts_dict, namespace, term_filter_data["count"])
#     elif(term_filter_data["method"] == "top_k"):
#         filter_method = lambda namespace: enforce_count(annotation_counts_dict, namespace, term_filter_data["count"])

#     for namespace in input_dict["namespaces"]:
#         namespace_term_list = filter_method(namespace)
#         print(f"{namespace} term count {len(namespace_term_list)}")
#         namespace_term_counts = [annotation_counts_dict[term] for term in namespace_term_list]
#         namespace_df = pd.DataFrame(list(zip(namespace_term_list, namespace_term_counts)), columns=["GO_term", "count"])
#         analysis_content[namespace] = namespace_df
#         print("namespace df")
#         print(namespace_df)
        
#         print("filtering namespace:", namespace)
#         print("namespace_term_list length", len(namespace_term_list))
#         json_path = "{}/../../data/generated_datasets/{}_terms.json".format(root_path, namespace)
#         with open(json_path, "w") as f:
#             json.dump(namespace_term_list, f)

#         print("loading split partition")
#         split_data = input_dict["split_data"]
#         if(split_data["do_split"]):
#             for prot_set_type in split_data["types"]:
#                 if(split_data["use_clusters"] == "50"):
#                     split_path = "{}/../../data/data_splits/cluster50".format(root_path)
#                 elif(split_data["use_clusters"] == False):
#                     split_path = "{}/../../data/data_splits/random".format(root_path)

#                 with open("{}/{}_ids.txt".format(split_path, prot_set_type), "r") as f:
#                     prot_ids = set([x[:-1] for x in f.readlines()])
                
#                 print("prot_ids:", len(prot_ids))
#                 logging.debug("saving results")
#                 print("saving results")
#                 path = "{}/../../data/generated_datasets/{}_{}_annotations.tsv".format(root_path, prot_set_type, namespace)
#                 print("saving to {}".format(path))
#                 construct_tsv(path, prot_dict, prot_ids, set(namespace_term_list))
#         else:
#             prot_ids = set(prot_dict.keys())

#             print("prot_ids:", len(prot_ids))

#             print("saving results")
#             path = "{}/../../data/generated_datasets/{}_{}_annotations.tsv".format(root_path, prot_set_type, namespace)
#             print("saving to {}".format(path))
#             construct_tsv(path, prot_dict, prot_ids, set(namespace_term_list))
#     analysis_content_dict[input_dict["form_content_id"]] = analysis_content
#     dash_cache_path = "{}/../../data/dash_cache/{}.pkl".format(root_path, input_dict["form_content_id"])
#     logging.error("persisting dash info in {}".format(dash_cache_path))
#     with open(dash_cache_path, "wb") as f:
#         pickle.dump(analysis_content, f)

