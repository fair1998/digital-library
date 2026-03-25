# AI Context - Digital Library System

เอกสารนี้ใช้เพื่อให้บายภาพรวมระบบ พฤติกรรมของระบบ หน้าเว็บ บทบาทของผู้ใช้ กฎธุรกิจ และความสัมพันธ์กับฐานข้อมูล
ให้ AI ใช้เอกสารนี้ร่วมกับ `data-dictionary.md` และ `plan.md` ก่อนสร้างหรือแก้ไขโค้ด

---

## 📊 Project Status (Updated: March 25, 2026)

### ✅ Completed Phases

- **Phase 0**: Project Setup - โครงสร้างพื้นฐานพร้อมใช้งาน
- **Phase 1**: Data Model Foundation - Models หนังสือครบถ้วน (Author, Category, Publisher, Book)
- **Phase 2**: Admin Foundation - Django Admin พร้อมจัดการข้อมูลหนังสือ

### 🚧 Current Phase

- **Phase 3**: Reservation System Data Layer (Next)

### 📋 Remaining Phases

- Phase 4-11: Reservation Admin, Loans, Fines, Member Pages, Testing, Documentation

---

## 1. System Overview

## System Name

Digital Library System

## System Type

ระบบจัดการห้องสมุดดิจิทัลสำหรับการจัดการข้อมูลหนังสือ การจอง การยืมคืน และค่าปรับ

## Main Purpose

- เก็บข้อมูลหนังสือในห้องสมุด
- ให้สมาชิกค้นหาและจองหนังสือ
- ให้ผู้ดูแลระบบจัดการคำขอจอง
- ให้ผู้ดูแลระบบบันทึกการยืมและคืน
- ให้ผู้ดูแลระบบจัดการค่าปรับจากการคืนช้า ทำหาย หรือชำรุด

## Design Direction

ระบบนี้ตีความเป็น “ระบบจัดการห้องสมุด” มากกว่าระบบอ่าน e-book
ดังนั้นแกนหลักของระบบคือ inventory + reservation + loan + fine

---

## 2. Main Modules

- Authentication / Users
- Books Management
- Authors Management
- Categories Management
- Publishers Management
- Reservations
- Loans
- Fines
- Admin Management

---

## 3. User Roles

## 3.1 Member

สมาชิกทั่วไป

หน้าที่หลัก:

- ดูข้อมูลหนังสือ
- ค้นหาหนังสือ
- จองหนังสือ
- ดูประวัติการจองของตัวเอง
- ดูประวัติการยืมของตัวเอง
- ดูค่าปรับของตัวเอง

## 3.2 Admin

ผู้ดูแลระบบ

หน้าที่หลัก:

- จัดการข้อมูลหนังสือ
- จัดการผู้แต่ง หมวดหมู่ สำนักพิมพ์
- ตรวจสอบและยืนยันการจอง
- ยกเลิกการจอง
- บันทึกการยืม
- บันทึกการคืน
- บันทึกกรณีหายหรือชำรุด
- จัดการค่าปรับ
- ดูข้อมูลสมาชิก

---

## 4. Database Summary

ระบบใช้ตารางหลักดังนี้

### Users

- users

### Books Domain

- books
- authors
- publishers
- categories
- book_authors
- book_categories

### Reservation Domain

- reservation_batches
- reservations

### Loan Domain

- loan_batches
- loan_items

### Fine Domain

- fines

หมายเหตุ:
ให้ยึดรายละเอียด field และ constraint ตาม `docs/data-dictionary.md`

---

## 5. Core Concepts

## 5.1 Book

หนังสือ 1 รายการในระบบ มีข้อมูลหลัก เช่น ชื่อ รายละเอียด รูปปก ปีพิมพ์ สำนักพิมพ์ จำนวนทั้งหมด และจำนวนที่พร้อมให้ยืม/จอง

## 5.2 Reservation Batch

การจอง 1 ครั้งของผู้ใช้ 1 คน
ในการจอง 1 ครั้ง สามารถมีหนังสือหลายเล่มได้
ดังนั้นจึงแยกเป็น:

- reservation_batches = หัวรายการจอง
- reservations = รายการหนังสือแต่ละเล่มในชุดจอง

## 5.3 Loan Batch

การยืม 1 ครั้งของผู้ใช้ 1 คน
การยืม 1 ครั้ง อาจมีหลายเล่ม
ดังนั้นจึงแยกเป็น:

- loan_batches = หัวรายการยืม
- loan_items = รายการหนังสือแต่ละเล่มที่ถูกยืม

## 5.4 Fine

ค่าปรับที่เกิดจาก loan_item ใด loan_item หนึ่ง
เช่น คืนช้า ทำหาย หรือชำรุด

---

## 6. Main Business Rules

## 6.1 Book Quantity Rules

- `total_quantity` คือจำนวนหนังสือทั้งหมด
- `available_quantity` คือจำนวนที่ยังพร้อมให้ยืมหรือจอง
- ค่า `available_quantity` ต้องไม่ติดลบ
- ค่า `available_quantity` ต้องไม่มากกว่า `total_quantity` ในบริบทปกติ

## 6.2 Reservation Rules

- สมาชิกจองหนังสือได้เมื่อ `available_quantity > 0`
- การจอง 1 ครั้งสามารถมีหลายเล่มได้
- สถานะ reservation batch มี:
  - pending
  - confirmed
  - cancelled
- สถานะ reservation item มี:
  - pending
  - confirmed
  - cancelled
- เมื่อ admin ยืนยันการจอง ระบบต้องอัปเดตสถานะให้สอดคล้องทั้ง batch และ item
- การจองมีวันหมดอายุ (`expires_at`)

## 6.3 Loan Rules

- การยืม 1 ครั้งสามารถมีหลายเล่มได้
- loan item แต่ละรายการมีสถานะ:
  - borrowed
  - returned
  - lost
- loan item อาจอ้างอิง reservation เดิมได้ หากยืมมาจากการจอง
- เมื่อคืนหนังสือ ต้องบันทึก `returned_at`
- หนังสือที่หายจะไม่ถูกเพิ่มกลับเข้า available_quantity

## 6.4 Fine Rules

- fine เกิดจาก loan_item
- fine type มี:
  - late_return
  - lost
  - damaged
- fine status มี:
  - unpaid
  - paid
- เมื่อจ่ายแล้ว ต้องบันทึก `paid_at`

## 6.5 Permission Rules

- member ห้ามเข้าหน้า admin
- member เห็นได้เฉพาะข้อมูลของตัวเองในหน้า my reservations / my loans / my fines
- admin เห็นข้อมูลทุกคนได้
- admin เท่านั้นที่ยืนยันการจองหรือบันทึกการยืมคืนได้

---

## 7. Member Pages

ด้านล่างคือหน้าหลักฝั่งผู้ใช้ทั่วไป

## 7.1 Home Page

### URL

`/`

### Purpose

แสดงหน้าแรกของระบบ และเป็นจุดเริ่มต้นไปยังรายการหนังสือหรือฟังก์ชันหลัก

### Member Can Do

- ดูข้อความต้อนรับ
- ไปหน้ารายการหนังสือ
- ค้นหาหนังสือ
- ดูหนังสือแนะนำหรือหนังสือใหม่

### Related Data

- books

---

## 7.2 Book List Page

### URL

`/books`

### Purpose

แสดงรายการหนังสือทั้งหมดในระบบ

### Member Can Do

- ดูรายการหนังสือ
- ค้นหาตามชื่อ
- กรองตามหมวดหมู่
- กรองตามสำนักพิมพ์
- ไปหน้ารายละเอียดหนังสือ
- ดูสถานะว่ามีหนังสือให้จองหรือไม่

### Related Data

- books
- categories
- book_categories
- publishers

### Important UI Information

ควรแสดงอย่างน้อย:

- รูปปก
- ชื่อหนังสือ
- สำนักพิมพ์
- ปีพิมพ์
- จำนวนคงเหลือ
- ปุ่มดูรายละเอียด

---

## 7.3 Book Detail Page

### URL

`/books/<id>`

### Purpose

แสดงข้อมูลหนังสือแบบละเอียด

### Member Can Do

- ดูชื่อหนังสือ
- ดูคำอธิบาย
- ดูรูปปก
- ดูผู้แต่ง
- ดูหมวดหมู่
- ดูสำนักพิมพ์
- ดูจำนวนทั้งหมด
- ดูจำนวนที่พร้อมให้ยืมหรือจอง
- กดจองหนังสือ

### Related Data

- books
- authors
- book_authors
- categories
- book_categories
- publishers

### Important Rules

- ถ้า available_quantity <= 0 ต้องไม่ให้จอง
- ถ้ายังไม่ได้ login อาจบังคับ login ก่อนจอง

