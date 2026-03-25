# Changelog - Digital Library System

## [Critical Fix] - 2026-03-25

### 🔧 Book Admin - Authors และ Categories Fields Missing

**Issue:** ฟอร์มเพิ่ม Book ไม่แสดง fields สำหรับเลือก Authors และ Categories เลย

**Root Cause:**

- Book model ใช้ ManyToMany แบบมี intermediate model (`through="BookAuthor"` และ `through="BookCategory"`)
- Django ไม่สามารถสร้าง form fields อัตโนมัติสำหรับ ManyToMany ที่มี `through` model
- การใช้ `autocomplete_fields = ("authors", "categories")` จะไม่ทำงาน เพราะ fields เหล่านี้ไม่สามารถแก้ไขได้โดยตรง

**Solution:**

- สร้าง `BookAuthorInline` และ `BookCategoryInline` แบบ TabularInline
- เพิ่ม `inlines = [BookAuthorInline, BookCategoryInline]` ใน BookAdmin
- ใช้ `autocomplete_fields` ภายใน inline เพื่อมีปุ่ม "+" สำหรับเพิ่ม Author/Category ใหม่

**Code Changes:**

```python
# เพิ่ม Inline classes
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1
    autocomplete_fields = ("author",)

class BookCategoryInline(admin.TabularInline):
    model = BookCategory
    extra = 1
    autocomplete_fields = ("category",)

# อัปเดต BookAdmin
class BookAdmin(admin.ModelAdmin):
    autocomplete_fields = ("publisher",)  # เหลือแค่ publisher
    inlines = [BookAuthorInline, BookCategoryInline]  # เพิ่ม inlines
```

**Benefits:**

- ✅ แสดง Authors และ Categories ในฟอร์ม Book แล้ว
- ✅ สามารถเพิ่ม/ลบ authors และ categories แบบ inline
- ✅ มีปุ่ม "+" สำหรับเพิ่ม Author/Category ใหม่ได้ทันที
- ✅ UI แบบตาราง เห็นภาพรวมได้ชัดเจน

---

## [Improvement] - 2026-03-25

### 🔧 Book Admin UX Enhancement

**Issue:** เมื่อเพิ่ม Book ใหม่ใน Django Admin ไม่มีปุ่ม "+" สำหรับเพิ่ม Author, Category, หรือ Publisher ใหม่ได้ทันที ต้องออกไปเพิ่มที่หน้าอื่นก่อน

**Root Cause:** การใช้ `filter_horizontal` widget สำหรับ ManyToMany fields (authors, categories) ไม่รองรับการเพิ่มรายการใหม่แบบ inline

**Solution:**

- เปลี่ยนจาก `filter_horizontal = ("authors", "categories")`
- เป็น `autocomplete_fields = ("authors", "categories", "publisher")`

**Benefits:**

- ✅ มีปุ่ม "+" ข้างๆ dropdown ทุกฟิลด์
- ✅ สามารถเพิ่ม Author/Category/Publisher ใหม่ได้ทันทีโดยไม่ต้องออกจากหน้า Book
- ✅ UI แบบ autocomplete ค้นหาง่าย รองรับข้อมูลเยอะ
- ✅ ลด steps ในการเพิ่มหนังสือใหม่

**Technical Details:**

- `autocomplete_fields` ใช้งานได้เพราะ AuthorAdmin, CategoryAdmin, และ PublisherAdmin มี `search_fields` กำหนดไว้แล้ว
- Django จะสร้าง AJAX endpoint อัตโนมัติสำหรับ autocomplete search
- Publisher ถูกเพิ่มเข้ามาด้วยเพื่อความสมบูรณ์

---

## [Phase 7 Complete] - 2026-03-25

### ✅ Phase 7: Fine System

**Status:** COMPLETED

#### What was done:

