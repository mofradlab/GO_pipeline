from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

root_path = os.path.abspath(os.path.dirname(__file__)) #Used for file management because cwd is unknown. 
logging.basicConfig(filename=root_path + '/app.log', level=logging.ERROR)
logging.error("test message for app startup from app_gen")
print("flask __name__", __name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "{}/../../data/user_uploads".format(root_path)
app.config['GOA_PATH'] = "../../data/swissprot_goa.gaf.gz" 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/../../data/SQL_leaderboard.db'.format(root_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.context_processor
def inject_base_url():
    return dict(base_url="/")

#Basic submission info. 
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    testing_set = db.Column(db.String(16), nullable=False)
    testing_quality = db.Column(db.String(16), nullable=False)
    namespace = db.Column(db.String(32), nullable=False)
    model = db.Column(db.String(32), nullable=False)
    group_name = db.Column(db.String(32), nullable=False)
    max_f1 = db.Column(db.Float)
    s_min = db.Column(db.Float)
    max_rm = db.Column(db.Float)
    submission_date = db.Column(db.String(16))

    def __repr__(self):
        return '<ID {}, Testing Set {}, Model {}, Group {}, F1 {}>'.format(
            self.id, self.submission_date, self.testing_set, self.model, self.group_name, self.f1_score)

#Large metric files, including Prec-Rec and MI, RU curves. 
class SubmissionMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    submission = db.relationship('Submission',
        backref=db.backref('metrics', lazy=True))
    metrics = db.Column(db.PickleType) #Stores pickled dictionary of lists. 

    def __repr__(self):
        return '<Submission {} Metrics>'.format(self.submission_id)

class SubmissionDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    submission = db.relationship('Submission',
        backref=db.backref('descriptions', lazy=True))
    description = db.Column(db.Text)

    def __repr__(self):
        return '<Submission Description %r>' % self.description