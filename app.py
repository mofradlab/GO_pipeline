from collections import defaultdict
from flask import Flask, render_template, request, send_file
from flask.helpers import send_from_directory, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from pipeline_app.app_gen import app, db, root_path, Submission, SubmissionMetrics, SubmissionDescription
from pipeline_app.pipeline_methods import construct_prot_dict, run_pipeline
from go_bench.load_tools import read_sparse, load_GO_tsv_file, convert_to_sparse_matrix
from go_bench.metrics import threshold_stats
from pipeline_app.dash_app import initialize_dash_app
import tarfile
import logging
import os
import datetime, time, json, pickle

with open("{}/../../data/ia_dict.json".format(root_path), "r") as f:
    str_ia_dict = json.load(f) #Load precalculated ia values for all GO terms. 
    go_ia_dict = {int(x): y for x, y in str_ia_dict.items()}

ALLOWED_EXTENSIONS = {'txt', 'tsv', 'csv', 'pfp', 'tab'}
ALLOWED_COMPRESSION = {'gz', 'gzip'}
def allowed_file(filename):
    fn_parts = filename.rsplit('.', -1)
    if(len(fn_parts) > 2):
        if(fn_parts[-1].lower() in ALLOWED_COMPRESSION):
            fn_parts = fn_parts[:-1]
    return len(fn_parts) > 1 and fn_parts[-1] in ALLOWED_EXTENSIONS

#Maps form ids to form data so that they can later be used for dataset construction. 
form_data = {}
analysis_content_dict = {}

logging.error("made imports and initialized dash app")

@app.route('/')
def default():
    return "hello world"


with app.test_request_context():
    requests_pathname_prefix = url_for('default') + 'results/'

dash_app = initialize_dash_app(__name__, app, analysis_content_dict, 
                    routes_pathname_prefix="/results/", 
                    requests_pathname_prefix=requests_pathname_prefix)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/go_header')
def go_header():
    return render_template('header.html')

@app.route("/dataset_form")
def dataset_construction():
    return render_template("dataset_form.html")

@app.route("/dataset_links")
def dataset_links():
    return render_template("dataset_links.html")

@app.route("/upload_form")
def send_upload_form():
    return render_template("upload_form.html")

@app.route('/leaderboard_table', methods=['POST'])
def get_table():
    req_dict = request.form.to_dict()
    print(req_dict)
    
    namespace = req_dict["namespace"]
    testing_set = req_dict["testing_set"]
    testing_quality = req_dict["testing_quality"]
    sort_column = req_dict["sort_col"]
    desc = req_dict["desc"]
    page_num = 0 #int(req_dict["page_num"])
    page_length = 500 # int(req_dict["page_len"])
    print(sort_column)
    order_col = defaultdict(lambda: Submission.max_f1, {"max_f1": Submission.max_f1, "s_min": Submission.s_min, 
                "submission_date": Submission.submission_date, 
                "group_name": Submission.group_name, "model": Submission.model})
    if(desc == "desc"):
        query_ordering = order_col[sort_column].desc()
    else:
        query_ordering = order_col[sort_column].asc()
    print("query ordering", query_ordering)
        
    headings = ["Group", "Model", "Max F1", "S Min", "Submission Date"]
    col_names = ["group_name", "model", "max_f1", "s_min", "submission_date"]
    submissions = Submission.query.filter_by(namespace=namespace)\
        .filter_by(testing_set=testing_set).filter_by(testing_quality=testing_quality)\
        .order_by(query_ordering).all()

    data = [[s.group_name, s.model, s.max_f1, s.s_min, s.submission_date] for s in submissions]
    page_start = min(len(data), page_num*page_length)
    page_end = min(len(data), (page_num+1)*page_length)
    data = data[page_start:page_end]
    print([s.s_min for s in submissions])
    return render_template("leaderboard_table.html", headings=headings, data=data, col_names=col_names, zip=zip)


