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

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['ALLOWED_EXTENSIONS'] ={'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

Bootstrap(app)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_type = db.Column(db.String(20), nullable=False)  
    challenge_id = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Progress {self.user_id}-{self.challenge_type}-{self.challenge_id}>'

class UserAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_type = db.Column(db.String(20), nullable=False)
    challenge_id = db.Column(db.Integer, nullable=False)
    code_submitted = db.Column(db.Text, nullable=False)
    succeeded = db.Column(db.Boolean, default=False)
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attempt {self.user_id}-{self.challenge_type}-{self.challenge_id}>'

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
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    attempts = db.relationship('UserAttempt', backref='user', lazy=True)

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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

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

def update_user_progress(user_id, challenge_type, challenge_id, succeeded):
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        challenge_type=challenge_type,
        challenge_id=challenge_id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            challenge_type=challenge_type,
            challenge_id=challenge_id
        )
        db.session.add(progress)

    progress.attempts += 1
    if succeeded and not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.utcnow()

    attempt = UserAttempt(
        user_id=user_id,
        challenge_type=challenge_type,
        challenge_id=challenge_id,
        code_submitted=request.form['code'],
        succeeded=succeeded
    )

    db.session.add(attempt)
    db.session.commit()

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
            # Easy Challenges
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

            # Medium Challenges
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
            },
            {
                'id': 4,
                'title': 'Fibonacci Sequence',
                'difficulty': 'Medium',
                'task': 'Write a program that generates the Fibonacci sequence up to the Nth term.',
                'test_code': 'Enter the number of terms: ',
                'example_input': '10',
                'expected_output': 'Fibonacci sequence up to 10th term: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34',
                'hints': ['Initialize the first two terms as 0 and 1', 'Use a loop to generate the next terms'],
                'valid_solutions': ["n = int(input('Enter the number of terms: '))\nfib = [0, 1]\nfor i in range(2, n):\n    fib.append(fib[i-1] + fib[i-2])\nprint(f'Fibonacci sequence up to {n}th term: {', '.join(map(str, fib))}')"]
            },

            # Hard Challenges
            {
                'id': 5,
                'title': 'Prime Numbers',
                'difficulty': 'Hard',
                'task': 'Write a program to find all prime numbers up to N.',
                'test_code': 'Enter N: ',
                'example_input': '30',
                'expected_output': 'Prime numbers up to 30: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29',
                'hints': ['Use a loop to check if a number is divisible by any number less than it'],
                'valid_solutions': ["n = int(input('Enter N: '))\nprimes = []\nfor i in range(2, n+1):\n    if all(i % j != 0 for j in range(2, i)):\n        primes.append(i)\nprint(f'Prime numbers up to {n}: {', '.join(map(str, primes))}')"]
            },
            {
                'id': 6,
                'title': 'Palindrome Checker',
                'difficulty': 'Hard',
                'task': 'Write a program to check if a given string is a palindrome.',
                'test_code': 'Enter a string: ',
                'example_input': 'racecar',
                'expected_output': 'racecar is a palindrome.',
                'hints': ['Check if the string is equal to its reverse'],
                'valid_solutions': ["s = input('Enter a string: ')\nif s == s[::-1]:\n    print(f'{s} is a palindrome.')\nelse:\n    print(f'{s} is not a palindrome.')"]
            },
            {
                'id': 7,
                'title': 'Anagram Checker',
                'difficulty': 'Hard',
                'task': 'Write a program to check if two strings are anagrams of each other.',
                'test_code': 'Enter first string: \nEnter second string: ',
                'example_input': 'listen silent',
                'expected_output': 'listen and silent are anagrams.',
                'hints': ['Sort both strings and compare them'],
                'valid_solutions': ["s1 = input('Enter first string: ')\ns2 = input('Enter second string: ')\nif sorted(s1) == sorted(s2):\n    print(f'{s1} and {s2} are anagrams.')\nelse:\n    print(f'{s1} and {s2} are not anagrams.')"]
            },
            {
                'id': 8,
                'title': 'Matrix Multiplication',
                'difficulty': 'Hard',
                'task': 'Write a program to multiply two matrices.',
                'test_code': 'Enter number of rows and columns for matrix A: \nEnter matrix A: \nEnter number of rows and columns for matrix B: \nEnter matrix B: ',
                'example_input': '2 2\n1 2\n3 4\n2 2\n5 6\n7 8',
                'expected_output': 'Product of matrix A and B: \n19 22\n43 50',
                'hints': ['Matrix multiplication requires the number of columns of A to equal the number of rows of B'],
                'valid_solutions': ["rows_a, cols_a = map(int, input('Enter number of rows and columns for matrix A: ').split())\nmatrix_a = [list(map(int, input().split())) for _ in range(rows_a)]\nrows_b, cols_b = map(int, input('Enter number of rows and columns for matrix B: ').split())\nmatrix_b = [list(map(int, input().split())) for _ in range(rows_b)]\nproduct = [[sum(matrix_a[i][k] * matrix_b[k][j] for k in range(cols_a)) for j in range(cols_b)] for i in range(rows_a)]\nprint('Product of matrix A and B:')\nfor row in product:\n    print(' '.join(map(str, row)))"]
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
    if 'user_id' not in session:
        flash('Please login to track your progress', 'warning')
        return redirect(url_for('login'))
    
    challenges = PythonChallenges.get_challenges()
    challenge_id = int(request.args.get('id', 1))
    challenge = next((c for c in challenges if c['id'] == challenge_id), None)

    result = None
    feedback = None
    next_challenge = None
    test_status = None
    solution = None

    if request.method == 'POST':
        user_code = request.form['code']
        action = request.form.get('action')

        if action == "show_solution":
            solution = challenge['valid_solutions'][0]  # Choose which solution to show
        else:
            feedback = PythonChallenges.validate_solution(user_code, challenge)
            succeeded = "Correct!" in feedback
            update_user_progress(session['user_id'], 'python', challenge_id, succeeded)

            if succeeded:
                next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None

    user_progress = None
    if 'user_id' in session:
        user_progress = UserProgress.query.filter_by(
            user_id=session['user_id'],
            challenge_type='python',
            challenge_id=challenge_id
        ).first()

    return render_template('python.html', 
                           challenge=challenge, 
                           result=result, 
                           feedback=feedback, 
                           next_challenge=next_challenge, 
                           test_status=test_status, 
                           total_challenges=len(challenges),  
                           solution=solution, 
                           current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0,
                           user_progress=user_progress)

class MatlabChallenges:
    @staticmethod
    def get_challenges():
        return [
             # Easy level
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
                'difficulty': 'Easy',
                'task': 'Write a MATLAB script that generates the first N numbers of the Fibonacci sequence.',
                'test_code': '6',
                'example_input': '6',
                'expected_output': '0 1 1 2 3 5',
                'hints': ['Use a loop', 'Fibonacci(n) = Fibonacci(n-1) + Fibonacci(n-2)'],
                'valid_solutions': ["n = input('Enter N: ');\nfib = zeros(1,n);\nfib(1) = 0;\nfib(2) = 1;\nfor i = 3:n\nfib(i) = fib(i-1) + fib(i-2);\nend\nfprintf('%d ', fib);"]
            },

            # Medium level
            {
                'id': 3,
                'title': 'Prime Number Check',
                'difficulty': 'Medium',
                'task': 'Write a MATLAB script that checks whether a given number is prime.',
                'test_code': '11',
                'example_input': '11',
                'expected_output': 'Prime number!',
                'hints': ['A prime number is only divisible by 1 and itself.'],
                'valid_solutions': ["n = input('Enter a number: ');\nif all(mod(n,2:n-1) ~= 0)\n    disp('Prime number!');\nelse\n    disp('Not a prime number.');\nend"]
            },
            {
                'id': 4,
                'title': 'Factorial Calculation',
                'difficulty': 'Medium',
                'task': 'Write a MATLAB script that calculates the factorial of a given number.',
                'test_code': '5',
                'example_input': '5',
                'expected_output': 'Factorial = 120',
                'hints': ['Use a loop to calculate the factorial.'],
                'valid_solutions': ["n = input('Enter a number: ');\nfactorial = 1;\nfor i = 1:n\n    factorial = factorial * i;\nend\ndisp(['Factorial = ', num2str(factorial)]);"]
            },

            # Hard level
            {
                'id': 5,
                'title': 'Matrix Multiplication',
                'difficulty': 'Hard',
                'task': 'Write a MATLAB script that multiplies two matrices.',
                'test_code': '3',
                'example_input': '[1 2; 3 4] [5 6; 7 8]',
                'expected_output': '[19 22; 43 50]',
                'hints': ['Use the * operator to multiply matrices.'],
                'valid_solutions': ["A = [1 2; 3 4];\nB = [5 6; 7 8];\nC = A * B;\ndisp(C);"]
            },
            {
                'id': 6,
                'title': 'Bubble Sort',
                'difficulty': 'Hard',
                'task': 'Write a MATLAB script that sorts an array using the bubble sort algorithm.',
                'test_code': '[5 2 9 1 5 6]',
                'example_input': '[5 2 9 1 5 6]',
                'expected_output': '[1 2 5 5 6 9]',
                'hints': ['Bubble sort compares each element with the next and swaps them if they are in the wrong order.'],
                'valid_solutions': ["arr = [5 2 9 1 5 6];\nfor i = 1:length(arr)-1\n    for j = 1:length(arr)-i\n        if arr(j) > arr(j+1)\n            temp = arr(j);\n            arr(j) = arr(j+1);\n            arr(j+1) = temp;\n        end\n    end\nend\ndisp(arr);"]
            },
            {
                'id': 7,
                'title': 'Sudoku Solver',
                'difficulty': 'Hard',
                'task': 'Write a MATLAB script that solves a given 9x9 Sudoku puzzle.',
                'test_code': '0',
                'example_input': '0 0 3 8 0 0 0 0 0\n6 0 0 0 0 0 4 0 0\n0 0 0 0 0 0 0 0 0\n5 0 0 0 0 0 3 0 0\n0 9 0 0 0 0 0 1 0\n0 0 7 0 0 0 0 0 6\n0 0 0 0 0 0 0 0 0\n0 0 0 0 0 6 0 0\n0 5 0 9 0 0 0 0 7',
                'expected_output': 'Solved Sudoku puzzle',
                'hints': ['Use a backtracking algorithm to solve the puzzle.'],
                'valid_solutions': ["function sudoku_solver(board)\n    % Backtracking solver function\n    % Implement logic here to solve the Sudoku\nend"]
            },
            {
                'id': 8,
                'title': 'Quicksort Algorithm',
                'difficulty': 'Hard',
                'task': 'Write a MATLAB script that sorts an array using the quicksort algorithm.',
                'test_code': '[5 2 9 1 5 6]',
                'example_input': '[5 2 9 1 5 6]',
                'expected_output': '[1 2 5 5 6 9]',
                'hints': ['Choose a pivot element and partition the array into two sub-arrays.'],
                'valid_solutions': ["arr = [5 2 9 1 5 6];\nfunction quicksort(arr)\n    if length(arr) <= 1\n        return;\n    end\n    pivot = arr(1);\n    left = arr(arr < pivot);\n    right = arr(arr > pivot);\n    quicksort(left);\n    quicksort(right);\nend\ndisp(quicksort(arr));"]
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
    solution = None

    if request.method == 'POST':
        user_code = request.form['code']

        action = request.form.get('action')

        if action == "show_solution":
            solution = challenge['valid_solutions'][0]  # Choose which solution to show
        else:
            feedback = MatlabChallenges.validate_solution(user_code, challenge)

        if "Correct!" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None

    return render_template('matlab.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), solution=solution, current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

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
            },
            {
                'id': 4,
                'title': 'Delete Data',
                'difficulty': 'Medium',
                'task': 'Write an SQL query to delete the student with id = 1.',
                'test_code': 'DELETE FROM students WHERE id = 1;',
                'example_input': 'DELETE FROM students WHERE id = 1;',
                'expected_output': 'Row with id = 1 deleted.',
                'hints': ['Use the DELETE statement', 'Use the WHERE clause to specify the row to delete'],
                'valid_solutions': ["DELETE FROM students WHERE id = 1;"]
            },
            {
                'id': 5,
                'title': 'Count Records',
                'difficulty': 'Medium',
                'task': 'Write an SQL query to count how many students are there in the `students` table.',
                'test_code': 'SELECT COUNT(*) FROM students;',
                'example_input': 'SELECT COUNT(*) FROM students;',
                'expected_output': '1',
                'hints': ['Use the COUNT() function'],
                'valid_solutions': ["SELECT COUNT(*) FROM students;"]
            },
            {
                'id': 6,
                'title': 'Join Tables',
                'difficulty': 'Hard',
                'task': 'Write an SQL query to join the `students` table with a `courses` table to get the student name and course name where the student id matches the course enrollment.',
                'test_code': 'SELECT students.name, courses.course_name FROM students JOIN courses ON students.id = courses.student_id;',
                'example_input': 'SELECT students.name, courses.course_name FROM students JOIN courses ON students.id = courses.student_id;',
                'expected_output': 'John Doe | Math',
                'hints': ['Use the JOIN clause to combine data from two tables', 'Ensure matching column names are used'],
                'valid_solutions': ["SELECT students.name, courses.course_name FROM students JOIN courses ON students.id = courses.student_id;"]
            },
            {
                'id': 7,
                'title': 'Group By and Aggregate Functions',
                'difficulty': 'Hard',
                'task': 'Write an SQL query to find the average age of students in each course.',
                'test_code': 'SELECT courses.course_name, AVG(students.age) FROM students JOIN courses ON students.id = courses.student_id GROUP BY courses.course_name;',
                'example_input': 'SELECT courses.course_name, AVG(students.age) FROM students JOIN courses ON students.id = courses.student_id GROUP BY courses.course_name;',
                'expected_output': 'Math | 26',
                'hints': ['Use the GROUP BY clause', 'Use the AVG() function to calculate the average'],
                'valid_solutions': ["SELECT courses.course_name, AVG(students.age) FROM students JOIN courses ON students.id = courses.student_id GROUP BY courses.course_name;"]
            },
            {
                'id': 8,
                'title': 'Subquery',
                'difficulty': 'Very Hard',
                'task': 'Write an SQL query to find the students who have an age greater than the average age of all students.',
                'test_code': 'SELECT name FROM students WHERE age > (SELECT AVG(age) FROM students);',
                'example_input': 'SELECT name FROM students WHERE age > (SELECT AVG(age) FROM students);',
                'expected_output': 'John Doe',
                'hints': ['Use a subquery to calculate the average age', 'Use the comparison operator in the WHERE clause'],
                'valid_solutions': ["SELECT name FROM students WHERE age > (SELECT AVG(age) FROM students);"]
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
    solution = None

    if request.method == 'POST':
        user_code = request.form['code']

        action = request.form.get('action')

        if action == "show_solution":
            solution = challenge['valid_solutions'][0]  # Choose which solution to show
        else:
            feedback = SQLChallenges.validate_solution(user_code, challenge)

        if "created and data inserted" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None

    return render_template('sql.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), solution=solution, current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

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
            },
            {
                'id': 3,
                'title': 'Even or Odd',
                'difficulty': 'Easy',
                'task': 'Write a program that checks whether a number is even or odd.',
                'test_code': 'Enter a number: ',
                'example_input': '7',
                'expected_output': '7 is Odd',
                'hints': ['Use modulus operator (%) to check even/odd'],
                'valid_solutions': [
                    """#include <stdio.h>
                    int main() {
                        int num;
                        printf("Enter a number: ");
                        scanf("%d", &num);
                        if (num % 2 == 0) {
                            printf("%d is Even", num);
                        } else {
                            printf("%d is Odd", num);
                        }
                        return 0;
                    }"""
                ]
            },
            {
                'id': 4,
                'title': 'Factorial Calculator',
                'difficulty': 'Medium',
                'task': 'Write a program that calculates the factorial of a number.',
                'test_code': 'Enter a number: ',
                'example_input': '5',
                'expected_output': 'Factorial of 5 is 120',
                'hints': ['Use a loop or recursion to calculate factorial'],
                'valid_solutions': [
                    """#include <stdio.h>
                    int main() {
                        int num, factorial = 1;
                        printf("Enter a number: ");
                        scanf("%d", &num);
                        for (int i = 1; i <= num; i++) {
                            factorial *= i;
                        }
                        printf("Factorial of %d is %d", num, factorial);
                        return 0;
                    }"""
                ]
            },
            {
                'id': 5,
                'title': 'Prime Number Checker',
                'difficulty': 'Medium',
                'task': 'Write a program that checks if a number is prime.',
                'test_code': 'Enter a number: ',
                'example_input': '11',
                'expected_output': '11 is a Prime number',
                'hints': ['A prime number is only divisible by 1 and itself'],
                'valid_solutions': [
                    """#include <stdio.h>
                    int main() {
                        int num, is_prime = 1;
                        printf("Enter a number: ");
                        scanf("%d", &num);
                        for (int i = 2; i <= num/2; i++) {
                            if (num % i == 0) {
                                is_prime = 0;
                                break;
                            }
                        }
                        if (is_prime) {
                            printf("%d is a Prime number", num);
                        } else {
                            printf("%d is not a Prime number", num);
                        }
                        return 0;
                    }"""
                ]
            },
            {
                'id': 6,
                'title': 'Fibonacci Series',
                'difficulty': 'Hard',
                'task': 'Write a program that generates the Fibonacci sequence up to a certain number.',
                'test_code': 'Enter the number of terms: ',
                'example_input': '6',
                'expected_output': 'Fibonacci Series: 0 1 1 2 3 5',
                'hints': ['The next number in the Fibonacci sequence is the sum of the previous two numbers'],
                'valid_solutions': [
                    """#include <stdio.h>
                    int main() {
                        int num, t1 = 0, t2 = 1, next_term;
                        printf("Enter the number of terms: ");
                        scanf("%d", &num);
                        printf("Fibonacci Series: ");
                        for (int i = 1; i <= num; ++i) {
                            if (i == 1) {
                                printf("%d ", t1);
                                continue;
                            }
                            if (i == 2) {
                                printf("%d ", t2);
                                continue;
                            }
                            next_term = t1 + t2;
                            t1 = t2;
                            t2 = next_term;
                            printf("%d ", next_term);
                        }
                        return 0;
                    }"""
                ]
            },
            {
                'id': 7,
                'title': 'Reverse a String',
                'difficulty': 'Hard',
                'task': 'Write a program that reverses a string.',
                'test_code': 'Enter a string: ',
                'example_input': 'hello',
                'expected_output': 'olleh',
                'hints': ['Use a loop to reverse the string'],
                'valid_solutions': [
                    """#include <stdio.h>
                    #include <string.h>
                    int main() {
                        char str[100];
                        printf("Enter a string: ");
                        scanf("%s", str);
                        int length = strlen(str);
                        printf("Reversed string: ");
                        for (int i = length - 1; i >= 0; i--) {
                            printf("%c", str[i]);
                        }
                        return 0;
                    }"""
                ]
            },
            {
                'id': 8,
                'title': 'Palindrome Checker',
                'difficulty': 'Hard',
                'task': 'Write a program that checks if a string is a palindrome.',
                'test_code': 'Enter a string: ',
                'example_input': 'madam',
                'expected_output': 'madam is a palindrome',
                'hints': ['A palindrome is a word, phrase, or sequence that reads the same backwards'],
                'valid_solutions': [
                    """#include <stdio.h>
                    #include <string.h>
                    int main() {
                        char str[100], reversed[100];
                        printf("Enter a string: ");
                        scanf("%s", str);
                        strcpy(reversed, str);
                        strrev(reversed);
                        if (strcmp(str, reversed) == 0) {
                            printf("%s is a palindrome", str);
                        } else {
                            printf("%s is not a palindrome", str);
                        }
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
    solution = None

    if request.method == 'POST':
        user_code = request.form['code']

        action = request.form.get('action')
        if action == "show_solution":
            solution = challenge['valid_solutions'][0] 
        else:
            feedback = CChallenges.validate_solution(user_code, challenge)
        
        if "Correct!" in feedback:
            next_challenge = challenge_id + 1 if challenge_id < len(challenges) else None
            test_status = 'Passed'  
        else:
            test_status = 'Failed'

    return render_template('c.html', challenge=challenge, result=result, feedback=feedback, next_challenge=next_challenge, test_status=test_status, total_challenges=len(challenges), solution=solution, current_hint_index=request.form.get('current_hint_index', 0) if request.method == 'POST' else 0)

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        flash('Please login to view your progress', 'danger')
        return redirect(url_for('login'))


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized successfully")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