---

## 7.4 My Reservations Page

### URL

`/my-reservations`

### Purpose

ให้สมาชิกดูประวัติการจองของตัวเอง

### Member Can Do

- ดูรายการจองทั้งหมดของตัวเอง
- ดูสถานะของ batch
- ดูรายการหนังสือในแต่ละ batch
- ดูวันหมดอายุของการจอง

### Related Data

- reservation_batches
- reservations
- books

### Important Information

ควรแสดง:

- เลข batch หรือรหัสรายการ
- วันที่จอง
- expires_at
- status
- รายการหนังสือใน batch

---

## 7.5 My Loans Page

### URL

`/my-loans`

### Purpose

ให้สมาชิกดูประวัติการยืมของตัวเอง

### Member Can Do

- ดูรายการยืมปัจจุบัน
- ดูประวัติการยืมเก่า
- ดู due_date
- ดูสถานะ borrowed / returned / lost

### Related Data

- loan_batches
- loan_items
- books

---

## 7.6 My Fines Page

### URL

`/my-fines`

### Purpose

ให้สมาชิกดูค่าปรับของตัวเอง

### Member Can Do

- ดูรายการค่าปรับ
- ดูประเภทค่าปรับ
- ดูจำนวนเงิน
- ดูสถานะการชำระ
- ดูเหตุผลเพิ่มเติม

### Related Data

- fines
- loan_items
- loan_batches
- books

---

## 8. Admin Pages

ในระยะแรก admin หลักของระบบอาจอิงบน Django Admin
แต่ด้านล่างนี้คือ logical pages / admin modules ที่ระบบควรรองรับ

## 8.1 Admin Dashboard

### URL

`/admin/`

### Purpose

แสดงภาพรวมของระบบ

### Admin Can See

- จำนวนหนังสือทั้งหมด
- จำนวนหนังสือที่พร้อมให้ยืมหรือจอง
- จำนวนการจองที่ pending
- จำนวนหนังสือที่กำลังถูกยืม
- จำนวนค่าปรับที่ unpaid

### Related Data

- books
- reservation_batches
- reservations
- loan_items
- fines

---

## 8.2 Book Management

### URL

`/admin/books/book/` หรือ custom page ในอนาคต

### Purpose

จัดการข้อมูลหนังสือ

### Admin Can Do

- เพิ่มหนังสือ
- แก้ไขหนังสือ
- ลบหนังสือ
- อัปโหลดรูปปก
- กำหนดสำนักพิมพ์
- กำหนดผู้แต่ง
- กำหนดหมวดหมู่
- แก้จำนวน total_quantity
- แก้จำนวน available_quantity อย่างระมัดระวัง

### Related Data

- books
- publishers
- authors
- categories
- book_authors
- book_categories

### Important Rules

- ควรระวังการแก้ available_quantity ตรง ๆ ถ้ามี transaction ค้างอยู่
- ถ้าระบบโตขึ้น ควรใช้ service layer สำหรับปรับ stock

---

## 8.3 Author Management

### Purpose

จัดการข้อมูลผู้แต่ง

### Admin Can Do

- เพิ่มผู้แต่ง
- แก้ไขผู้แต่ง
- ลบผู้แต่ง

### Related Data

- authors
- book_authors

---

## 8.4 Category Management

### Purpose

จัดการข้อมูลหมวดหมู่

### Admin Can Do

- เพิ่มหมวดหมู่
- แก้ไขหมวดหมู่
- ลบหมวดหมู่

### Related Data

- categories
- book_categories

---

## 8.5 Publisher Management

### Purpose

จัดการข้อมูลสำนักพิมพ์

### Admin Can Do

- เพิ่มสำนักพิมพ์
- แก้ไขสำนักพิมพ์
- ลบสำนักพิมพ์

### Related Data

- publishers
- books

---

## 8.6 Reservation Management

### Purpose

จัดการรายการจอง

### Admin Can Do

- ดูรายการจองทั้งหมด
- ดูว่าใครจองอะไร
- ดูวันหมดอายุของการจอง
- ยืนยันการจอง
- ยกเลิกการจอง

### Related Data

- reservation_batches
- reservations
- users
- books

### Important Rules

- การยืนยันควรเปลี่ยนสถานะทั้ง batch และ item
- การยกเลิกควรเปลี่ยนสถานะทั้ง batch และ item
- การยืนยัน/ยกเลิกต้องสอดคล้องกับจำนวน available_quantity