@app.route("/leaderboard")
def leaderboard():
    namespace = "molecular_function"
    testing_set = "cluster50"
    testing_quality = "exp"
    headings = ["Group", "Model", "Max F1", "S Min", "Submission Date"]
    submissions = Submission.query.filter_by(namespace=namespace)\
        .filter_by(testing_set=testing_set).filter_by(testing_quality=testing_quality)\
        .order_by(Submission.max_f1.desc()).all()
    data = [[s.group_name, s.model, s.max_f1, s.s_min, s.submission_date] for s in submissions]
    col_names = ["group_name", "model", "max_f1", "s_min", "submission_date"]
    return render_template("leaderboard.html", headings=headings, data=data, col_names=col_names, zip=zip)
    #return render_template("leaderboard.html", headings=headings, data=data)

@app.route("/file_download/<form_hash>")
def file_download(form_hash):
    file_path = "{}/../../data/{}_gene_ontology_data.tar.gz".format(root_path, form_hash)
    if(os.path.isfile(file_path)):
        return send_file(file_path, as_attachment=True, attachment_filename="GO_benchmark_data.tar.gz")
    else:
        return "File not found. Try resubmitting form."

@app.route("/loading_page/<form_hash>")
def loading_page(form_hash):
    return render_template("loading_page.html")

@app.route("/documentation")
def get_documentation():
    return render_template("documentation.html")

@app.route('/save_form', methods=['POST'])
def save_form():
    if request.method == 'POST':
        req_dict = request.form.to_dict()
        print(req_dict)
        print("storing form under key {}".format(req_dict["form_content_id"]))
        print(req_dict)
        form_data[req_dict["form_content_id"]] = req_dict
        return "Form recieved."

@app.route('/receive_upload_form', methods=['POST'])
def receive_upload_form():
    if request.method == 'POST':
        upload_dict = request.form.to_dict()
        print("upload dict")
        print(upload_dict)
        try:
            namespace = upload_dict["namespace"]
            testing_set = upload_dict["testing_set"]
            testing_quality = upload_dict["testing_quality"]
            group = upload_dict["group"]
            model = upload_dict["model_name"]
            file_type = upload_dict["file_type"]
            if("model_description" in upload_dict):
                model_description = upload_dict["model_description"]
            else:
                model_description = ""
            submission_time = time.time()
        except:
            print("missing fields")
            return "[Error] Make sure all required fields are filled in."
        
        if 'submission_file' not in request.files:
            return "[Error] Submission File not included."
        file = request.files['submission_file']
        print(model, group, namespace, testing_set, testing_quality)
        if not file or file.filename == '':
            print("filename error")
            return "[Error] No file selected."

        save_path = os.path.join(app.config['UPLOAD_FOLDER'], str(int(submission_time))+file.filename)
        if file and allowed_file(file.filename):
            file.save(save_path)
        else:
            return "[Error] Invalid file type."
        print("saved file")

        #Load testing predictions
        test_path = "{}/../../data/testing_datasets/{}/{}".format(root_path, testing_set, testing_quality)
        with open("{}/{}_terms.json".format(test_path, namespace), "r") as f: 
            test_ids = json.load(f)
        testing_dict = load_GO_tsv_file("{}/testing_{}_annotations.tsv".format(test_path, namespace))
        test_prot_ids = [prot_id for prot_id in testing_dict.keys()]
        testing_matrix = convert_to_sparse_matrix(testing_dict, test_ids, test_prot_ids)
        # try:
        if(file_type == "single_entry"):
            prediction_matrix = read_sparse(save_path, test_prot_ids, test_ids)
        else:
            prediction_dict = load_GO_tsv_file(save_path)
            prediction_matrix = convert_to_sparse_matrix(prediction_dict, test_ids, test_prot_ids)
        # except Exception as e:
        #     os.remove(save_path)
        #     print("error", e)
        #     return "[Error] " + str(e)
        os.remove(save_path)
        print("created matrices")
        test_ia = np.zeros(len(test_ids))
        for i, test_id in enumerate(test_ids):
            id_int = int(test_id[3:])
            if(id_int in go_ia_dict):
                test_ia[i] = go_ia_dict[id_int]

        precs, recs, f_scores, rms, mis, rus, s_vals = threshold_stats(testing_matrix, prediction_matrix, test_ia)
        print(max(f_scores), "max f1")
        #Load predictions into sparse matrix with read_sparse. Add some helpful error messages for users. 
        #Load testing set into sparse matrix. 
        #Generate precision-recall statistics and save in SQL database. 
        #Return message explaining results.  
        stat_dict = {"prec": precs, "rec": recs, "f1": f_scores, 
        "rm": rms, "mi": mis, "ru": rus, "s": s_vals}

        submission_date = str(datetime.date.today())
        s = Submission(testing_set=testing_set, 
                        testing_quality=testing_quality, 
                        namespace=namespace, 
                        model=model, group_name=group, 
                        max_f1=np.around(max(f_scores), 3),  
                        s_min=np.around(min(s_vals), 3), 
                        max_rm=np.around(max(rms), 3), 
                        submission_date=submission_date)
        SubmissionMetrics(metrics=pickle.dumps(stat_dict), submission=s)
        SubmissionDescription(description=model_description, submission=s)
        db.session.add(s)
        db.session.commit()
        print(s.id, s.max_f1, s.s_min, s.max_rm)
        return "Your predictions were successfully submitted. They recieved a maximum F1 score of {}.".format(s.max_f1)

