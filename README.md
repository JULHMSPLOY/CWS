# CodeTrek18
CodeTrek18 เป็นเว็บไซต์ฝึกเขียนโปรแกรมที่ออกแบบมาให้ทุกคนสามารถพัฒนาทักษะการเขียนโปรแกรมได้ โดยมี 4 ภาษาให้เลือกฝึก คือ Python, Matlab, SQL และ C โดยสามารถเลือกโจทย์ในการฝึกเขียนโปรแกรมได้ตามความต้องการ ตั้งแต่ระดับพื้นฐานจนถึงระดับที่มีความท้าทายมากขึ้น!!
# Progamming Language
- Python (Flask): สำหรับเขียนฝั่งเซิร์ฟเวอร์ที่จัดการกับข้อมูล และสร้างลอจิกที่เกี่ยวข้องกับการทำงานของเว็บแอปพลิเคชัน
- JavaScript (HTML): สำหรับใช้ในฝั่งผู้ใช้ (frontend) เพื่อจัดการกับ UI และการโต้ตอบกับผู้ใช้ รวมถึงการทำงานร่วมกับเซิร์ฟเวอร์ผ่าน API
# Libraries
โปรเจกต์นี้มีการใช้ Libraries จำนวน 5 ตัว ดังต่อไปนี้
- Flask สำหรับการพัฒนาเว็บแอปพลิเคชัน และการจัดการในการยืนยันตัวตน (Authentication) และข้อมูลของผู้ใช้ (Profile) ด้วย
- SQLAIchemy สำหรับการจัดการฐานข้อมูล
- Bootstrap เป็น CSS Framework สำหรับการออกแบบหน้าตาเว็บแอปพลิเคชัน
- Werkzenug สำหรับการเข้ารหัสผ่าน
- bcrypt สำหรับแปลงข้อมูล เป็นการ Hashing รหัสผ่าน
- subprocess สำหรับการรันโปรแกรมของผู้ใช้และตรวจสอบผลลัพธ์
- jinja2 สำหรับแสดงผล HTML templates
# How to use  
- ติดตั้ง Libraries โดยใช้คำสั่งด้านล่างนี้ใน terminal หรือ command prompt

```sh 
pip install flask flask_sqlalchemy flask_bootstrap werkzeug bcrypt
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
# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
