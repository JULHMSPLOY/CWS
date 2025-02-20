from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

Bootstrap(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class AuthController:
    @staticmethod
    def resister(username, email, password, confirm_password):
        if password != confirm_password:
            return "Passwords do not match."

        if len(password) < 10:
            return "Password must be at least 10 characters long."

        user_exists = User.query.filter_by(User.username == username) or (User.email == email).first()
        if user_exists:
            return "Username or Email already exists!"

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        return None

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        error = AuthController.resister(
            request.form['username'],
            request.form['email'],
            request.form['password'],
            request.form['confirm_password']
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Account created successfully!', 'success')
            return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
