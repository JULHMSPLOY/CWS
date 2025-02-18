from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_first_request
def create_tables():
    db.create_all()

@app.route ('/')
def home():
    return render_template('index.html')