import pandas as pd
import numpy as np
from collections import defaultdict
import os
#from Bio.UniProt.GOA import GAF20FIELDS
GAF20FIELDS = ['DB', 'DB_Object_ID', 'DB_Object_Symbol', 'Qualifier', 'GO_ID', 'DB:Reference', 'Evidence', 'With', 'Aspect', 'DB_Object_Name', 'Synonym', 'DB_Object_Type', 'Taxon_ID', 'Date', 'Assigned_By', 'Annotation_Extension', 'Gene_Product_Form_ID']

#Codes are semi-redundant, and proteins are often annotated using multiple codes. 
# annotation_codes = ["ECO_0000247", "ECO_0000250", "ECO_0000255", "ECO_0000266", "ECO_0000269", "ECO_0000270", "ECO_0000303", 
# "ECO_0000304", "ECO_0000305", "ECO_0000314", "ECO_0000315", "ECO_0000316", "ECO_0000317", "ECO_0000318", 
# "ECO_0000353", "ECO_0007001", "ECO_0007003", "ECO_0007005", "ECO_0007007"]

evidence_codes = {'ISO', 'IGI', 'ISA', 'IGC', 'IEP', 
                  'RCA', 'HDA', 'HGI', 'IKR', 'TAS', 'HEP', 
                  'ND', 'IBA', 'IMP', 'EXP', 'IDA', 'IC', 'ISM', 
                  'ISS', 'NAS', 'IRD', 'IEA', 'IPI', 'HMP'}

experimental_codes = {"experiment":("ECO_0000269", 'EXP'), 
                        "direct_assay":("ECO_0000314", 'IDA'), 
                        "physical_interaction":("ECO_0000353", 'IPI'), 
                        "mutant_phenotype":("ECO_0000315", 'IMP'),
                        "genetic_interaction":("ECO_0000316", 'IGI'),
                        "expression_pattern":("ECO_0000270", 'IEP')}

high_throughput_codes = {"high_throughput_experiment": ("ECO_0006056", 'HTP'),
                        "high_throughput_direct_assay": ("ECO_0007005", 'HDA'),
                        "high_throughput_mutant_phenotype":("ECO_0007001", 'HMP'),
                        "high_throughput_genetic_interaction": ("ECO_0007003", 'HGI'),
                        "high_throughput_expression_pattern":("ECO_0007007", 'HEP')
                        }

phylogenetic_codes = {"biological_aspect_of_ancestor":("ECO_0000318", 'IBA'),
                        "biological_aspect_of_descendant":("ECO_0000319", 'IBD'),
                        "key_residues":("ECO_0000320", 'IKR'),
                        "rapid_divergence":("ECO_0000320", 'IRD')
}

reviewed_computational_codes = {"sequence_or_structural_similarity":("ECO_0000250", 'ISS'),
                        "sequence_orthology":("ECO_0000266", 'ISO'),
                        "sequence_alignment":("ECO_0000247", 'ISA'),
                        "sequence_model":("ECO_0000255", 'ISM'),
                        "genomic_context":("ECO_0000317", 'IGC'),
                        "reviewed_computational_analysis":("ECO_0000245", 'RCA')
}

unreviewed_computational_codes = {
    "inferred from electronic annotation": ('IEA'),
}

reviewed_misc_codes = {
    "tracable author statement": ("_", 'TAS'),
    "inferred by curator": ("_", 'NC')
}

unreviewed_misc_codes = {
    "non-tracable author statement": ("_", 'NAS'),
    "no biological data available": ("_", 'ND')
}

def extract_code_acronyms(code_description):
    return [x[1] for x in code_description.values()]

def to_data_num(year, month, day):
    return int(year)*10000+int(month)*100+int(day)

#The annotations dict maps protein ids to a list of (GO annotation, evidence_code) tuples. 

def read_table_annotations(tab_path, protein_annotations_dict, code):
    for df in pd.read_table(tab_path, sep='\t', chunksize=4000, 
                usecols=["Entry", "Gene ontology IDs"], keep_default_na=False, dtype=str):
        for row in df.itertuples():
            name = row[1]
            if(len(name) <= 2):
                print(name)
            annotations = row[2].split("; ")
            annotations = [(annotation, code) for annotation in annotations]
            if(row[1] in protein_annotations_dict):
                protein_annotations_dict[row[1]].extend(annotations)
            else:
                protein_annotations_dict[row[1]] = list(annotations)

def read_codes(codes):
    protein_annotations_dict = {}
    root_path = os.path.abspath(os.path.dirname(__file__))
    for code in codes:
        path = "{}/../../data/uniprot-reviewed[{}].tab".format(root_path, code)
        read_table_annotations(path, protein_annotations_dict, code)
    for prot_id, annotations in protein_annotations_dict.items():
        protein_annotations_dict[prot_id] = list(set([x[0] for x in annotations]))
    return protein_annotations_dict

#Load all protein annotations based on select annotation codes, from a specific time-range. 
def load_protein_annotations(annotation_codes, min_date=0, max_date=1e10):
    annotation_codes = set(annotation_codes)
    annot_dict = defaultdict(set)
    root_path = os.path.abspath(os.path.dirname(__file__))

    df_iter = pd.read_csv("{}/../../data/swissprot_goa.gaf.gz".format(root_path), dtype=str,
                          sep='\t',
                          comment='!',
                          names=GAF20FIELDS,
                          chunksize=int(1e6))    
    for zdf in df_iter:
        # For now, remove all with a qualifier
        dates = zdf.Date.astype(int)
        
        zdf = zdf[zdf.Evidence.isin(annotation_codes) & zdf.Qualifier.isnull() & dates.ge(min_date) & dates.le(max_date)]
        for tup in zdf.itertuples():
            annot_dict[tup[2]].add(tup[5])
    return annot_dict