- Fine model already existed with all required fields:
  - loan_item (FK to LoanItem)
  - amount (DecimalField)
  - type (choices: late_return, lost, damaged)
  - reason (TextField, optional)
  - status (choices: unpaid, paid, default=unpaid)
  - paid_at (DateTimeField, nullable)
  - created_at, updated_at (auto timestamps)

- Enhanced `FineAdmin` with comprehensive features:
  - เพิ่ม list_display: id, loan_item_display, book_title, borrower_name, type, amount_display, status_display, paid_at, created_at
  - เพิ่ม list_filter: type, status, created_at, paid_at
  - เพิ่ม search_fields: id, loan_item book title, user details, reason
  - เพิ่ม autocomplete_fields: loan_item
  - เพิ่ม list_select_related เพื่อ optimize queries
  - เพิ่ม date_hierarchy: created_at
  - เพิ่ม custom display methods:
    - loan_item_display: แสดง Loan Item ID พร้อม link
    - book_title: แสดงชื่อหนังสือ
    - borrower_name: แสดงชื่อผู้ยืม
    - amount_display: แสดงจำนวนเงินพร้อมสัญลักษณ์ $
    - status_display: แสดง status badge แบบมีสี (green=paid, red=unpaid)

- สร้าง admin action `mark_as_paid`:
  - ตรวจสอบว่า fine ยังไม่ได้ชำระ
  - ป้องกันการชำระซ้ำ (already paid)
  - เปลี่ยน status เป็น paid
  - บันทึก paid_at timestamp
  - แสดง success/error messages แบบ item-by-item

- สร้าง admin action `mark_as_unpaid`:
  - ตรวจสอบว่า fine ถูกชำระแล้ว
  - ป้องกันการเปลี่ยนสถานะซ้ำ (already unpaid)
  - เปลี่ยน status เป็น unpaid
  - ล้าง paid_at (set to None)
  - แสดง success/error messages แบบ item-by-item

- ปรับปรุง `LoanItemAdmin`:
  - เพิ่ม 'id' ใน search_fields เพื่อรองรับ autocomplete ใน FineAdmin

#### Business Logic Implemented:

- **Fine Management Workflow:**
  - Admin สร้าง fine ได้โดยเลือก loan_item และกำหนด type, amount, reason
  - Admin จัดการสถานะการชำระผ่าน admin actions
  - ป้องกันการชำระซ้ำ
  - รองรับการ revert สถานะเป็น unpaid ถ้าจำเป็น

#### Error Handling:

- ใช้ try-except เพื่อจัดการ errors ในแต่ละ fine
- แสดง error messages แบบ item-by-item
- แสดงสรุปผลรวม (success/failed counts)
- ป้องกัน workflow ที่ไม่สมเหตุสมผล

#### Query Optimization:

- เพิ่ม list_select_related ใน FineAdmin
- ใช้ autocomplete_fields แทน dropdown ธรรมดา
- Optimize การแสดงข้อมูล loan_item, book, และ user

#### UI/UX Enhancements:

- Status badge มีสีแยกชัดเจน (paid=เขียว, unpaid=แดง)
- แสดงจำนวนเงินพร้อมสัญลักษณ์ $
- แสดงข้อมูล loan item, book, และ borrower ที่ครบถ้วน
- Date hierarchy สำหรับการกรองตามวันที่

#### Deliverables:

- ✅ Fine model พร้อมใช้งาน
- ✅ Admin สามารถสร้าง fine ได้
- ✅ Admin สามารถค้นหาตาม loan item, book, user
- ✅ Admin สามารถกรองตาม type, status, dates
- ✅ Admin สามารถทำเครื่องหมาย fine เป็น paid/unpaid
- ✅ ระบบป้องกัน workflow ที่ไม่สมเหตุสมผล
- ✅ UI/UX ใช้งานง่ายและชัดเจน

---

## [Phase 6 Complete] - 2026-03-25

### ✅ Phase 6: Loan Admin Workflow

**Status:** COMPLETED

#### What was done:

