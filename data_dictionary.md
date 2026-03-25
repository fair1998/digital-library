# Data Dictionary: Digital Library System

เอกสารนี้อธิบายความหมายของแต่ละตารางและแต่ละฟิลด์ในฐานข้อมูลระบบจัดการห้องสมุดดิจิทัล

---

## Table: `users`

| Field          | Type         | Constraints               | Description                                |
| -------------- | ------------ | ------------------------- | ------------------------------------------ |
| `id`           | int          | PK, increment             | รหัสผู้ใช้ เป็น Primary Key ของตารางผู้ใช้ |
| `username`     | varchar(150) | not null, unique          | ชื่อผู้ใช้สำหรับเข้าสู่ระบบ ต้องไม่ซ้ำกัน  |
| `password`     | varchar(128) | not null                  | รหัสผ่านที่ถูกเข้ารหัสแบบ hash แล้ว        |
| `first_name`   | varchar(150) | not null                  | ชื่อจริงของผู้ใช้                          |
| `last_name`    | varchar(150) | not null                  | นามสกุลของผู้ใช้                           |
| `email`        | varchar(254) | unique                    | อีเมลของผู้ใช้ ใช้สำหรับติดต่อ             |
| `is_active`    | boolean      | not null, default `true`  | สถานะการใช้งานของผู้ใช้                    |
| `is_superuser` | boolean      | not null, default `false` | สิทธิ์ผู้ดูแลระบบ                          |
| `last_login`   | timestamp    | nullable                  | วันเวลาที่ผู้ใช้เข้าสู่ระบบล่าสุด          |
| `date_joined`  | timestamp    | not null, default `now()` | วันเวลาที่สร้างบัญชีผู้ใช้                 |
| `phone_number` | varchar(10)  | nullable                  | เบอร์โทรศัพท์ (ตัวเลข 10 หลัก)             |

**คำอธิบายตาราง:** เก็บข้อมูลผู้ใช้งานทั้งหมดในระบบ

---

## Table: `books`

| Field                | Type         | Constraints                         | Description                                    |
| -------------------- | ------------ | ----------------------------------- | ---------------------------------------------- |
| `id`                 | int          | PK, increment                       | รหัสหนังสือ เป็น Primary Key ของตารางหนังสือ   |
| `title`              | varchar(255) | not null                            | ชื่อหนังสือ                                    |
| `description`        | text         | nullable                            | รายละเอียดหรือคำอธิบายหนังสือ                  |
| `image_url`          | text         | nullable                            | URL ของรูปปกหนังสือ                            |
| `total_quantity`     | int          | not null, default `0`, check `>= 0` | จำนวนหนังสือทั้งหมดในระบบ รวมทั้งที่ถูกยืมอยู่ |
| `available_quantity` | int          | not null, default `0`, check `>= 0` | จำนวนหนังสือที่ยังสามารถยืมหรือจองได้ในขณะนั้น |
| `publish_year`       | int          | nullable, check `>= 0`              | ปีที่พิมพ์หนังสือ                              |
| `publisher_id`       | int          | FK -> `publishers.id`, nullable     | อ้างอิงไปยังสำนักพิมพ์ของหนังสือ               |
| `updated_at`         | timestamp    | default `now()`                     | วันและเวลาที่แก้ไขข้อมูลล่าสุด                 |
| `created_at`         | timestamp    | default `now()`                     | วันและเวลาที่เพิ่มหนังสือเข้าระบบ              |

**คำอธิบายตาราง:** เก็บข้อมูลหนังสือทั้งหมดในระบบ

---

## Table: `authors`

| Field        | Type         | Constraints     | Description                    |
| ------------ | ------------ | --------------- | ------------------------------ |
| `id`         | int          | PK, increment   | รหัสผู้แต่ง                    |
| `name`       | varchar(255) | not null        | ชื่อผู้แต่งหนังสือ             |
| `updated_at` | timestamp    | default `now()` | วันและเวลาที่แก้ไขข้อมูลล่าสุด |
| `created_at` | timestamp    | default `now()` | วันและเวลาที่สร้างข้อมูล       |

**คำอธิบายตาราง:** เก็บข้อมูลผู้แต่งหนังสือ

---

## Table: `categories`

| Field        | Type         | Constraints      | Description                       |
| ------------ | ------------ | ---------------- | --------------------------------- |
| `id`         | int          | PK, increment    | รหัสหมวดหมู่                      |
| `name`       | varchar(255) | not null, unique | ชื่อหมวดหมู่หนังสือ ต้องไม่ซ้ำกัน |
| `updated_at` | timestamp    | default `now()`  | วันและเวลาที่แก้ไขข้อมูลล่าสุด    |
| `created_at` | timestamp    | default `now()`  | วันและเวลาที่สร้างข้อมูล          |

