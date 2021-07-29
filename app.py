from flask import Flask, render_template, request, send_file
from pipeline_app.pipeline_methods import construct_prot_dict, pipeline
import tarfile
import logging
import os
from pipeline_app.dash_app import initialize_dash_app

logging.basicConfig(filename=(os.path.abspath(os.path.dirname(__file__)) + '/app.log'), level=logging.DEBUG)
logging.error("test message for app startup")
print("starting app")
app = Flask(__name__)
root_path = os.path.abspath(os.path.dirname(__file__)) #Used for file management because cwd is unknown. 

#Maps form ids to form data so that they can later be used for dataset construction. 
form_data = {}
analysis_content_dict = {}
dash_app = initialize_dash_app(__name__, app, analysis_content_dict, url_base_pathname="/results/")

@app.route('/')
def default():
    return "hello world"

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/dataset_form")
def dataset_construction():
    return render_template("dataset_form.html")

@app.route("/file_download/<form_hash>")
def file_download(form_hash):
    file_path = "{}/../../data/{}_gene_ontology_data.tar.gz".format(root_path, form_hash)
    if(os.path.isfile(file_path)):
        return send_file(file_path)
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
        logging.error(req_dict)
        logging.error("storing form under key {}".format(req_dict["form_content_id"]))
        print(req_dict)
        form_data[req_dict["form_content_id"]] = req_dict
        return "Form recieved."



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
        logging.debug(req_dict)
        print(req_dict)
        print("parsing request\n\n\n\n")
        input_dict = construct_prot_dict(req_dict)
        print(input_dict)

        # return send_file("{}/../../data/gene_ontology_data.tar.gz".format(root_path))
        pipeline(input_dict, analysis_content_dict)
        
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