@app.route('/server', methods=['GET', 'POST'])
def process_sequence():
    print("recieved post request")
    print("root path", root_path)
    if request.method == 'POST':
        form_hash = list(request.form.to_dict().keys())[0]
        print(form_hash)

        if(os.path.isfile("{}/../../data/{}_gene_ontology_data.tar.gz".format(root_path, form_hash))):
            print("File for {} already generated".format(form_hash))
            return "Form Processed"

        req_dict = form_data[form_hash]
        logging.error(req_dict)
        print(req_dict)
        print("parsing request\n\n\n\n")
        input_dict = construct_prot_dict(req_dict)
        print(input_dict)

        # return send_file("{}/../../data/gene_ontology_data.tar.gz".format(root_path))

        run_pipeline(input_dict, analysis_content_dict)
        
        source_dir = "{}/../../data/generated_datasets/".format(root_path)
        with tarfile.open("{}/../../data/{}_gene_ontology_data.tar.gz".format(root_path, form_hash), "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

        filter_LRU_archive_files("{}/../../data".format(root_path), 2e9, "_gene_ontology_data") #Make sure server doesn't cache too many files. 
        filter_LRU_archive_files("{}/../../data/dash_cache".format(root_path), 2e8)
        return "Form Processed"

#Archive files should be deleted, starting with the oldest, when they take up more than 2 GB of space. 
def filter_LRU_archive_files(file_dir, max_disk_usage, file_identifier=None):
    print("filtering {} archives for files containing {}".format(file_dir, file_identifier))
    if(file_identifier is None):
        file_identifier = ""
    files = [x for x in os.listdir(file_dir) if file_identifier in x]
    print("current files", files)
    file_access_times = {}
    file_sizes = {}
    total_bytes = 0
    for f_name in files:
        file_stats = os.stat(os.path.join(file_dir, f_name))
        print(file_stats)
        total_bytes += file_stats.st_size
        file_sizes[f_name] = file_stats.st_size
        file_access_times[f_name] = file_stats.st_atime

    print("total bytes", total_bytes)

    file_access_time_pairs = list(zip(file_access_times.values(), file_access_times.keys()))
    file_access_time_pairs.sort()

    for access_time, f_name in file_access_time_pairs:
        print("remaining bytes", total_bytes)
        if(total_bytes < max_disk_usage):
            break
        print("removing file:", f_name)
        os.remove(os.path.join(file_dir, f_name))
        total_bytes -= file_sizes[f_name]

if __name__ == '__main__':
    app.run()