---

## 8.7 Loan Management

### Purpose

จัดการรายการยืม

### Admin Can Do

- สร้างการยืมใหม่
- เลือก user
- เลือกหนังสือหลายเล่ม
- อ้างอิง reservation เดิมได้ถ้ามี
- กำหนด due_date
- เปลี่ยนสถานะเป็น returned
- เปลี่ยนสถานะเป็น lost

### Related Data

- loan_batches
- loan_items
- users
- books
- reservations

### Important Rules

- ห้ามคืนซ้ำ
- ห้ามเปลี่ยนจาก returned กลับเป็น borrowed แบบไม่มีเหตุผล
- ถ้า lost ไม่ควรคืน stock กลับ

---

## 8.8 Fine Management

### Purpose

จัดการค่าปรับ

### Admin Can Do

- สร้างค่าปรับ
- แก้เหตุผล
- แก้จำนวนเงิน
- เปลี่ยนสถานะ unpaid / paid
- บันทึก paid_at

### Related Data

- fines
- loan_items
- books
- users

---

## 9. Main User Flows

## 9.1 Flow: Browse Books

1. Member เข้าหน้า home หรือ book list
2. ระบบดึงรายการหนังสือ
3. Member ค้นหาหรือกรองหนังสือ
4. Member กดดูรายละเอียดหนังสือ
5. ระบบแสดงข้อมูลแบบละเอียด

---

## 9.2 Flow: Reserve One or More Books

1. Member login เข้าระบบ
2. Member เลือกหนังสือที่ต้องการจอง
3. ระบบตรวจสอบว่า available_quantity ของแต่ละเล่มมากกว่า 0
4. ระบบสร้าง `reservation_batch`
5. ระบบสร้าง `reservations` หลายรายการภายใต้ batch เดียว
6. สถานะเริ่มต้นเป็น `pending`
7. ระบบบันทึก `expires_at`
8. Admin เข้ามาตรวจสอบ
9. ถ้าอนุมัติ:
   - batch status = confirmed
   - item status = confirmed
   - ปรับจำนวน available_quantity ตามนโยบายของระบบ
10. ถ้าไม่อนุมัติ:

- batch status = cancelled
- item status = cancelled

---

## 9.3 Flow: Borrow Books

1. Admin เปิดหน้าจัดการการยืม
2. Admin เลือก user
3. Admin เลือกหนังสือที่จะให้ยืม
4. ถ้ามาจากการจอง สามารถอ้างอิง reservation เดิมได้
5. Admin กำหนด due_date
6. ระบบสร้าง `loan_batch`
7. ระบบสร้าง `loan_items`
8. loan item status เริ่มต้นเป็น `borrowed`

---

## 9.4 Flow: Return Books

1. Admin เปิดรายการ loan
2. Admin เลือก loan item ที่ถูกคืน
3. ระบบตรวจสอบว่ายังไม่ถูกคืนมาก่อน
4. ระบบเปลี่ยน status เป็น `returned`
5. ระบบบันทึก `returned_at`
6. ระบบเพิ่ม available_quantity กลับ
7. ถ้าคืนช้า อาจสร้าง fine ประเภท `late_return`

---

## 9.5 Flow: Mark Book as Lost

1. Admin เปิดรายการ loan item
2. Admin เปลี่ยนสถานะเป็น `lost`
3. ระบบไม่เพิ่ม available_quantity กลับ
4. Admin หรือระบบสร้าง fine ประเภท `lost`

---

## 9.6 Flow: Fine Payment

1. Admin เปิดรายการ fine
2. ตรวจสอบยอดและเหตุผล
3. เมื่อสมาชิกชำระเงิน
4. Admin เปลี่ยน status เป็น `paid`
5. ระบบบันทึก `paid_at`

---

## 10. Data Relationships by Feature

## 10.1 Book Feature

ใช้ตาราง:

- books
- publishers
- authors
- categories
- book_authors
- book_categories

## 10.2 Reservation Feature

ใช้ตาราง:

- reservation_batches
- reservations
- books
- users

## 10.3 Loan Feature

ใช้ตาราง:

- loan_batches
- loan_items
- books
- users
- reservations

## 10.4 Fine Feature

ใช้ตาราง:

- fines
- loan_items
- loan_batches
- books
- users

---

## 11. UI / UX Expectations

## 11.1 General

