# Project Plan - Digital Library System

เอกสารนี้คือแผนการพัฒนาระบบห้องสมุดดิจิทัลแบบละเอียด
ใช้สำหรับกำหนดลำดับการทำงานของโปรเจกต์ และใช้เป็น roadmap ให้ AI ทำงานทีละส่วนอย่างถูกต้อง

---

## 1. Project Goal

สร้างระบบจัดการห้องสมุดดิจิทัลที่รองรับการทำงานหลักดังนี้

- จัดการข้อมูลหนังสือ
- จัดการผู้แต่ง หมวดหมู่ สำนักพิมพ์
- ให้สมาชิกดูรายการหนังสือและจองหนังสือได้
- ให้ผู้ดูแลระบบตรวจสอบ ยืนยัน หรือยกเลิกการจอง
- ให้ผู้ดูแลระบบบันทึกการยืมและคืนหนังสือ
- รองรับค่าปรับกรณีคืนช้า ทำหาย หรือชำรุด
- ใช้ Django เป็น backend และใช้ Django Admin สำหรับงานจัดการระบบในระยะแรก

---

## 2. Project Scope

### In Scope

- Authentication พื้นฐาน
- ระบบจัดการหนังสือ
- ระบบจองหนังสือ
- ระบบยืมคืนหนังสือ
- ระบบค่าปรับ
- Django Admin สำหรับ admin
- Media upload สำหรับรูปปกหนังสือใน local development

### Out of Scope (initial phase)

- Online payment gateway
- Notification ผ่าน email / SMS จริง
- ระบบอ่าน e-book online
- Multi-branch library
- Barcode / RFID integration
- Reporting ขั้นสูงและ dashboard analytics แบบเต็มรูปแบบ

---

## 3. Core Roles

## 3.1 Member

ผู้ใช้งานทั่วไปของระบบ

ทำได้:

- login / logout
- ดูรายการหนังสือ
- ค้นหาหนังสือ
- ดูรายละเอียดหนังสือ
- จองหนังสือ
- ดูประวัติการจองของตัวเอง
- ดูประวัติการยืมของตัวเอง
- ดูค่าปรับของตัวเอง

ทำไม่ได้:

- เข้าหน้า admin
- จัดการข้อมูลหนังสือ
- ยืนยันการจอง
- แก้ไขข้อมูลผู้ใช้อื่น

## 3.2 Admin

ผู้ดูแลระบบ

ทำได้:

- จัดการข้อมูลหนังสือ
- จัดการผู้แต่ง หมวดหมู่ สำนักพิมพ์
- ดูรายการจองทั้งหมด
- ยืนยันหรือยกเลิกการจอง
- บันทึกการยืมหนังสือ
- บันทึกการคืนหนังสือ
- บันทึกหนังสือหายหรือชำรุด
- สร้างและอัปเดตค่าปรับ
- ดูข้อมูลสมาชิก

---

## 4. Reference Documents

เอกสารที่ต้องใช้ร่วมกันเสมอ

- `docs/data-dictionary.md`
- `docs/ai-context.md`
- `docs/plan.md`

กติกา:

- โครงสร้างฐานข้อมูลให้ยึดตาม data dictionary เป็นหลัก
- flow และ permission ให้ยึดตาม ai-context เป็นหลัก
- ลำดับการพัฒนาให้ยึดตาม plan นี้เป็นหลัก

---

## 5. Development Strategy

แนวทางการพัฒนา:

1. ออกแบบข้อมูลให้ชัดก่อน
2. สร้าง models ให้ครบ
3. สร้าง migrations
4. ลงทะเบียน Django admin
5. ทดสอบ CRUD บน admin ก่อน
6. จากนั้นค่อยทำ business logic
7. จากนั้นค่อยทำหน้า member-facing pages
8. สุดท้ายค่อยเพิ่ม validation และ optimization

เหตุผล:

- ลดความเสี่ยงเรื่อง schema เปลี่ยนกลางทาง
- ใช้ Django Admin ช่วยตรวจสอบข้อมูลจริงได้เร็ว
- ทำให้ AI สร้างงานเป็น phase ได้ง่าย

---

## 6. Phase Breakdown

# Phase 0: Project Setup ✅ COMPLETED

## Goal

เตรียมโครงสร้างโปรเจกต์ให้พร้อมสำหรับการพัฒนา

## Tasks

