from flask import Flask, render_template, request, send_file
from pipeline_app.pipeline_methods import construct_prot_dict, pipeline
import tarfile
import os
from pipeline_app.dash_app import initialize_dash_app

app = Flask(__name__)

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

@app.route("/file_download")
def file_construction():
    return send_file("../data/swissprot_goa.gaf.gz")

@app.route('/server', methods=['GET', 'POST'])
def process_sequence():
    print("recieved post request")
    if request.method == 'POST':
        req_dict = request.form.to_dict()
        print(req_dict)
        print("parsing request\n\n\n\n")
        input_dict = construct_prot_dict(req_dict)
        print(input_dict)


        root_path = os.path.abspath(os.path.dirname(__file__))
        # return send_file("{}/../../data/gene_ontology_data.tar.gz".format(root_path))

        pipeline(input_dict, analysis_content_dict)
        
        source_dir = "{}/../../data/generated_datasets/".format(root_path)
        with tarfile.open("{}/../../data/gene_ontology_data.tar.gz".format(root_path), "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        #config_dict = parse_server_multidict(request.form)
        #return str(config_dict)
        return send_file("{}/../../data/gene_ontology_data.tar.gz".format(root_path))


if __name__ == '__main__':
    app.run()