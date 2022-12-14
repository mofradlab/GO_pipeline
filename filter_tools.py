from goatools.obo_parser import GODag
import os
root_path = os.path.abspath(os.path.dirname(__file__))
godag = GODag("{}/../data/go-basic.obo".format(root_path))

#godag_obsolete = GODag("../data/go-basic.obo", load_obsolete=True)

#protein_annotation_dict should map proteins to lists of (GO ID, evidence code) tuples. 
#Function ignores evidence codes and maps GO annotations to lists of proteins. 
def invert_protein_annotation_dict(protein_annotation_dict):
    annotation_protein_dict = {}
    for prot_id, annotations in protein_annotation_dict.items():
        for annotation in annotations:
            if(annotation in annotation_protein_dict):
                annotation_protein_dict[annotation].append(prot_id)
            else:
                annotation_protein_dict[annotation] = [prot_id]
    return annotation_protein_dict

def get_counts_dict(annotation_protein_dict):
    return {key:len(value) for key, value in annotation_protein_dict.items()}

def list_ancestors(term, godag):
    ancestors = list(godag[term]._parents)
    seen = set()
    while ancestors:
        ancestor = ancestors.pop()
        if(ancestor in seen):
            continue
        seen.add(ancestor)
        ancestors.extend(godag[ancestor]._parents)
        yield ancestor

def filter_dict(protein_annotation_dict, term_list):
    filtered_annotation_dict = {}
    term_set = set(term_list)
    for prot_id in protein_annotation_dict.keys():
        filtered_terms = []
        for term in protein_annotation_dict[prot_id]:
            if(term in term_set):
                filtered_terms.append(term)
        if(filtered_terms):
            filtered_annotation_dict[prot_id] = filtered_terms
    return filtered_annotation_dict


def propogate_annotations(annotation_protein_dict, term_list, godag):
    term_set = set(term_list)
    term_ancestor_mappings = {term: [x for x in list_ancestors(term, godag) if x in term_set] for term in term_list}
    for prot_id in annotation_protein_dict:
        propogated_annotations = set(annotation_protein_dict[prot_id])
        for term in annotation_protein_dict[prot_id]:
            propogated_annotations.update(term_ancestor_mappings[term])
        annotation_protein_dict[prot_id] = list(propogated_annotations)
        
#Returns the top term_count most popular terms, as sorted by frequency. 
def enforce_count(annotation_count_dict, namespace, term_count):
    term_list = [] 
    for term, count in annotation_count_dict.items():
        if(godag[term].namespace == namespace):
            term_list.append((count, term))
    term_list.sort(reverse=True)
    return [x[1] for x in term_list[:term_count]]

def enforce_threshold(annotation_count_dict, namespace, threshold, term_blacklist=None):
    if(not term_blacklist):
        term_blacklist = {}
    else:
        term_blacklist = set(term_blacklist)
    term_list = [] 
    for term, count in annotation_count_dict.items():
        if((godag[term].namespace == namespace or namespace == "all") and term not in term_blacklist):
            term_list.append((count, term))
    term_list.sort(reverse=True)
    i = 0
    while i < len(term_list) and term_list[i][0] >= threshold:
        i += 1
    return [x[1] for x in term_list[:i]]