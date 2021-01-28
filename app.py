from flask import Flask, render_template, request, send_file
from pipeline_app.pipeline_methods import construct_prot_dict, pipeline
import tarfile
import logging
import os
from pipeline_app.dash_app import initialize_dash_app

logging.basicConfig(filename=(os.path.abspath(os.path.dirname(__file__)) + 'app.log'), level=logging.DEBUG)
logging.error("test message")

app = Flask(__name__)

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
    root_path = os.path.abspath(os.path.dirname(__file__))
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
        print(req_dict)
        form_data[req_dict["form_content_id"]] = req_dict
        return "Form recieved."

@app.route('/server', methods=['GET', 'POST'])
def process_sequence():
    print("recieved post request")
    if request.method == 'POST':
        form_hash = list(request.form.to_dict().keys())[0]
        print(form_hash)
        root_path = os.path.abspath(os.path.dirname(__file__))
        req_dict = form_data[form_hash]
        logging.debug(req_dict)
        print(req_dict)
        print("parsing request\n\n\n\n")
        input_dict = construct_prot_dict(req_dict)
        print(input_dict)

        root_path = os.path.abspath(os.path.dirname(__file__))
        # return send_file("{}/../../data/gene_ontology_data.tar.gz".format(root_path))

        data_files = os.listdir("{}/../../data".format(root_path))
        
        pipeline(input_dict, analysis_content_dict)
        
        source_dir = "{}/../../data/generated_datasets/".format(root_path)
        with tarfile.open("{}/../../data/{}_gene_ontology_data.tar.gz".format(root_path, form_hash), "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        #config_dict = parse_server_multidict(request.form)
        #return str(config_dict)
        return "Form Processed"


if __name__ == '__main__':
    app.run()