- [x] สร้าง Django project
- [x] สร้าง virtual environment
- [x] ติดตั้ง dependencies พื้นฐาน
- [x] สร้าง requirements.txt
- [x] ตั้งค่า `.gitignore`
- [x] ตั้งค่า database connection
- [x] ตั้งค่า timezone / language
- [x] ตั้งค่า media files สำหรับ development
- [x] สร้าง apps:
  - [x] users
  - [x] books
  - [x] reservations
  - [x] loans
  - [x] fines

## Deliverables

- Django project run ได้
- apps ถูกเพิ่มใน `INSTALLED_APPS`
- database เชื่อมต่อได้
- media file config ใช้งานได้

## Acceptance Criteria

- `python manage.py runserver` ทำงานได้
- `python manage.py makemigrations` ทำงานได้
- `python manage.py migrate` ทำงานได้

## Status: ✅ COMPLETED

---

# Phase 1: Data Model Foundation ✅ COMPLETED

## Goal

สร้างตารางข้อมูลพื้นฐานของระบบหนังสือ

## Scope

- authors
- categories
- publishers
- books
- book_authors
- book_categories

## Tasks

### 1.1 Author Model

- [x] สร้าง model `Author`
- [x] กำหนด field:
  - id
  - name
  - created_at
  - updated_at
- [x] เพิ่ม `__str__`

### 1.2 Category Model

- [x] สร้าง model `Category`
- [x] กำหนด field:
  - id
  - name
  - created_at
  - updated_at
- [x] เพิ่ม unique constraint ที่ name
- [x] เพิ่ม `__str__`

### 1.3 Publisher Model

- [x] สร้าง model `Publisher`
- [x] กำหนด field:
  - id
  - name
  - created_at
  - updated_at
- [x] เพิ่ม unique constraint ที่ name
- [x] เพิ่ม `__str__`

### 1.4 Book Model

- [x] สร้าง model `Book`
- [x] กำหนด field:
  - id
  - title
  - description
  - image_url หรือ cover_image
  - total_quantity
  - available_quantity
  - publish_year
  - publisher
  - created_at
  - updated_at
- [x] ตั้ง validation:
  - total_quantity >= 0
  - available_quantity >= 0
- [x] เพิ่ม `__str__`

### 1.5 BookAuthor Relation

- [x] สร้างตารางเชื่อม `BookAuthor`
- [x] ใส่ unique constraint `(book, author)`

### 1.6 BookCategory Relation

- [x] สร้างตารางเชื่อม `BookCategory`
- [x] ใส่ unique constraint `(book, category)`

## Deliverables

- models ฝั่งหนังสือครบ
- migrations สำหรับ tables พื้นฐานครบ

## Acceptance Criteria

- สามารถเพิ่มข้อมูลผู้แต่ง หมวดหมู่ สำนักพิมพ์ หนังสือได้
- สามารถผูกหนังสือกับผู้แต่งและหมวดหมู่ได้
- ไม่มี duplicate relation ซ้ำ

## Status: ✅ COMPLETED

---

# Phase 2: Admin Foundation ✅ COMPLETED

## Goal

ทำให้ admin สามารถจัดการข้อมูลหลักของระบบได้จาก Django Admin

## Scope

- authors
- categories
- publishers
- books
- relation tables

## Tasks

- [x] register model ทั้งหมดใน admin
- [x] ปรับ list_display
- [x] ปรับ search_fields
- [x] ปรับ list_filter
- [x] ใช้ inline หรือ many-to-many admin editing ตามที่เลือก
- [x] ปรับ ordering
- [x] ปรับ readonly fields เช่น created_at, updated_at
- [x] ทดสอบเพิ่ม/แก้ไข/ลบข้อมูล

## Deliverables

- Django Admin ใช้จัดการข้อมูลพื้นฐานได้สะดวก

## Acceptance Criteria

- Admin เพิ่มหนังสือได้
- Admin กำหนดผู้แต่งและหมวดหมู่ให้หนังสือได้
- Admin ค้นหาหนังสือได้จาก title
- Admin กรองตาม publisher หรือ category ได้

## Status: ✅ COMPLETED

---

# Phase 3: Reservation System Data Layer

## Goal

สร้างโครงสร้างข้อมูลระบบจองหนังสือ

## Scope

- reservation_batches
- reservations

## Tasks

### 3.1 ReservationBatch Model

- [x] สร้าง model `ReservationBatch`
- [x] fields:
  - id
  - user
  - status
  - expires_at
  - created_at
  - updated_at
- [x] status choices:
  - pending
  - confirmed
  - cancelled

### 3.2 Reservation Model

