from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

Bootstrap(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)

    def __repr__(self):
        return '<User %r>' % self.username
    
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    username = request.from['username']
    email = request.from['email']

    user_exists = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
    if user_exists:
        return "Username or Email already exists!"
    
    new_user = User(username=username, email=email)

    db.session.add(new_user)
    db.session.commit()

@app.route ('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)