# CodeTrek18
CodeTrek18 เป็นเว็บแอปพลิเคชันสำหรับฝึกเขียนโปรแกรมที่ออกแบบมาให้ทุกคนสามารถพัฒนาทักษะการเขียนโปรแกรมได้ โดยมี 4 ภาษาให้เลือกฝึก คือ Python, Matlab, SQL และ C โดยสามารถเลือกโจทย์ในการฝึกเขียนโปรแกรมได้ตามความต้องการ ตั้งแต่ระดับพื้นฐานจนถึงระดับที่มีความท้าทายมากขึ้น!!
# Progamming Language
- Python (Flask): สำหรับเขียนฝั่งเซิร์ฟเวอร์ที่จัดการกับข้อมูล และสร้างลอจิกที่เกี่ยวข้องกับการทำงานของเว็บแอปพลิเคชัน
- JavaScript (HTML): สำหรับใช้ในฝั่งผู้ใช้ (frontend) เพื่อจัดการกับ UI และการโต้ตอบกับผู้ใช้ รวมถึงการทำงานร่วมกับเซิร์ฟเวอร์ผ่าน API
# Libraries
โปรเจกต์นี้มีการใช้ Libraries จำนวน 8 ตัว ดังต่อไปนี้
- Flask สำหรับการพัฒนาเว็บแอปพลิเคชัน และการจัดการในการยืนยันตัวตน (Authentication) และข้อมูลของผู้ใช้ (Profile) ด้วย
- datetime สำหรับการจัดการกับวันที่และเวลา
- SQLAIchemy สำหรับการจัดการฐานข้อมูล
- Bootstrap เป็น CSS Framework สำหรับการออกแบบหน้าตาเว็บแอปพลิเคชัน
- Werkzenug สำหรับการเข้ารหัสผ่าน
- subprocess สำหรับการเรียกใช้งานคำสั่งจากภายนอก
- sqlite3 สำหรับการเชื่อมต่อและจัดการฐานข้อมูล SQLite โดยตรง
- os สำหรับการจัดการกับระบบไฟล์
# Features
- ผู้ใช้สามารถลงทะเบียนและเข้าสู่ระบบได้
- การจัดการโปรไฟล์ผู้ใช้ โดยมีชื่อจริง นามสกุล อีเมล ทักษะ และภาพโปรไฟล์
- มีโจทย์สำหรับการฝึเขียนโปรแกรมในภาษา Python, MATLAB, SQL, และ C
- โจทย์จะแบ่งออกเป็นระดับง่าย ปานกลางและยาก
# Directory Structure

```sh
/project-root
├── /instence
│   ├── test.db                  # ไฟล์ฐานข้อมูล SQLite
├── /requirements.txt            # รายการของไลบรารี Python ที่จำเป็น (Flask, Flask-SQLAlchemy, Flask-Bootstrap, etc.)
├── /static
│   ├── /profile_pics            # โฟลเดอร์สำหรับเก็บภาพโปรไฟล์ที่ผู้ใช้อัปโหลด
│   ├── style.css                # ไฟล์ CSS สำหรับการออกแบบของแอปพลิเคชัน
│   ├── style1.css               # ไฟล์ CSS อื่น ๆ สำหรับการออกแบบที่อาจจะใช้ในการจัดรูปแบบเพิ่มเติม
│   ├── style2.css 
├── /templates
│   ├── c.html                   # หน้าให้ฝึกเขียนโค้ด C
│   ├── choose_challenge.html    # หน้าเลือกโจทย์ฝึก
│   ├── index.html               # หน้าแรกของแอป
│   ├── login.html               # หน้าให้ผู้ใช้เข้าสู่ระบบ
│   ├── matlab.html              # หน้าให้ฝึกเขียนโค้ด MATLAB
│   ├── profile.html             # หน้าโปรไฟล์ของผู้ใช้
│   ├── progress.html            # หน้าแสดงผลการฝึกหรือความคืบหน้าของผู้ใช้ในการฝึก
│   ├── python.html              # หน้าให้ฝึกเขียนโค้ด Python
│   ├── signup.html              # หน้าให้ผู้ใช้ลงทะเบียน
│   ├── sql.html                 # หน้าให้ฝึกเขียนโค้ด SQL
├── /app.py                      # ไฟล์แอปพลิเคชันหลักของ Flask
├── /README.md                   # เอกสารโปรเจค
├── /LICENSE.md                  # เอกสารเกี่ยวกับสิทธิ์การใช้งานโปรเจค
```