- [x] สร้าง model `Reservation`
- [x] fields:
  - id
  - book
  - reservation_batch
  - status
  - created_at
  - updated_at
- [x] status choices:
  - pending
  - confirmed
  - cancelled

### 3.3 Rules

- [x] ออกแบบ helper/check ว่าจองได้เมื่อ `available_quantity > 0`
- [x] ออกแบบ policy ว่า 1 batch มีหลาย reservation items
- [x] ออกแบบการยกเลิกทั้ง batch และราย item ให้สอดคล้องกัน

## Deliverables

- models ของการจองพร้อมใช้งาน

## Acceptance Criteria

- สร้าง reservation batch ได้
- สร้าง reservation items หลายเล่มใน batch เดียวได้
- ความสัมพันธ์ user -> reservation_batches -> reservations ถูกต้อง

## Status: ✅ COMPLETED

---

# Phase 4: Reservation Admin Workflow ✅ COMPLETED

## Goal

ให้ admin จัดการรายการจองได้

## Tasks

- [x] register reservation models ใน admin
- [x] แสดงข้อมูลผู้ใช้ สถานะ วันหมดอายุ
- [x] เพิ่ม filter ตาม status
- [x] เพิ่ม search ตาม username หรือชื่อหนังสือ
- [x] ออกแบบ admin action:
  - confirm reservation batch
  - cancel reservation batch
- [x] เมื่อ confirm:
  - เปลี่ยน batch status เป็น confirmed
  - เปลี่ยน reservation items เป็น confirmed
  - ลด `books.available_quantity`
- [x] เมื่อ cancel:
  - เปลี่ยน batch status เป็น cancelled
  - เปลี่ยน reservation items เป็น cancelled
  - ถ้าเคยลดจำนวนแล้ว ต้องคืนจำนวนอย่างระมัดระวังตามเงื่อนไขจริง
- [x] **เพิ่ม: Admin สามารถสร้างการจองแทน user ได้**
  - เปิด has_add_permission สำหรับ ReservationBatch และ Reservation
  - เพิ่ม save_model override เพื่อตั้งค่า expires_at อัตโนมัติ
  - เพิ่ม has_delete_permission สำหรับป้องกันการลบ batch
  - ปรับ readonly_fields ให้ admin เลือก user และ book ได้

## Deliverables

- Admin ตรวจสอบและจัดการการจองได้
- **Admin สร้างการจองแทน user ได้** (เพิ่มใหม่)

## Acceptance Criteria

- Admin ยืนยันการจองได้
- Admin ยกเลิกการจองได้
- **Admin สร้าง reservation batch และเลือก user ได้**
- **Admin เพิ่ม reservation items (หนังสือ) ได้**
- **ระบบตั้งค่า expires_at อัตโนมัติ (3 วัน)**
- จำนวน available_quantity สอดคล้องกับสถานะการจอง

## Status: ✅ COMPLETED

---

# Phase 5: Loan System Data Layer ✅ COMPLETED

## Goal

สร้างโครงสร้างข้อมูลระบบยืมหนังสือ

## Scope

- loan_batches
- loan_items

## Tasks

### 5.1 LoanBatch Model

- [x] สร้าง model `LoanBatch`
- [x] fields:
  - id
  - user
  - due_date
  - created_at
  - updated_at

### 5.2 LoanItem Model

- [x] สร้าง model `LoanItem`
- [x] fields:
  - id
  - book
  - loan_batch
  - reservation (nullable)
  - status
  - returned_at
  - created_at
  - updated_at
- [x] status choices:
  - borrowed
  - returned
  - lost

### 5.3 Rules

- [x] รองรับทั้งการยืมที่มาจาก reservation และไม่มาจาก reservation
- [x] ออกแบบ flow ยืมหลายเล่มใน batch เดียว
- [x] ตรวจสอบ available_quantity ก่อนสร้าง loan

## Deliverables

- models ของระบบยืมพร้อมใช้งาน

## Acceptance Criteria

- สร้าง loan batch ได้
- สร้าง loan items หลายรายการได้
- loan item เชื่อม reservation ได้ถ้ามาจากการจอง

## Status: ✅ COMPLETED

---

# Phase 6: Loan Admin Workflow ✅ COMPLETED

## Goal

ให้ admin บันทึกการยืมและการคืนได้

## Tasks

- [x] register loan models ใน admin
- [x] search/filter ตาม user, book, status, due_date
- [x] ออกแบบ action:
  - mark returned
  - mark lost
