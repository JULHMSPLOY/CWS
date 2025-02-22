# CodeTrek18
CodeTrek18 เป็นเว็บไซต์ฝึกเขียนโปรแกรมที่ออกแบบมาให้ทุกคนสามารถพัฒนาทักษะการเขียนโปรแกรมได้ โดยมี 4 ภาษาให้เลือกฝึก คือ Python, Matlab, SQL และ C โดยสามารถเลือกโจทย์ในการฝึกเขียนโปรแกรมได้ตามความต้องการ ตั้งแต่ระดับพื้นฐานจนถึงระดับที่มีความท้าทายมากขึ้น!!
# Project Setup
โปรเจกต์นี้มีการใช้ Libraries จำนวน 5 ตัว ดังต่อไปนี้
- Flask สำหรับการพัฒนาเว็บแอปพลิเคชัน และการจัดการในการยืนยันตัวตน (Authentication) และข้อมูลของผู้ใช้ (Profile) ด้วย
- SQLAIchemy สำหรับการจัดการฐานข้อมูล
- Bootstrap (CSS Framework) สำหรับการออกแบบหน้าตาเว็บแอปพลิเคชัน
- Werkzenug สำหรับการเข้ารหัสผ่าน
- bcrypt สำหรับการแปลงข้อมูล (Hashing) รหัสผ่าน
- subprocess สำหรับการรันโปรแกรมของผู้ใช้และตรวจสอบผลลัพธ์
- jinja2 สำหรับแสดงผล HTML templates 
โดยสามารถติดตั้ง Libraries ทั้งหมดนี้ได้ โดยใช้คำสั่งดังด้านล่างใน terminal หรือ command prompt

```sh 
pip install flask flask_sqlalchemy flask_bootstrap werkzeug bcrypt
```

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