**คำอธิบายตาราง:** เก็บข้อมูลหมวดหมู่ของหนังสือ

---

## Table: `publishers`

| Field        | Type         | Constraints      | Description                    |
| ------------ | ------------ | ---------------- | ------------------------------ |
| `id`         | int          | PK, increment    | รหัสสำนักพิมพ์                 |
| `name`       | varchar(255) | not null, unique | ชื่อสำนักพิมพ์ ต้องไม่ซ้ำกัน   |
| `updated_at` | timestamp    | default `now()`  | วันและเวลาที่แก้ไขข้อมูลล่าสุด |
| `created_at` | timestamp    | default `now()`  | วันและเวลาที่สร้างข้อมูล       |

**คำอธิบายตาราง:** เก็บข้อมูลสำนักพิมพ์

---

## Table: `book_authors`

| Field       | Type | Constraints                  | Description                              |
| ----------- | ---- | ---------------------------- | ---------------------------------------- |
| `id`        | int  | PK, increment                | รหัสรายการเชื่อมระหว่างหนังสือกับผู้แต่ง |
| `book_id`   | int  | not null, FK -> `books.id`   | อ้างอิงไปยังหนังสือ                      |
| `author_id` | int  | not null, FK -> `authors.id` | อ้างอิงไปยังผู้แต่ง                      |

**Unique Index:** (`book_id`, `author_id`) เพื่อป้องกันข้อมูลซ้ำ

**คำอธิบายตาราง:** ตารางเชื่อมความสัมพันธ์แบบ many-to-many ระหว่างหนังสือกับผู้แต่ง

---

## Table: `book_categories`

| Field         | Type | Constraints                     | Description                               |
| ------------- | ---- | ------------------------------- | ----------------------------------------- |
| `id`          | int  | PK, increment                   | รหัสรายการเชื่อมระหว่างหนังสือกับหมวดหมู่ |
| `book_id`     | int  | not null, FK -> `books.id`      | อ้างอิงไปยังหนังสือ                       |
| `category_id` | int  | not null, FK -> `categories.id` | อ้างอิงไปยังหมวดหมู่                      |

**Unique Index:** (`book_id`, `category_id`) เพื่อป้องกันข้อมูลซ้ำ

**คำอธิบายตาราง:** ตารางเชื่อมความสัมพันธ์แบบ many-to-many ระหว่างหนังสือกับหมวดหมู่

---

## Table: `reservation_batches`

| Field        | Type        | Constraints                                                              | Description                                                                                             |
| ------------ | ----------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `id`         | int         | PK, increment                                                            | รหัสชุดการจอง                                                                                           |
| `user_id`    | int         | not null, FK -> `users.id`                                               | ผู้ใช้ที่ทำรายการจอง                                                                                    |
| `status`     | varchar(20) | not null, default `pending`, check (`pending`, `confirmed`, `cancelled`) | สถานะของชุดการจอง โดย `pending` คือรอดำเนินการ, `confirmed` คือยืนยันแล้ว, `cancelled` คือยกเลิกทั้งชุด |
| `expires_at` | timestamp   | not null                                                                 | วันและเวลาหมดอายุของการจอง                                                                              |
| `updated_at` | timestamp   | default `now()`                                                          | วันและเวลาที่แก้ไขข้อมูลล่าสุด                                                                          |
| `created_at` | timestamp   | default `now()`                                                          | วันและเวลาที่สร้างชุดการจอง                                                                             |

**คำอธิบายตาราง:** เก็บหัวรายการจอง 1 ครั้ง ซึ่ง 1 ชุดการจองสามารถมีหนังสือได้หลายเล่ม

---

## Table: `reservations`

| Field                  | Type        | Constraints                                                              | Description                                                                                   |
| ---------------------- | ----------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `id`                   | int         | PK, increment                                                            | รหัสรายการจอง                                                                                 |
| `book_id`              | int         | not null, FK -> `books.id`                                               | หนังสือที่ถูกจอง                                                                              |
| `reservation_batch_id` | int         | not null, FK -> `reservation_batches.id`                                 | อ้างอิงไปยังชุดการจอง                                                                         |
| `status`               | varchar(20) | not null, default `pending`, check (`pending`, `confirmed`, `cancelled`) | สถานะของรายการจอง โดย `pending` คือรออนุมัติ, `confirmed` คือจองสำเร็จ, `cancelled` คือยกเลิก |
| `updated_at`           | timestamp   | default `now()`                                                          | วันและเวลาที่แก้ไขข้อมูลล่าสุด                                                                |
| `created_at`           | timestamp   | default `now()`                                                          | วันและเวลาที่สร้างรายการจอง                                                                   |

**คำอธิบายตาราง:** เก็บรายการหนังสือแต่ละเล่มที่อยู่ภายในชุดการจอง

---

## Table: `loan_batches`

