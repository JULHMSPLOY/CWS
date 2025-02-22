from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import subprocess
import sqlite3
import os
import bcrypt

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['ALLOWED_EXTENSIONS'] ={'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

Bootstrap(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.Column(db.String(200), nullable=True)
    profile_picture = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class AuthController:
    @staticmethod
    def register(username, email, password, confirm_password):
        try:
            if password != confirm_password:
                return "Passwords do not match."

            if len(password) < 10:
                return "Password must be at least 10 characters long."

            user_exists = User.query.filter(db.or_(User.username == username, User.email == email)).first()
            if user_exists:
                return "Username or Email already exists!"

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, email=email, password=hashed_password)
        
            db.session.add(new_user)
            db.session.commit()
            return None
        except Exception as e:
            db.session.rollback()
            return f"Database error: {str(e)}"

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
        print("Method:", request.method)

    if request.method == 'POST':
        error = AuthController.register(
            username =request.form['username'],
            email = request.form['email'],
            password = request.form['password'],
            confirm_password = request.form['confirm_password']
        )

        print("Error:", error)
        
        if error:
            flash(error, 'danger')
            return render_template('signup.html')
        else:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            skills = request.form['skills']
            file = request.files['profile_picture']

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.skills = skills

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_picture = filename

            db.session.commit()  
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('profile.html', user=user)
    else:
        flash('Please log in to view or update your profile.', 'danger')
        return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/choose_challenge', methods=['GET'])
def choose_challenge():
    challenges = {
        'Python': '/python',
        'MATLAB': '/matlab',
        'SQL': '/sql',
        'C': '/c'
    }

    return render_template('choose_challenge.html', challenges=challenges)

class PythonChallenges:
    @staticmethod
    def get_challenges():
        return [
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
                'valid_solutions': ["n = int(input('Enter N: '))\nnums = [str(i) for i in range(1,n+1) if i%3==0 or i%5==0]\nprint(f'Numbers divisible by 3 or 5 up to {n}: {', '.join(nums)}')"]
            }
        ]
    
    @staticmethod
    def validate_solution(user_code, challenge):
        try:
            input_data = challenge['test_code'] + challenge['example_input']
            process = subprocess.run(['python3', '-c', user_code], input=input_data, text=True, capture_output=True, timeout=5)
            result = process.stdout.strip()
            expected = challenge['expected_output'].strip()
            if result == expected:
                return 'Correct! Well done.'
            else:
                return f'Incorrect solution.\nYour output: "{result}"\nExpected: "{expected}"\nTry again!'
        except subprocess.TimeoutExpired:
            return 'Error: Code execution timed out. Your program might have an infinite loop.'
        except Exception as e:
            return f'Error: {str(e)}'

