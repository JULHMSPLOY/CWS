# CodeTrek18
CodeTrek18 เป็นเว็บไซต์ฝึกเขียนโปรแกรมที่ออกแบบมาให้ทุกคนสามารถพัฒนาทักษะการเขียนโปรแกรมได้ โดยมี 4 ภาษาให้เลือกฝึก คือ Python, Matlab, SQL และ C โดยสามารถเลือกโจทย์ในการฝึกเขียนโปรแกรมได้ตามความต้องการ ตั้งแต่ระดับพื้นฐานจนถึงระดับที่มีความท้าทายมากขึ้น!!
# Project Setup
โปรเจกต์นี้ใช้ Flask สำหรับการพัฒนาเว็บแอปพลิเคชัน, SQLAIchemy สำหรับการจัดการฐานข้อมูล และ Bootstrap (CSS Framework) สำหรับการออกแบบหน้าตาเว็บแอปพลิเคชัน รวมถึงยังมีการใช้ Flask สำหรับการจัดการในการยืนยันตัวตน (Authentication) และข้อมูลของผู้ใช้ (Profile) อีกด้วย โดยสามารถติดตั้ง Libraries ที่จำเป็น ดังต่อไปนี้

```sh 
pip install flask flask_sqlalchemy flask_bootstrap werkzeug bcrypt
```
นอกจากนี้ ยังมีการใช้ Werkzenug สำหรับการเข้ารหัสผ่าน, bcrypt สำหรับการแปลงข้อมูล (Hashing) รหัสผ่าน, subprocess สำหรับการรันโปรแกรมของผู้ใช้และตรวจสอบผลลัพธ์ และ jinja2 สำหรับแสดงผล HTML templates 

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
