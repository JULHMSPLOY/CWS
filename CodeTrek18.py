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

@app.route('/python', methods=['GET', 'POST'])
def python_practice():
    challenges = [
        {
            'id': 1,
            'title': 'Rectangle Calculator',
            'difficulty': 'Easy',
            'task': 'A program that receives the width and length of a rectangle and then calculates the area and perimeter (or circumference).',
            'test_code': 'Rectangle\nEnter width and length: ',
            'example_input': '4 5',
            'expected_output': 'Width =  4.0 Length =  5.0\nArea = 20.0, Perimeter = 18.0',
            'hints': ['Remember to convert input strings to float', 'Area = width * length', 'Perimeter = 2 * (width + length)'],
            'valid_solutions': ["print('Rectangle')\nwd, lg = input('Enter width and length: ').split()\nwd = float(wd); lg = float(lg)\nprint('Width = ', wd, 'Length = ', lg)\nA = wd*lg\nP = wd+wd+lg+lg\nprint(F'Area = {A}, Perimeter = {P}')"]
        },
        {
            'id': 2,
            'title': 'Temperature Converter',
            'difficulty': 'Easy',
            'task': 'Create a program that converts Celsius to Fahrenheit. Formula: °F = (°C × 9/5) + 32',
            'test_code': 'Enter temperature in Celsius: ',
            'example_input': '25',
            'expected_output': '25.0 Celsius is equal to 77.0 Fahrenheit',
            'hints': ['Convert input to float', 'Use the formula: F = (C * 9/5) + 32'],
            'valid_solutions': ["celsius = float(input('Enter temperature in Celsius: '))\nfahrenheit = (celsius * 9/5) + 32\nprint(f'{celsius} Celsius is equal to {fahrenheit} Fahrenheit')"]
        },
        {
            'id': 3,
            'title': 'Number Sequence',
            'difficulty': 'Medium',
            'task': 'Create a program that prints all numbers from 1 to N that are divisible by 3 or 5.',
            'test_code': 'Enter N: ',
            'example_input': '15',
            'expected_output': 'Numbers divisible by 3 or 5 up to 15: 3, 5, 6, 9, 10, 12, 15',
            'hints': ['Use a for loop to check numbers from 1 to N', 'Use the modulo operator (%) to check divisibility'],
            'valid_solutions': ["n = int(input('Enter N: '))\nnums = [str(i) for i in range(1,n+1) if i%3==0 or i%5==0]\nprint(f'Numbers divisible by 3 or 5 up to {n}: {", ".join(nums)}')"]
        }
    ]

    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None
    next_challenge = None
    test_status = None
    
    if request.method == 'POST':
        user_code = request.form['code']
        show_hint = request.form.get('show_hint', False)

        if show_hint:
            # Handle hint display
            current_hint_index = int(request.form.get('current_hint_index', 0))
            if current_hint_index < len(challenge['hints']):
                feedback = f"Hint: {challenge['hints'][current_hint_index]}"
                test_status = 'hint'
        else:
            try:
                # Test the code with example input
                input_data = challenge['test_code'] + challenge['example_input']
                process = subprocess.run(
                    ['python3', '-c', user_code],
                    input=input_data, text=True, capture_output=True, timeout=5
                )

                result = process.stdout.strip()
                expected = challenge['expected_output'].strip()

                if result == expected:
                    feedback = 'Correct! Well done.'
                    next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None
                    test_status = 'success'
                else:
                    feedback = f'Incorrect solution.\nYour output: "{result}"\nExpected: "{expected}"\nTry again!'
                    test_status = 'error'

            except subprocess.TimeoutExpired:
                feedback = 'Error: Code execution timed out. Your program might have an infinite loop.'
                test_status = 'error'
            except Exception as e:
                feedback = f'Error: {str(e)}'
                test_status = 'error'
                result = None

    return render_template('python.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

@app.route('/matlab', methods=['GET', 'POST'])
def matlab_practice():

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