- [x] เมื่อคืน:
  - เปลี่ยน status เป็น returned
  - กำหนด returned_at
  - เพิ่ม available_quantity กลับ
- [x] เมื่อ lost:
  - เปลี่ยน status เป็น lost
  - ไม่เพิ่ม available_quantity กลับ
  - เตรียมสร้าง fine ประเภท lost

## Deliverables

- Admin จัดการการยืมคืนได้

## Acceptance Criteria

- บันทึกการคืนได้
- บันทึกกรณีหนังสือหายได้
- จำนวน available_quantity สอดคล้องกับสถานะจริง

## Status: ✅ COMPLETED

---

# Phase 7: Fine System ✅ COMPLETED

## Goal

สร้างระบบค่าปรับ

## Scope

- fines

## Tasks

- [x] สร้าง model `Fine`
- [x] fields:
  - id
  - loan_item
  - amount
  - type
  - reason
  - status
  - paid_at
  - created_at
  - updated_at
- [x] type choices:
  - late_return
  - lost
  - damaged
- [x] status choices:
  - unpaid
  - paid
- [x] register fine model ใน admin
- [x] เพิ่ม filter/search
- [x] เพิ่ม admin actions: mark_as_paid, mark_as_unpaid
- [x] เพิ่ม list_display ที่ครบถ้วน
- [x] เพิ่ม autocomplete_fields
- [x] เพิ่ม status badge แบบมีสี

## Business Rules

- คืนช้า -> fine type = late_return
- ทำหาย -> fine type = lost
- หนังสือเสียหาย -> fine type = damaged
- เมื่อชำระแล้ว -> status = paid และ set paid_at

## Deliverables

- ระบบค่าปรับพร้อมใช้งาน

## Acceptance Criteria

- Admin สร้าง fine ได้
- Admin เปลี่ยนสถานะเป็น paid ได้
- Fine ผูกกับ loan_item ได้ถูกต้อง

## Status: ✅ COMPLETED

---

# Phase 8: Member-Facing Pages 🚧 IN PROGRESS

## Goal

สร้างหน้าฝั่งผู้ใช้ทั่วไป

## Scope

- authentication (register, login, logout)
- home
- book list
- book detail
- my reservations
- my loans
- my fines

## Tasks

### 8.0 Authentication System ✅ COMPLETED

- [x] สร้าง UserRegistrationForm พร้อม validation
- [x] สร้าง UserLoginForm
- [x] สร้าง register_view, login_view, logout_view
- [x] สร้าง URLs สำหรับ authentication
- [x] สร้าง register template
- [x] สร้าง login template
- [x] Validation เบอร์โทรศัพท์ (10 หลัก)
- [x] Success/Error messages
- [x] Redirect logic หลังล็อกอิน
- [x] ตั้งค่า LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL

### 8.1 Home Page ✅ COMPLETED

- [x] แสดงภาพรวมระบบ
- [x] แสดง features ของระบบ (ค้นหา, จอง, ติดตาม)
- [x] สร้าง base template พร้อม navbar
- [x] แสดงสถานะผู้ใช้ใน navbar
- [x] Hero section พร้อม call-to-action
- [x] Responsive design ด้วย Bootstrap 5

### 8.2 Book List Page ✅ COMPLETED

- [x] แสดงรายการหนังสือทั้งหมด
- [x] search ตามชื่อหนังสือ
- [x] filter ตาม category / publisher
- [x] pagination
- [x] Query optimization (select_related, prefetch_related)
- [x] Responsive grid layout
- [x] Book cards with cover images
- [x] Availability badges

### 8.3 Book Detail Page ✅ COMPLETED

- [x] แสดงรายละเอียดหนังสือ
- [x] แสดงผู้แต่ง หมวดหมู่ สำนักพิมพ์
- [x] แสดงจำนวน available_quantity
- [x] ปุ่มจองหนังสือ (ใช้งานได้จริง)
- [x] Breadcrumb navigation
- [x] Large cover image display
- [x] Login prompt for non-authenticated users
- [x] Shopping cart system for multiple book selection
- [x] Add to cart functionality
- [x] View cart with real-time availability check
- [x] Remove from cart functionality
- [x] Confirm reservation from cart (creates ReservationBatch)
- [x] Success/error messages
- [x] Redirect to My Reservations after booking

### 8.4 My Reservations Page ✅ COMPLETED

- [x] แสดง batch และ items ของการจอง
- [x] แสดงสถานะ
- [x] แสดงวันหมดอายุ
- [x] Status badges พร้อมสี
- [x] Query optimization

