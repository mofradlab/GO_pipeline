

#Parses an input dictionary to generate several outputs in the generated_datasets directory. 
def pipeline(input_dict):
    filter_settings = input_dict["filter_settings"]
    codes = filter_settings["evidence_codes"]
    min_date = 0 if "min_date" in filter_settings else filter_settings["min_date"]
    max_date = 1e10 if "max_date" in filter_settings else filter_settings["max_date"]
    
    print("loading proteins")
    prot_dict = load_protein_annotations(codes, min_date=min_date, max_date=max_date) #Read in protein annotations made by specific codes. 
    prot_dict = filter_dict(prot_dict, godag)    
    
    #Read in terms
    term_list = [term for term in godag]
    #Count occurences of each GO term
    if(input_dict["propogate_terms"]):
        propogate_annotations(prot_dict, term_list, godag)
        
    annotation_dict = invert_protein_annotation_dict(prot_dict) #Maps GO IDs to lists of protein IDs. 
    annotation_counts_dict = get_counts_dict(annotation_dict)
        
    print("filtering rare terms")
    #Filter terms for each namespace
    term_filter_data = input_dict["term_filter_data"]
    if(term_filter_data["method"] == "min_samples"):
        filter_method = lambda namespace: enforce_threshold(annotation_counts_dict, namespace, term_filter_data["count"])
    elif(term_filter_data["method"] == "top_k"):
        filter_method = lambda namespace: enforce_count(annotation_counts_dict, namespace, term_filter_data["count"])
    
    for namespace in input_dict["namespaces"]:
        namespace_term_list = filter_method(namespace)
        print("filtering namespace:", namespace)
        print("namespace_term_list length", len(namespace_term_list))

        print("loading split partition")
        split_data = input_dict["split_data"]
        if(split_data["do_split"]):
            for prot_set_type in split_data["types"]:
                if(split_data["use_clusters"] == "50"):
                    split_path = "../data/data_splits/cluster50"
                elif(split_data["use_clusters"] == False):
                    split_path = "../data/data_splits/random"

                with open(f"{split_path}/{prot_set_type}_ids.txt", "r") as f:
                    prot_ids = set([x[:-1] for x in f.readlines()])
                
                print("prot_ids:", len(prot_ids))

                print("saving results")
                path = f"../data/generated_datasets/{prot_set_type}_{namespace}_annotations.tsv"
                print(f"saving to {path}")
                construct_tsv(path, prot_dict, prot_ids, set(namespace_term_list))
                
        else:
            prot_ids = set(prot_dict.keys())

            print("prot_ids:", len(prot_ids))

            print("saving results")
            path = f"../data/generated_datasets/{prot_set_type}_{namespace}_annotations.tsv"
            print(f"saving to {path}")
            construct_tsv(path, prot_dict, prot_ids, set(namespace_term_list))