- ชื่อข้อมูลควรสื่อความหมายตรงกับฐานข้อมูล
- ทุกหน้า list ควรมี search/filter เมื่อเหมาะสม
- ควรแสดงสถานะเป็นคำที่เข้าใจง่าย
- ควรแยกหน้า member กับ admin ชัดเจน

## 11.2 Status Display Recommendations

### Reservation Status

- pending = รอดำเนินการ
- confirmed = ยืนยันแล้ว
- cancelled = ยกเลิก

### Loan Status

- borrowed = กำลังยืม
- returned = คืนแล้ว
- lost = สูญหาย

### Fine Status

- unpaid = ยังไม่ชำระ
- paid = ชำระแล้ว

---

## 12. Technical Direction for AI

AI ควรใช้แนวทางนี้เมื่อสร้างโค้ด

### Models

- ใช้ชื่อ model แบบ singular
- ใช้ choices สำหรับสถานะ
- ใช้ timestamp fields ให้สม่ำเสมอ
- ใช้ `related_name` อย่างมีเหตุผล
- อย่าสร้าง nullable เกินจำเป็น

### Admin

- ทำให้ใช้งานได้จริงก่อนสวย
- list_display ต้องช่วยให้ admin เห็นข้อมูลสำคัญเร็ว
- search_fields ต้องรองรับ field ที่ใช้บ่อย
- list_filter ต้องมี status / publisher / dates ตามความเหมาะสม

### Views / Templates

- ตั้งชื่อให้ตรงกับ feature
- แยก member pages กับ admin pages ชัดเจน
- validation ฝั่ง backend ต้องมีเสมอ แม้มี validation ฝั่ง UI แล้ว

### Business Logic

- อย่าอัปเดต stock แบบสุ่ม
- ทุก action ที่กระทบ available_quantity ต้องชัดว่าทำเมื่อไร
- ถ้าต้องตัดสินใจเรื่อง stock timing ให้เสนอออกมา ไม่เดาเองเงียบ ๆ

---

## 13. Constraints for AI

AI ต้องไม่ทำสิ่งต่อไปนี้โดยไม่ขอหรือไม่แจ้ง

- อย่าสร้างตารางใหม่เองนอกเหนือจาก schema หลัก
- อย่าเปลี่ยนชื่อ field หลักเอง
- อย่าลบ concept ของ batch/item
- อย่ารวม reservations กับ loan_items เป็นตารางเดียว
- อย่ารวม fines เข้า loan_items โดยตรงแบบไม่มี table แยก
- อย่าใส่ logic ที่ขัดกับ data dictionary

---

## 14. Open Decisions / Flexible Areas

จุดที่ AI สามารถเสนอแนวทางได้ แต่ต้องแจ้งก่อน

- จะใช้ explicit through model หรือ ManyToManyField with through สำหรับ authors/categories
- จะใช้ `ImageField` หรือ `image_url`
- จะวาง business logic ใน model methods, services, หรือ admin actions
- จะมี custom admin pages เพิ่มหรือใช้ Django Admin ล้วนใน MVP

---

## 15. Recommended Prompt for AI

Use this system context for implementation:

1. Read:
   - docs/ai-context.md
   - docs/plan.md
   - docs/data-dictionary.md

2. Follow these rules:
   - Treat these files as the source of truth.
   - Implement one phase at a time.
   - Do not invent schema changes silently.
   - Summarize any assumptions before coding when necessary.

3. Current project type:
   - Django-based digital library management system
   - Focus on admin workflow first, member pages second

---

## 16. Current Development Priority

ลำดับความสำคัญปัจจุบันของโปรเจกต์นี้

1. books models
2. books admin
3. reservations models/admin
4. loans models/admin
5. fines models/admin
6. member-facing pages
7. testing and refinement

---

## 17. Definition of Correct Understanding

AI จะถือว่าเข้าใจระบบถูกต้องเมื่อสามารถอธิบายได้ว่า:

- หนังสือ 1 เล่มมีผู้แต่งหลายคนได้
- หนังสือ 1 เล่มมีหลายหมวดหมู่ได้
- การจอง 1 ครั้งมีหลายเล่มผ่าน reservation batch
- การยืม 1 ครั้งมีหลายเล่มผ่าน loan batch
- ค่าปรับผูกกับ loan item
- admin เป็นผู้จัดการธุรกรรมหลักของระบบ
- member เห็นเฉพาะข้อมูลของตัวเอง

---