# Setup

- ติดตั้ง Libraries โดยใช้คำสั่งด้านล่างนี้ใน terminal หรือ command prompt
```sh 
pip install flask flask_sqlalchemy flask_bootstrap werkzeug bcrypt
```

# Usage 
- สร้างเว็บแอปพลิเคชัน Flask

```sh 
from flask import Flask
app = Flask(__name__)
```

- ตั้งค่า Flask app โดยใช้ไฟล์ app.config

```sh 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  
app.config['SECRET_KEY'] = 'your_secret_key'  
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'  
app.config['ALLOWED_EXTENSIONS'] ={'png', 'jpg', 'jpeg', 'gif'} 
```

- ใช้ SQLAlchemy เพื่อเชื่อมต่อกับฐานข้อมูล SQLite

```sh 
db = SQLAlchemy(app)
```

- สามารถสร้างและจัดการโมเดล User ที่เก็บข้อมูลผู้ใช้ได้ เช่น ชื่อ, อีเมล, รหัสผ่าน, และข้อมูลโปรไฟล์อื่นๆ

```sh 
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
```

- ในฟังก์ชัน register() จะมีการตรวจสอบว่า username กับ email ซ้ำกันหรือไม่ โดยใช้ generate_password_hash จาก werkzeug ในการเข้ารหัสผ่านก่อนที่จะเก็บในฐานข้อมูล

```sh
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
new_user = User(username=username, email=email, password=hashed_password)
```

- ในฟังก์ชัน register() จะตรวจสอบรหัสผ่านที่กรอกเข้ามาว่าตรงกับรหัสผ่านที่เก็บในฐานข้อมูลหรือไม่ โดยใช้ฟังก์ชัน check_password() ที่ใช้ werkzeug ในการตรวจสอบรหัสผ่านที่ป้อนเข้ามาว่าตรงกับรหัสผ่านที่เก็บไว้ในฐานข้อมูลหรือไม่

```sh
def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)
```

- ในฟังก์ชัน profile() ผู้ใช้สามารถอัพโหลดรูปภาพโปรไฟล์ได้ และใช้ secure_filename จาก werkzeug สำหรับทำให้ชื่อไฟล์ที่อัพโหลดมีความปลอดภัยและไม่ทำให้เกิดปัญหากับระบบไฟล์

```sh
if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    user.profile_picture = filename
```

- ทดสอบโค้ดโดยการใช้ subprocess เพื่อเรียกใช้งานคำสั่ง Python และ MATLAB สำหรับทดสอบคำตอบในคำถามการเขียนโค้ด

```sh
process = subprocess.run(['python3', '-c', user_code], input=input_data, text=True, capture_output=True, timeout=5)
    result = process.stdout.strip()
```

- ใช้ session เพื่อจัดการการเข้าสู่ระบบของผู้ใช้ โดยตัวแปร session จะเก็บข้อมูลที่สำคัญ เช่น การตรวจสอบว่า user เป็นคนที่ล็อกอินเข้ามาหรือไม่

```sh
session['user_id'] = user.id
```

- ใช้ Bootstrap ออกแบบ UI ในแอปพลิเคชันด้วยการใช้ Bootstrap framework เพื่อทำให้หน้าเว็บดูดีและตอบสนองได้

```sh
def home():
    return render_template('index.html')
```
```sh
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
```

# Getting Started 
- Clone the repository

```sh
git clone https://github.com/JULHMSPLOY/CWS.git
```

- Install dependencies

```sh
pip install -r requirements.txt
```

- Run the application

```sh
flask run
```

Open your browser and go to <http://127.0.0.1:5000>
# Database Setup (If needed)
If the database (users.db) is not created yet, run the following

```sh
python init_db.py
```

This will initialize the SQLite database.
# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
