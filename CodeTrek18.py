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
import subprocess

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'your_secret_key'
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
    def register(username, email, password, confirm_password):
        if password != confirm_password:
            return "Passwords do not match."

        if len(password) < 10:
            return "Password must be at least 10 characters long."

        user_exists = User.query.filter((User.username == username) or (User.email == email)).first()
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
        error = AuthController.register(
            request.form['username'],
            request.form['email'],
            request.form['password'],
            request.form['confirm_password']
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if user and AuthController.check_password(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/python', methods = ['GET', 'POST'])
def python_practice():
    challenges = [
        {
            'id' : 1,
            'task' : 'A program that receives the width and length of a rectangle and then calculates the area and perimeter (or circumference).',
            'test_code' : 'Rectangle\nEnter width and length: ',
            'expected_output' : 'Width =  4.0 Length =  5.0\nArea = 20.0, Perimeter = 18.0',
            'valid_solutions' : ["print('Rectangle')\nwd,lg = input('Enter width and length: ').split()\nwd = float(wd); lg = float(lg)\nprint('Width = ', wd, 'Length = ', lg)\nA = wd*lg\nP = wd+wd+lg+lg\nprint(F'Area = {A}, Perimeter = {P}')"] 
        }
    ]

    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None

    if request.method == 'POST':
        user_code = request.form['code']

        try:
            input_data = challenge['test_code']
            process = subprocess.run(
                ['python3', '-c', user_code],
                input=input_data, text=True, capture_output=True, timeout=5
            )

            result = process.stdout.strip()
            expected = challenge['expected_output'].strip()

            if result == expected:
                feedback = 'Correct! Well done.'
                next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None
            else:
                feedback = 'Incorrect solution. Try again!'
                next_challenge = None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