| Field        | Type      | Constraints                | Description                    |
| ------------ | --------- | -------------------------- | ------------------------------ |
| `id`         | int       | PK, increment              | รหัสชุดการยืม                  |
| `user_id`    | int       | not null, FK -> `users.id` | ผู้ใช้ที่ยืมหนังสือ            |
| `due_date`   | timestamp | nullable                   | วันและเวลาที่ต้องคืนหนังสือ    |
| `updated_at` | timestamp | default `now()`            | วันและเวลาที่แก้ไขข้อมูลล่าสุด |
| `created_at` | timestamp | default `now()`            | วันและเวลาที่สร้างรายการยืม    |

**คำอธิบายตาราง:** เก็บหัวรายการยืม 1 ครั้ง ซึ่ง 1 ครั้งสามารถมีหนังสือได้หลายเล่ม

---

## Table: `loan_items`

| Field            | Type        | Constraints                                                          | Description                                                                              |
| ---------------- | ----------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `id`             | int         | PK, increment                                                        | รหัสรายการยืมหนังสือ                                                                     |
| `book_id`        | int         | not null, FK -> `books.id`                                           | หนังสือที่ถูกยืม                                                                         |
| `loan_batch_id`  | int         | not null, FK -> `loan_batches.id`                                    | อ้างอิงไปยังชุดการยืม                                                                    |
| `reservation_id` | int         | nullable, FK -> `reservations.id`                                    | อ้างอิงไปยังรายการจองเดิม หากการยืมนี้มาจากการจอง                                        |
| `status`         | varchar(20) | not null, default `borrowed`, check (`borrowed`, `returned`, `lost`) | สถานะของหนังสือที่ยืม โดย `borrowed` คือกำลังยืม, `returned` คือคืนแล้ว, `lost` คือทำหาย |
| `returned_at`    | timestamp   | nullable                                                             | วันและเวลาที่คืนหนังสือจริง                                                              |
| `updated_at`     | timestamp   | default `now()`                                                      | วันและเวลาที่แก้ไขข้อมูลล่าสุด                                                           |
| `created_at`     | timestamp   | default `now()`                                                      | วันและเวลาที่สร้างรายการยืม                                                              |

**คำอธิบายตาราง:** เก็บรายการหนังสือแต่ละเล่มในชุดการยืม

---

## Table: `fines`

| Field          | Type          | Constraints                                          | Description                                                                           |
| -------------- | ------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `id`           | int           | PK, increment                                        | รหัสค่าปรับ                                                                           |
| `loan_item_id` | int           | not null, FK -> `loan_items.id`                      | อ้างอิงไปยังรายการยืมที่เกิดค่าปรับ                                                   |
| `amount`       | decimal(10,2) | not null                                             | จำนวนเงินค่าปรับ                                                                      |
| `type`         | varchar(20)   | not null, check (`late_return`, `lost`, `damaged`)   | ประเภทค่าปรับ โดย `late_return` คือคืนช้า, `lost` คือทำหาย, `damaged` คือชำรุดเสียหาย |
| `reason`       | text          | nullable                                             | รายละเอียดเพิ่มเติมหรือสาเหตุของค่าปรับ                                               |
| `status`       | varchar(20)   | not null, default `unpaid`, check (`unpaid`, `paid`) | สถานะการชำระค่าปรับ โดย `unpaid` คือยังไม่ชำระ และ `paid` คือชำระแล้ว                 |
| `paid_at`      | timestamp     | nullable                                             | วันและเวลาที่ชำระค่าปรับ                                                              |
| `updated_at`   | timestamp     | default `now()`                                      | วันและเวลาที่แก้ไขข้อมูลล่าสุด                                                        |
| `created_at`   | timestamp     | default `now()`                                      | วันและเวลาที่สร้างรายการค่าปรับ                                                       |

**คำอธิบายตาราง:** เก็บข้อมูลค่าปรับของแต่ละรายการยืมหนังสือ

---

## Relationship Summary

- `books.publisher_id` อ้างอิง `publishers.id`
- `book_authors.book_id` อ้างอิง `books.id`
- `book_authors.author_id` อ้างอิง `authors.id`
- `book_categories.book_id` อ้างอิง `books.id`
- `book_categories.category_id` อ้างอิง `categories.id`
- `reservation_batches.user_id` อ้างอิง `users.id`
- `reservations.book_id` อ้างอิง `books.id`
- `reservations.reservation_batch_id` อ้างอิง `reservation_batches.id`
- `loan_batches.user_id` อ้างอิง `users.id`
- `loan_items.book_id` อ้างอิง `books.id`
- `loan_items.loan_batch_id` อ้างอิง `loan_batches.id`
- `loan_items.reservation_id` อ้างอิง `reservations.id`
- `fines.loan_item_id` อ้างอิง `loan_items.id`