- ปรับปรุง `LoanBatchAdmin`:
  - เพิ่ม list_display: id, user, due_date, items_count, borrowed_count, returned_count, lost_count, created_at
  - เพิ่ม search_fields: username, email, first_name, last_name
  - เพิ่ม list_filter: created_at, due_date
  - เพิ่ม autocomplete_fields: user
  - เพิ่ม inline editing สำหรับ LoanItems
  - แสดงสถิติการยืมแบบ real-time (borrowed/returned/lost counts)

- ปรับปรุง `LoanItemAdmin`:
  - เพิ่ม list_display: id, book, batch_user, batch_due_date, status, returned_at, created_at
  - เพิ่ม list_filter: status, created_at, returned_at, batch due_date
  - เพิ่ม search_fields: book title, user details
  - เพิ่ม autocomplete_fields: book, loan_batch, reservation
  - เพิ่ม list_select_related เพื่อ optimize queries
  - เพิ่ม admin actions: mark_as_returned, mark_as_lost

- สร้าง admin action `mark_as_returned`:
  - ตรวจสอบว่า loan item สามารถคืนได้ (borrowed status)
  - ป้องกันการคืนซ้ำ (already returned)
  - ป้องกันการคืนหนังสือที่หาย (lost status)
  - เปลี่ยน status เป็น returned
  - บันทึก returned_at timestamp
  - เพิ่ม available_quantity กลับคืน
  - แสดง success/error messages แบบ batch-by-batch

- สร้าง admin action `mark_as_lost`:
  - ตรวจสอบว่า loan item สามารถทำเครื่องหมายเป็น lost ได้
  - ป้องกันการทำเครื่องหมาย lost กับหนังสือที่คืนแล้ว
  - ป้องกันการทำเครื่องหมาย lost ซ้ำ
  - เปลี่ยน status เป็น lost
  - **ไม่เพิ่ม** available_quantity กลับ (หนังสือหาย)
  - แจ้งเตือน admin ให้สร้าง fine สำหรับหนังสือหาย
  - แสดง success/error messages แบบ batch-by-batch

- ปรับปรุง search และ autocomplete:
  - เพิ่ม id ใน search_fields ของ Book, Reservation, ReservationBatch
  - เพิ่ม autocomplete_fields ใน ReservationAdmin
  - เพิ่ม autocomplete_fields ใน ReservationBatchAdmin

#### Business Logic Implemented:

- **Return Workflow:**
  - ตรวจสอบสถานะก่อนคืน (ต้องเป็น borrowed)
  - บันทึก timestamp ของการคืน
  - อัปเดต available_quantity อัตโนมัติ
  - Transaction safety ด้วย atomic
  - Error handling แบบ per-item

- **Lost Workflow:**
  - ตรวจสอบสถานะก่อนทำเครื่องหมาย lost
  - ไม่คืน stock กลับ (หนังสือหายจริง)
  - เตือน admin ให้สร้าง fine
  - Transaction safety ด้วย atomic
  - Error handling แบบ per-item

#### Error Handling:

- ใช้ try-except เพื่อจัดการ errors ในแต่ละ loan item
- แสดง error messages แบบ item-by-item
- แสดงสรุปผลรวม (success/failed counts)
- ป้องกันการคืนซ้ำหรือ lost ซ้ำ
- ป้องกัน workflow ที่ไม่สมเหตุสมผล (เช่น คืนหนังสือที่หายแล้ว)

#### Query Optimization:

- เพิ่ม list_select_related ใน LoanItemAdmin
- ใช้ autocomplete_fields แทน dropdown ธรรมดา
- Optimize การแสดงข้อมูล user และ batch

#### Deliverables:

- ✅ Admin สามารถดูรายการยืมทั้งหมด
- ✅ Admin สามารถค้นหาตาม user, book, status
- ✅ Admin สามารถกรองตาม status, due_date
- ✅ Admin สามารถทำเครื่องหมายหนังสือเป็น returned
- ✅ Admin สามารถทำเครื่องหมายหนังสือเป็น lost
- ✅ จำนวน available_quantity สอดคล้องกับสถานะการยืมคืน
- ✅ ระบบป้องกัน workflow ที่ไม่สมเหตุสมผล

---

## [Phase 5 Complete] - 2026-03-25

### ✅ Phase 5: Loan System Data Layer

**Status:** COMPLETED

#### What was done:

- สร้าง `LoanBatch` model พร้อม:
  - Fields ครบถ้วนตาม data dictionary (user, due_date, created_at, updated_at)
  - ForeignKey ไปยัง User model
  - Meta options: db_table='loan_batches', ordering by created_at
  - `__str__` method แสดง batch ID และ username
- สร้าง `LoanItem` model พร้อม:
  - Fields ครบถ้วนตาม data dictionary (book, loan_batch, reservation, status, returned_at, created_at, updated_at)
  - Status choices: borrowed, returned, lost
  - ForeignKey ไปยัง Book, LoanBatch, และ Reservation (nullable)
  - Meta options: db_table='loan_items', ordering by created_at
  - `__str__` method แสดงชื่อหนังสือและสถานะ
- Migrations ถูกสร้างและ apply เรียบร้อยแล้ว:
  - `loans/migrations/0001_initial.py`
  - `loans/migrations/0002_initial.py`
  - `loans/migrations/0003_initial.py`

#### Business Rules Implemented:

- รองรับการยืมที่มาจาก reservation และไม่มาจาก reservation (ผ่าน nullable reservation field)
- ออกแบบ flow ยืมหลายเล่มใน batch เดียว (1 LoanBatch มีหลาย LoanItems)
- พร้อมสำหรับตรวจสอบ available_quantity ก่อนสร้าง loan (จะทำใน Phase 6)
- Status tracking: borrowed → returned หรือ lost
- บันทึกวันที่คืนหนังสือ (returned_at) เมื่อเปลี่ยนสถานะเป็น returned

#### Database Tables Created:

- `loan_batches` - Header record for borrowing transactions
  - id (PK)
  - user_id (FK → users)
  - due_date
  - created_at
  - updated_at

- `loan_items` - Individual borrowed books
  - id (PK)
  - book_id (FK → books)
  - loan_batch_id (FK → loan_batches)
  - reservation_id (FK → reservations, nullable)
  - status (borrowed/returned/lost)
  - returned_at
  - created_at
  - updated_at

#### Relationships:

- User → LoanBatch (one-to-many)
- LoanBatch → LoanItem (one-to-many)
- Book → LoanItem (one-to-many)
- Reservation → LoanItem (one-to-one, optional)

#### Deliverables:

- ✅ LoanBatch model พร้อมใช้งาน
- ✅ LoanItem model พร้อมใช้งาน
- ✅ สร้าง loan batch ได้
- ✅ สร้าง loan items หลายรายการได้
- ✅ loan item เชื่อม reservation ได้ถ้ามาจากการจอง
- ✅ Migrations สำเร็จ

---

## [Phase 4 Complete] - 2026-03-25

### ✅ Phase 4: Reservation Admin Workflow

**Status:** COMPLETED

#### What was done:

- ลงทะเบียน `ReservationBatch` และ `Reservation` models ใน Django Admin
- ปรับปรุง `ReservationBatchAdmin`:
  - เพิ่ม list_display: id, user, status, expires_at, reservation_count, timestamps
  - เพิ่ม list_filter: status, expires_at, created_at
  - เพิ่ม search_fields: username, email, first_name, last_name
  - เพิ่ม inline display สำหรับ reservations
  - เพิ่ม admin actions: confirm_reservations, cancel_reservations