@app.route('/python', methods=['GET', 'POST'])
def python_practice():
    challenges = PythonChallenges.get_challenges()
    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None
    next_challenge = None
    test_status = None

    if request.method == 'POST':
        user_code = request.form['code']
        feedback = PythonChallenges.validate_solution(user_code, challenge)
        if "Correct!" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None

    return render_template('python.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

class MatlabChallenges:
    @staticmethod
    def get_challenges():
        return [
            {
                'id': 1,
                'title': 'Circle Area and Circumference',
                'difficulty': 'Easy',
                'task': 'Write a MATLAB script that calculates the area and circumference of a circle given its radius.',
                'test_code': '5',
                'example_input': '5',
                'expected_output': 'Area = 78.54, Circumference = 31.42',
                'hints': ['Use pi in MATLAB', 'Area = pi * r^2', 'Circumference = 2 * pi * r'],
                'valid_solutions': ["r = input('Enter radius: ');\nA = pi * r^2;\nC = 2 * pi * r;\nfprintf('Area = %.2f, Circumference = %.2f\n', A, C);"]
            },
            {
                'id': 2,
                'title': 'Fibonacci Sequence',
                'difficulty': 'Medium',
                'task': 'Write a MATLAB script that generates the first N numbers of the Fibonacci sequence.',
                'test_code': '6',
                'example_input': '6',
                'expected_output': '0 1 1 2 3 5',
                'hints': ['Use a loop', 'Fibonacci(n) = Fibonacci(n-1) + Fibonacci(n-2)'],
                'valid_solutions': ["n = input('Enter N: ');\nfib = zeros(1,n);\nfib(1) = 0;\nfib(2) = 1;\nfor i = 3:n\nfib(i) = fib(i-1) + fib(i-2);\nend\nfprintf('%d ', fib);"]
            }
        ]
    
    @staticmethod
    def validate_solution(user_code, challenge):
        try:
            input_data = challenge['example_input']
            process = subprocess.run(['matlab', '-batch', user_code], input=input_data, text=True, capture_output=True, timeout=5)
            result = process.stdout.strip()
            expected = challenge['expected_output'].strip()
            if result == expected:
                return 'Correct! Well done.'
            else:
                return f'Incorrect solution.\nYour output: "{result}"\nExpected: "{expected}"\nTry again!'
        except subprocess.TimeoutExpired:
            return 'Error: Code execution timed out. Your program might have an infinite loop.'
        except Exception as e:
            return f'Error: {str(e)}'

@app.route('/matlab', methods=['GET', 'POST'])
def matlab_practice():
    challenges = MatlabChallenges.get_challenges()
    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None
    next_challenge = None
    test_status = None

    if request.method == 'POST':
        user_code = request.form['code']
        feedback = MatlabChallenges.validate_solution(user_code, challenge)
        if "Correct!" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None

    return render_template('matlab.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

class SQLChallenges:
    @staticmethod
    def get_challenges():
        return [
            {
            'id': 1,
            'title': 'Create Table and Insert Data',
            'difficulty': 'Easy',
            'task': 'Write an SQL query to create a table named `students` with columns `id`, `name`, and `age`, and insert data into the table.',
            'test_code': 'INSERT INTO students (id, name, age) VALUES (1, "John Doe", 25);',
            'example_input': 'CREATE TABLE students (id INT, name VARCHAR(50), age INT); INSERT INTO students (id, name, age) VALUES (1, "John Doe", 25);',
            'expected_output': 'Table `students` created and data inserted.',
            'hints': ['Use the CREATE TABLE statement', 'Use the INSERT INTO statement to add records'],
            'valid_solutions': ["CREATE TABLE students (id INT, name VARCHAR(50), age INT);\nINSERT INTO students (id, name, age) VALUES (1, 'John Doe', 25);"]
        },
        {
            'id': 2,
            'title': 'Select Query',
            'difficulty': 'Easy',
            'task': 'Write an SQL query to select all the data from the `students` table.',
            'test_code': 'SELECT * FROM students;',
            'example_input': 'SELECT * FROM students;',
            'expected_output': '1 | John Doe | 25',
            'hints': ['Use the SELECT statement', 'Use the wildcard (*) to select all columns'],
            'valid_solutions': ["SELECT * FROM students;"]
        },
        {
            'id': 3,
            'title': 'Update Data',
            'difficulty': 'Medium',
            'task': 'Write an SQL query to update the age of the student with id = 1 to 26.',
            'test_code': 'UPDATE students SET age = 26 WHERE id = 1;',
            'example_input': 'UPDATE students SET age = 26 WHERE id = 1;',
            'expected_output': '1 | John Doe | 26',
            'hints': ['Use the UPDATE statement', 'Use the WHERE clause to specify the row to update'],
            'valid_solutions': ["UPDATE students SET age = 26 WHERE id = 1;"]
        }
    ]

    @staticmethod
    def validate_solution(user_code, challenge):
        try:
            connection = sqlite3.connect('test.db')
            cursor = connection.cursor()
            cursor.execute(user_code)
            connection.commit()
            result = "Table `students` created and data inserted."
            connection.close()
            return result
        except Exception as e:
            return f'Error: {str(e)}'

@app.route('/sql', methods=['GET', 'POST'])
def sql_practice():
    challenges = SQLChallenges.get_challenges()
    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None
    next_challenge = None
    test_status = None

    if request.method == 'POST':
        user_code = request.form['code']
        feedback = SQLChallenges.validate_solution(user_code, challenge)
        if "created and data inserted" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None

    return render_template('sql.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

class CChallenges:
    @staticmethod
    def get_challenges():
        return [
            {
                'id': 1,
                'title': 'Rectangle Calculator',
                'difficulty': 'Easy',
                'task': 'A program that receives the width and length of a rectangle and then calculates the area and perimeter.',
                'test_code': 'Enter width and length: ',
                'example_input': '4 5',
                'expected_output': 'Width = 4.0 Length = 5.0\nArea = 20.0, Perimeter = 18.0',
                'hints': ['Remember to convert input strings to float', 'Area = width * length', 'Perimeter = 2 * (width + length)'],
                'valid_solutions': [
                    """#include <stdio.h>
                    int main() {
                        float wd, lg, A, P;
                        printf("Enter width and length: ");
                        scanf("%f %f", &wd, &lg);
                        printf("Width = %.1f Length = %.1f\n", wd, lg);
                        A = wd * lg;
                        P = 2 * (wd + lg);
                        printf("Area = %.1f, Perimeter = %.1f", A, P);
                        return 0;
                    }"""
                ]
            },
            {
                'id': 2,
                'title': 'Temperature Converter',
                'difficulty': 'Easy',
                'task': 'Create a program that converts Celsius to Fahrenheit.',
                'test_code': 'Enter temperature in Celsius: ',
                'example_input': '25',
                'expected_output': '25.0 Celsius is equal to 77.0 Fahrenheit',
                'hints': ['Use the formula: °F = (°C × 9/5) + 32'],
                'valid_solutions': [
                    """#include <stdio.h>
                    int main() {
                        float celsius, fahrenheit;
                        printf("Enter temperature in Celsius: ");
                        scanf("%f", &celsius);
                        fahrenheit = (celsius * 9/5) + 32;
                        printf("%.1f Celsius is equal to %.1f Fahrenheit", celsius, fahrenheit);
                        return 0;
                    }"""
                ]
            }
        ]
    
    @staticmethod
    def validate_solution(user_code, challenge):
        try:
            filename = 'user_code.c'
            with open(filename, 'w') as file:
                file.write(user_code)

            compile_process = subprocess.run(['gcc', 'user_code.c', '-o', 'user_code'], capture_output=True, text=True)
            if compile_process.returncode != 0:
                return f'Error compiling code: {compile_process.stderr}'
            
            input_data = challenge['example_input']
            run_process = subprocess.run(['./user_code'], input=input_data, text=True, capture_output=True, timeout=5)
            result = run_process.stdout.strip()

            expected = challenge['expected_output'].strip()

            if result == expected:
                return 'Correct! Well done.'
            else:
                return f'Incorrect solution.\nYour output: "{result}"\nExpected: "{expected}"\nTry again!'

        except subprocess.TimeoutExpired:
            return 'Error: Code execution timed out. Your program might have an infinite loop.'
        except Exception as e:
            return f'Error: {str(e)}'
        
@app.route('/c', methods=['GET', 'POST'])
def c_practice():
    challenges = CChallenges.get_challenges()
    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None
    next_challenge = None
    test_status = None
    
    if request.method == 'POST':
        user_code = request.form['code']
        feedback = CChallenges.validate_solution(user_code, challenge)
        if "Correct!" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None
            test_status = 'Passed'  
        else:
            test_status = 'Failed'

    return render_template('c.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized successfully")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
