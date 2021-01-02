from flask import Flask, render_template, request, send_file

app = Flask(__name__)

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
        print(request.form)
        config_dict = parse_server_multidict(request.form)
        return str(config_dict)

if __name__ == '__main__':
    app.run()