- ปรับปรุง `ReservationAdmin`:
  - เพิ่ม list_display: id, book, batch_id, batch_user, batch_status, status, timestamps
  - เพิ่ม list_filter: status, created_at, batch status
  - เพิ่ม search_fields: book title, user username/email
  - เพิ่ม list_select_related เพื่อ optimize queries
- สร้าง admin action `confirm_reservations`:
  - ตรวจสอบว่า batch สามารถยืนยันได้ (pending, ไม่หมดอายุ)
  - เปลี่ยน batch status เป็น confirmed
  - เปลี่ยน reservation items ทั้งหมดเป็น confirmed
  - ลด `books.available_quantity` สำหรับแต่ละเล่ม
  - ใช้ `transaction.atomic()` เพื่อป้องกันข้อมูลไม่สอดคล้อง
  - แสดง error/warning messages ที่ชัดเจน
- สร้าง admin action `cancel_reservations`:
  - ตรวจสอบว่า batch สามารถยกเลิกได้ (pending หรือ confirmed)
  - เปลี่ยน batch status เป็น cancelled
  - เปลี่ยน reservation items ทั้งหมดเป็น cancelled
  - คืน `books.available_quantity` สำหรับ items ที่เคย confirmed
  - ใช้ `transaction.atomic()` เพื่อป้องกันข้อมูลไม่สอดคล้อง
  - แสดง error/warning messages ที่ชัดเจน

#### Business Logic Implemented:

- **Confirm Workflow:**
  - ตรวจสอบ available_quantity ก่อนยืนยันการจอง
  - อัปเดต status ของ batch และ items พร้อมกัน
  - ลด available_quantity อัตโนมัติเมื่อยืนยัน
  - ป้องกันการยืนยันซ้ำหรือการยืนยันที่หมดอายุ

- **Cancel Workflow:**
  - รองรับการยกเลิกทั้ง pending และ confirmed status
  - คืน available_quantity เฉพาะ items ที่เคย confirmed
  - ป้องกันข้อมูล available_quantity ไม่สอดคล้อง
  - อัปเดต status ของ batch และ items พร้อมกัน

#### Error Handling:

- ใช้ try-except เพื่อจัดการ errors ในแต่ละ batch
- แสดง error messages แบบ batch-by-batch
- แสดงสรุปผลรวม (success/failed counts)
- ป้องกันการ confirm เมื่อหนังสือไม่พอ

#### Deliverables:

- ✅ Admin สามารถดูรายการจองทั้งหมด
- ✅ Admin สามารถค้นหาตาม username หรือชื่อหนังสือ
- ✅ Admin สามารถกรองตาม status
- ✅ Admin สามารถยืนยันการจองได้
- ✅ Admin สามารถยกเลิกการจองได้
- ✅ จำนวน available_quantity สอดคล้องกับสถานะการจอง

---

## [Phase 3 Complete] - 2026-03-25

### ✅ Phase 3: Reservation System Data Layer

**Status:** COMPLETED

#### What was done:

- สร้าง `ReservationBatch` model พร้อม:
  - Fields ครบถ้วนตาม data dictionary (user, status, expires_at, created_at, updated_at)
  - Status choices: pending, confirmed, cancelled
  - Helper methods: `is_expired()`, `can_be_confirmed()`, `can_be_cancelled()`
  - ForeignKey ไปยัง User model
- สร้าง `Reservation` model พร้อม:
  - Fields ครบถ้วนตาม data dictionary (book, reservation_batch, status, created_at, updated_at)
  - Status choices: pending, confirmed, cancelled
  - Helper methods: `can_be_confirmed()`, `can_be_cancelled()`
  - ForeignKey ไปยัง Book และ ReservationBatch
- Migrations ถูกสร้างและ apply เรียบร้อยแล้ว:
  - `reservations/migrations/0001_initial.py`
  - `reservations/migrations/0002_initial.py`

#### Business Rules Implemented:

- ตรวจสอบว่าการจองหมดอายุหรือไม่ผ่าน `is_expired()`
- ตรวจสอบว่าสามารถยืนยันการจองได้หรือไม่ (ต้องเป็น pending, ไม่หมดอายุ, และหนังสือมีจำนวนเพียงพอ)
- ตรวจสอบว่าสามารถยกเลิกการจองได้หรือไม่ (สถานะต้องเป็น pending หรือ confirmed)
- 1 batch สามารถมีหลาย reservation items ได้

#### Database Tables Created:

- `reservation_batches`
- `reservations`

#### Deliverables:

- ✅ Models ของการจองพร้อมใช้งาน
- ✅ สร้าง reservation batch ได้
- ✅ สร้าง reservation items หลายเล่มใน batch เดียวได้
- ✅ ความสัมพันธ์ user -> reservation_batches -> reservations ถูกต้อง

---

## [Phase 0-2 Complete] - 2026-03-25

### ✅ Phase 0: Project Setup

**Status:** COMPLETED

#### What was done:

- สร้าง Django project `config/`
- สร้าง apps ทั้งหมด: `users`, `books`, `reservations`, `loans`, `fines`
- ตั้งค่า `requirements.txt` พร้อม dependencies
- ตั้งค่า database (SQLite for development)
- ตั้งค่า media files configuration
- ตั้งค่า timezone เป็น Asia/Bangkok
- สร้างโครงสร้างโฟลเดอร์ `media/books/covers/`

#### Deliverables:

- ✅ `python manage.py runserver` ทำงานได้
- ✅ `python manage.py migrate` ทำงานได้
- ✅ Apps ทั้งหมดถูกเพิ่มใน `INSTALLED_APPS`

---

### ✅ Phase 1: Data Model Foundation

**Status:** COMPLETED

#### What was done:

- สร้าง `Author` model พร้อม fields ครบถ้วนตาม data dictionary
- สร้าง `Category` model พร้อม unique constraint ที่ name
- สร้าง `Publisher` model พร้อม unique constraint ที่ name
- สร้าง `Book` model พร้อม:
  - ImageField สำหรับ cover image
  - ForeignKey ไปยัง Publisher
  - ManyToManyField ไปยัง Author และ Category ผ่าน through tables
  - CheckConstraints สำหรับ total_quantity และ available_quantity >= 0
- สร้าง `BookAuthor` intermediate model พร้อม unique constraint (book, author)
- สร้าง `BookCategory` intermediate model พร้อม unique constraint (book, category)
- สร้าง migrations: `books/migrations/0001_initial.py`

#### Database Tables Created:

- `authors`
- `categories`
- `publishers`
- `books`
- `book_authors`
- `book_categories`

#### Deliverables:

- ✅ Models ฝั่งหนังสือครบถ้วน
- ✅ Migrations ทำงานได้
- ✅ สามารถเพิ่มข้อมูลและสร้างความสัมพันธ์ได้ถูกต้อง
- ✅ Constraints ป้องกันข้อมูลผิดพลาด

---

### ✅ Phase 2: Admin Foundation

**Status:** COMPLETED

#### What was done:

- ลงทะเบียน models ทั้งหมดใน `books/admin.py`
- **AuthorAdmin:**
  - list_display: id, name, books_count, created_at, updated_at
  - search_fields: name
  - list_filter: created_at, updated_at
  - ordering: name
  - Annotated books_count เพื่อหลีกเลี่ยง N+1 queries
- **CategoryAdmin:**
  - list_display: id, name, books_count, created_at, updated_at
  - search_fields: name
  - list_filter: created_at, updated_at
  - ordering: name
  - Annotated books_count
- **PublisherAdmin:**
  - list_display: id, name, books_count, created_at, updated_at
  - search_fields: name
  - list_filter: created_at, updated_at
  - ordering: name
  - Annotated books_count