### 8.5 My Loans Page ✅ COMPLETED

- [x] แสดงรายการยืม
- [x] แสดง due_date
- [x] แสดงสถานะ borrowed / returned / lost
- [x] คำนวณและแสดงสถานะ overdue
- [x] แสดง returned date
- [x] Status badges พร้อมสี

### 8.6 My Fines Page ✅ COMPLETED

- [x] แสดงรายการค่าปรับ
- [x] แสดงยอดเงิน ประเภท และสถานะการชำระ
- [x] Summary cards (total unpaid, total paid)
- [x] Fine type badges
- [x] Reason popover
- [x] Warning alert for unpaid fines

## Deliverables

- ✅ ผู้ใช้ใช้งานระบบหลักได้สมบูรณ์

## Acceptance Criteria

- ✅ ผู้ใช้ดูหนังสือได้
- ✅ ผู้ใช้จองหนังสือได้ (สร้าง ReservationBatch และ Reservation)
- ✅ ผู้ใช้ดูประวัติการจอง ยืม และค่าปรับของตัวเองได้
- ✅ ระบบตรวจสอบ available_quantity ก่อนจอง
- ✅ ระบบแสดง success/error messages

## Status: ✅ COMPLETED

**Implementation Details:**

- Member สามารถจองหนังสือผ่านปุ่มในหน้า Book Detail
- ระบบสร้าง ReservationBatch พร้อม status='pending' และ expires_at (3 วัน)
- ระบบสร้าง Reservation item เชื่อมกับหนังสือที่เลือก
- ตรวจสอบ available_quantity > 0 ก่อนอนุญาตให้จอง
- Admin ต้องยืนยันการจองผ่าน Django Admin
- Admin สามารถสร้างการจองแทน user ได้ผ่าน admin interface

---

# Phase 9: Business Logic Hardening

## Goal

เสริม validation และป้องกันข้อมูลผิดพลาด

## Tasks

- [ ] ป้องกัน available_quantity ติดลบ
- [ ] ป้องกันการคืนซ้ำ
- [ ] ป้องกัน confirm reservation ซ้ำ
- [ ] ป้องกัน mark lost หลัง returned แล้ว
- [ ] ป้องกันสร้าง fine ซ้ำโดยไม่ตั้งใจ
- [ ] ตรวจสอบ due_date และ overdue logic
- [ ] เพิ่ม model validation / service layer validation

## Deliverables

- ระบบเสถียรมากขึ้น

## Acceptance Criteria

- action ที่ผิดลำดับถูก block
- ข้อมูลไม่หลุดเป็น state ที่ขัดแย้งกัน

---

# Phase 10: Testing

## Goal

ทดสอบระบบให้มั่นใจว่า flow หลักทำงานครบ

## Tasks

- [ ] unit tests สำหรับ models
- [ ] tests สำหรับ reservation workflow
- [ ] tests สำหรับ loan workflow
- [ ] tests สำหรับ fine workflow
- [ ] admin smoke test
- [ ] manual testing checklist

## Manual Test Scenarios

- [ ] เพิ่มหนังสือใหม่
- [ ] จองหนังสือ 1 เล่ม
- [ ] จองหนังสือหลายเล่ม
- [ ] ยืนยันการจอง
- [ ] ยกเลิกการจอง
- [ ] สร้างรายการยืมจากการจอง
- [ ] สร้างรายการยืมแบบไม่ผ่านการจอง
- [ ] คืนหนังสือปกติ
- [ ] คืนหนังสือช้าและสร้างค่าปรับ
- [ ] ทำหนังสือหายและสร้างค่าปรับ
- [ ] ชำระค่าปรับ

---

# Phase 11: Documentation and Cleanup

## Goal

เก็บงานให้เรียบร้อยและพร้อมส่ง/พัฒนาต่อ

## Tasks

- [ ] ปรับ README
- [ ] ปรับ docs ให้ตรงกับของจริง
- [ ] ตรวจสอบ migrations
- [ ] ลบ code ทดลองที่ไม่ใช้
- [ ] ตั้งชื่อ model / field / admin class ให้สม่ำเสมอ
- [ ] ตรวจสอบ import และ structure ของ app

## Deliverables

- โปรเจกต์พร้อมอ่านต่อและพัฒนาต่อ

---

## 7. Dependency Order

ลำดับ dependency สำคัญมาก

1. Project setup
2. Base models
3. Admin setup
4. Reservation models
5. Reservation admin logic
6. Loan models
7. Loan admin logic
8. Fine model
9. Member pages
10. Validation / tests / docs