- **BookAdmin:**
  - list_display: id, cover_preview, title, publisher, publish_year, total_quantity, available_quantity, availability_status, author_names, category_names, updated_at
  - search_fields: title, description, authors**name, categories**name, publisher\_\_name
  - list_filter: publish_year, publisher, available_quantity, authors, categories
  - filter_horizontal: authors, categories
  - ordering: -created_at
  - Custom methods: cover_preview (แสดงรูปปก), availability_status (แสดงสถานะความพร้อม)
  - list_select_related: publisher (optimize queries)
  - prefetch_related: authors, categories (optimize queries)

#### Features Implemented:

- ✅ Admin interface ใช้งานง่าย มีการจัด layout ที่ดี
- ✅ Search และ filter ทำงานได้ดี
- ✅ แสดง preview รูปปกหนังสือใน list view
- ✅ แสดงจำนวนหนังสือที่เชื่อมโยงกับ Author, Category, Publisher
- ✅ Query optimization ด้วย select_related, prefetch_related, และ annotation
- ✅ Readonly fields สำหรับ created_at, updated_at

#### Deliverables:

- ✅ Admin สามารถเพิ่ม/แก้ไข/ลบข้อมูลได้ทุก model
- ✅ Admin ค้นหาหนังสือได้จากชื่อ, ผู้แต่ง, หมวดหมู่, สำนักพิมพ์
- ✅ Admin กรองข้อมูลได้ตามเกณฑ์ต่างๆ
- ✅ Performance ดี ไม่มี N+1 query problem

---

## 📋 Next Phase

### Phase 8: Member-Facing Pages

**Status:** รอดำเนินการ

#### Planned Tasks:

- [ ] สร้างหน้า home page
- [ ] สร้างหน้า book list และ book detail
- [ ] สร้างหน้า my reservations
- [ ] สร้างหน้า my loans
- [ ] สร้างหน้า my fines
- [ ] เพิ่ม search และ filter ใน book list

---

## Technical Stack

- **Framework:** Django 5.1.5
- **Database:** SQLite (development)
- **Python:** 3.x
- **Dependencies:**
  - Pillow (image handling)
  - django-extensions (development tools)

---

## File Structure

```
digital-library/
├── config/              # Django project settings
├── books/               # Books app (✅ Complete)
├── users/               # Users app (ready)
├── reservations/        # Reservations app (pending)
├── loans/               # Loans app (pending)
├── fines/               # Fines app (pending)
├── media/               # Media files
│   └── books/covers/    # Book cover images
├── docs/                # Documentation
│   ├── ai-context.md    # System overview (updated)
│   ├── plan.md          # Development plan (updated)
│   ├── data-dictionary.md
│   ├── README-AI.md     # AI entry point (updated)
│   └── CHANGELOG.md     # This file
├── db.sqlite3           # Development database
├── manage.py
└── requirements.txt
```

---

## Notes for AI

- ยึดตาม data dictionary เป็นหลักในการออกแบบ schema
- ทำงานทีละ phase ตาม plan.md
- ใช้ Django Admin เป็นหลักในการทดสอบ CRUD ก่อนสร้าง UI
- รักษา code quality และ documentation ให้เป็นปัจจุบัน
- เมื่อเริ่ม Phase ใหม่ ให้อัปเดต CHANGELOG นี้

---

## Migration History

### Books App

- `0001_initial.py` - สร้าง tables: authors, categories, publishers, books, book_authors, book_categories

### Reservations App

- `0001_initial.py` - สร้าง table: reservation_batches
- `0002_initial.py` - สร้าง table: reservations

### Loans App

- `0001_initial.py` - สร้าง table: loan_batches
- `0002_initial.py` - สร้าง table: loan_items
- `0003_initial.py` - เพิ่ม unique constraint

### Fines App

- `0001_initial.py` - สร้าง table: fines
- `0002_initial.py` - เพิ่ม fields และ constraints

### Users App

- `0001_initial.py` - สร้าง custom user model (ถ้ามี)

---

_Last updated: March 25, 2026_