ห้ามทำ loan ก่อน reservation schema ชัด
ห้ามทำ fine ก่อน loan schema ชัด
ห้ามทำ member pages ก่อน data layer ใช้งานได้จริง

---

## 8. Coding Rules for AI

AI ต้องปฏิบัติตามกติกานี้เสมอ

- อ่าน `docs/data-dictionary.md`, `docs/ai-context.md`, `docs/plan.md` ก่อน
- ยึด schema ตาม data dictionary
- อย่าสร้าง field ใหม่เองโดยไม่มีเหตุผล
- อย่าเปลี่ยนชื่อ model/field โดยไม่แจ้ง
- ทำงานทีละ phase
- เมื่อ implement phase ใด ให้สรุปสิ่งที่ทำและสิ่งที่ยังไม่ทำ
- ถ้ามี ambiguity ให้ยึดเอกสาร project ก่อนเดา
- ถ้าจำเป็นต้องเสนอการปรับ schema ให้เสนอเป็นข้อแนะนำแยก ไม่แก้เงียบ ๆ

---

## 9. Current Recommended Execution Order for This Project

ลำดับที่แนะนำสำหรับโปรเจกต์นี้ ณ ตอนนี้

- [x] books app models
- [x] books app admin
- [x] reservations models
- [x] reservations admin
- [ ] loans models
- [ ] loans admin
- [ ] fines models
- [ ] fines admin
- [ ] member-facing pages
- [ ] test flows
- [ ] refine permissions and validation

## Project Progress Summary

### ✅ Completed Phases (0-4)

**Phase 0: Project Setup** - โครงสร้างโปรเจกต์พร้อมใช้งาน

- Django project และ apps ทั้งหมดถูกสร้างและลงทะเบียนแล้ว
- Database connection และ media files ตั้งค่าเรียบร้อย
- Environment และ dependencies พร้อมใช้งาน

**Phase 1: Data Model Foundation** - Models ของระบบหนังสือครบถ้วน

- สร้าง models: Author, Category, Publisher, Book
- สร้าง many-to-many relations: BookAuthor, BookCategory
- Migrations ทั้งหมดสร้างและใช้งานได้แล้ว
- มี constraints และ validations ครบถ้วนตาม data dictionary

**Phase 2: Admin Foundation** - Django Admin พร้อมใช้งาน

- ลงทะเบียน models ทั้งหมดใน admin
- Admin interface มี search, filter, และ ordering ครบ
- สามารถจัดการข้อมูลหนังสือ ผู้แต่ง หมวดหมู่ และสำนักพิมพ์ได้อย่างสะดวก

**Phase 3: Reservation System Data Layer** - Models ของระบบการจองครบถ้วน

- สร้าง models: ReservationBatch, Reservation
- สร้าง status choices (pending, confirmed, cancelled)
- เพิ่ม helper methods: can_be_confirmed(), can_be_cancelled(), is_expired()
- Migrations สร้างและ apply เรียบร้อยแล้ว
- ความสัมพันธ์ user -> reservation_batches -> reservations ถูกต้อง

**Phase 4: Reservation Admin Workflow** - Admin จัดการการจองได้สมบูรณ์

- ลงทะเบียน ReservationBatch และ Reservation ใน Django Admin
- เพิ่ม list_display, search_fields, list_filter สำหรับค้นหาและกรองข้อมูล
- สร้าง admin actions:
  - confirm_reservations: ยืนยันการจอง เปลี่ยนสถานะ และลด available_quantity
  - cancel_reservations: ยกเลิกการจอง เปลี่ยนสถานะ และคืน available_quantity (ถ้าเคย confirm)
- ใช้ transaction.atomic() เพื่อความปลอดภัยของข้อมูล
- แสดง inline reservations ใน ReservationBatch admin
- เพิ่ม validation และ error handling ครบถ้วน

### 📋 Next Phases

**Phase 5: Loan System Data Layer** - รอดำเนินการ

---

## 10. Definition of Done

โปรเจกต์จะถือว่าเสร็จในระดับ MVP เมื่อ

- Admin จัดการข้อมูลหนังสือได้ครบ
- Member ดูและจองหนังสือได้
- Admin ยืนยันการจองได้
- Admin บันทึกการยืมและคืนได้
- ระบบเก็บค่าปรับได้
- ข้อมูลจำนวนหนังสือคงเหลือถูกต้อง
- เอกสารใน docs สอดคล้องกับโค้ดจริง

---
