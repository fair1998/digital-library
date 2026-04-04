# Changelog - Digital Library System

## [Bug Fix] - 2026-04-05 - Overdue Badge Only for Active Loans

### 🐛 Fix Overdue Badge Display Logic

**แก้ไข logic การแสดง badge "เกินกำหนด" ให้แสดงเฉพาะ loan batches ที่มี status เป็น `active` เท่านั้น**

**Issue:**

- ก่อนหน้านี้ระบบแสดง "เกินกำหนด" badge สำหรับทุก batch ที่เกินกำหนดคืน รวมถึง batch ที่มี status เป็น `completed` แล้ว
- การแสดงผลนี้ทำให้เกิดความสับสน เพราะ batch ที่คืนครบแล้วไม่ควรแสดงว่า "เกินกำหนด" อีก

**Changes:**

**Updated Views** (`loans/views.py`):

แก้ไข logic การคำนวณ `is_overdue` ใน 3 views:

- `my_loans_view()` - บรรทัด 28
- `active_loans_view()` - บรรทัด 184
- `loan_detail_view()` - บรรทัด 218

```python
# เดิม
batch.is_overdue = batch.due_date and batch.due_date < now

# แก้เป็น
batch.is_overdue = batch.status == 'active' and batch.due_date and batch.due_date < now
```

**Impact:**

- หน้า My Loans: แสดง "เกินกำหนด" เฉพาะ batch ที่ status = active และเลยกำหนดคืนแล้ว
- หน้า Active Loans (Admin): แสดง "เกินกำหนด" เฉพาะ batch ที่ status = active และเลยกำหนดคืนแล้ว
- หน้า Loan Detail (Admin): แสดง "เกินกำหนด" เฉพาะ batch ที่ status = active และเลยกำหนดคืนแล้ว
- Batch ที่เป็น `completed` แล้วจะไม่แสดง "เกินกำหนด" badge อีก

---

## [Enhancement] - 2026-04-04 - Loan Batch Status Field

### 📦 LoanBatch `status` Field

**เพิ่ม field `status` ในตาราง `loan_batches` เพื่อติดตามสถานะภาพรวมของการยืมแต่ละ batch**

**New Features:**

**1. `status` field บน `LoanBatch`**

- เพิ่ม 2 สถานะ:
  - `active` = ยังมีหนังสือที่ยังไม่คืน (default)
  - `completed` = คืนครบแล้ว หรือทุก item เป็น returned/lost
- สร้าง loan batch ใหม่จะมี `status = active` เสมอ (เป็น default)

**2. Auto-complete Batch**

- เมื่อ admin บันทึกการคืน (`mark_returned_view`) หรือบันทึกหนังสือหาย (`mark_lost_view`)
- ระบบตรวจสอบว่ายังมี loan item ที่สถานะ `borrowed` เหลือใน batch หรือไม่
- ถ้าไม่มีเหลือ → batch `status` เปลี่ยนเป็น `completed` อัตโนมัติ
- ใช้ `transaction.atomic()` เพื่อความปลอดภัยของข้อมูล

**3. Filter ใหม่หน้า Active Loans**

- เปลี่ยน filter จากสถานะของ `loan_items` มาเป็นสถานะของ `loan_batches`
- ตัวเลือก: **ทั้งหมด** / **Active** / **Completed**

**4. UI Updates**

- หน้า Active Loans: แสดง badge สถานะ (`Active` / `Completed`) ข้างชื่อ Loan Batch
- หน้า Loan Detail: แสดง badge สถานะของ batch ในส่วน "ข้อมูลการยืม"

**Changes:**

**Model Changes** (`loans/models.py`):

```python
class LoanBatch(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
```

**Migration:** `loans/migrations/0005_loanbatch_status.py`

**View Changes** (`loans/views.py`):

1. **Modified: `mark_returned_view`**

   ```python
   # After saving returned item:
   all_completed = not loan_batch.loan_items.filter(status='borrowed').exists()
   if all_completed:
       loan_batch.status = 'completed'
       loan_batch.save()
   ```

2. **Modified: `mark_lost_view`** (เช่นเดียวกับ mark_returned_view)

3. **Modified: `active_loans_view`**

   ```python
   # Before (filtered by loan_items.status)
   loan_batches.filter(loan_items__status=status_filter).distinct()

   # After (filtered by loan_batches.status)
   loan_batches.filter(status=status_filter)
   ```

**Template Changes:**

- `templates/loans/active_loans.html`:
  - เปลี่ยน dropdown ตัวเลือก filter เป็น `active` / `completed`
  - แสดง badge สถานะข้างชื่อ batch
- `templates/loans/loan_detail.html`:
  - เพิ่มแสดงสถานะ batch พร้อม badge ในการ์ด "ข้อมูลการยืม"

**Documentation:**

- ✅ อัพเดท `docs/data_dictionary.md` - เพิ่ม field `status` ในตาราง `loan_batches` พร้อม business rules
- ✅ อัพเดท `docs/ai-context.md` - อัพเดท section 6.3 (Loan Rules) และ 8.7 (Loan Management)

---

## [Enhancement] - 2026-03-26 - Admin Reservation Management with Auto-Rejection

### 🎯 Selective Confirmation & Auto-Rejection

**ปรับปรุงระบบยืนยันการจองให้ยืดหยุ่นและประหยัดเวลา**

**New Features:**

**1. Selective Confirmation with Stock Checking**

- Admin dashboard ที่ `/dashboard/reservations` แสดงรายละเอียดการจองแต่ละ batch
- แสดงสถานะสต็อกของหนังสือแต่ละเล่มแบบ real-time:
  - 🟢 **Green badge**: มีสต็อกพร้อมยืนยัน (X/Y available)
  - 🔴 **Red badge**: Out of Stock (0/Y)
- Checkbox สำหรับเลือกหนังสือที่จะยืนยัน:
  - เฉพาะหนังสือที่มีสต็อกสามารถเลือกได้
  - หนังสือที่หมดสต็อก → checkbox disabled
- "Select All" checkbox สำหรับเลือกทุกเล่มที่มีสต็อก

**2. Auto-Rejection for Unselected Books**

- **หนังสือที่ไม่ได้เลือก = ถูกยกเลิกอัตโนมัติ**
- Admin ไม่ต้องกด "Reject" ทีละเล่ม
- ลดขั้นตอนและป้องกันความผิดพลาด

**Example Workflow:**

```
การจองมี 5 หนังสือ:
- Book A (มีสต็อก) ✓ เลือก → Confirmed
- Book B (มีสต็อก) ✓ เลือก → Confirmed
- Book C (มีสต็อก) ✓ เลือก → Confirmed
- Book D (หมดสต็อก) ✗ ไม่เลือก → Cancelled (auto)
- Book E (หมดสต็อก) ✗ ไม่เลือก → Cancelled (auto)

ผลลัพธ์: "ดำเนินการสำเร็จ: ยืนยัน 3 เล่ม, ยกเลิก 2 เล่ม"
```

**3. Automatic Expiry Date Setting**

- เมื่อยืนยันการจอง → `expires_at` ถูก set อัตโนมัติ
- Default: ปัจจุบัน + 3 วัน (configurable via `RESERVATION_EXPIRY_DAYS`)
- User ต้องมารับหนังสือก่อนวันหมดอายุ
- หลังหมดอายุ → admin ควรยกเลิกและคืนสต็อก

**Changes:**

**Removed Features:**

- ❌ ลบปุ่ม "Reject" สำหรับหนังสือแต่ละเล่ม
- ❌ ลบ `admin_reject_reservation_item_view` function
- ❌ ลบ URL pattern สำหรับ reject action
- ❌ ลบ JavaScript function `rejectReservation()`
- ❌ ลบ hidden reject form

**Model Changes** (`reservations/models.py`):

```python
# Updated help_text
expires_at = models.DateTimeField(
    null=True,
    blank=True,
    help_text='Expiry time for confirmed reservation - user must pick up books before this time'
)
```

**View Changes** (`reservations/views.py`):

1. **Modified: `admin_confirm_selected_reservations_view`**

   ```python
   # New logic:
   - Get all pending reservations
   - Split into selected vs unselected
   - Confirm selected (if stock available)
   - Auto-reject unselected
   - Set expires_at = now() + timedelta(days=RESERVATION_EXPIRY_DAYS)
   - Update batch status
   ```

2. **Modified: `admin_confirm_reservation_view`**

   ```python
   # Add expires_at setting
   if has_confirmed:
       batch.status = 'confirmed'
       batch.expires_at = timezone.now() + timedelta(days=expiry_days)
       batch.save()
   ```

3. **Removed: `admin_reject_reservation_item_view`**
   - ไม่จำเป็นต้องใช้แล้วเพราะมี auto-rejection

**Template Changes** (`templates/reservations/reservation_detail.html`):

- ลบ Action column ออกจาก table
- ลบปุ่ม "Reject" ทั้งหมด
- ลบ hidden reject form
- ลบ JavaScript function สำหรับ rejection
- เน้นที่ checkbox selection เท่านั้น

**URL Changes** (`reservations/urls.py`):

```python
# Removed
- path('reservations/<int:batch_id>/reject/<int:reservation_id>/', ...)

# Kept
- path('reservations/<int:batch_id>/confirm-selected/', ...)
- path('reservations/<int:batch_id>/cancel/', ...)
```

**Message Updates:**

```python
# Success with breakdown
f'ดำเนินการสำเร็จ: ยืนยัน {confirmed_count} เล่ม, ยกเลิก {rejected_count} เล่ม'

# Stock warning
f'ไม่สามารถยืนยันหนังสือต่อไปนี้ได้ (สต็อคไม่พอ): {", ".join(insufficient_books)}'
```

**Benefits:**

✅ **ลดขั้นตอน**: ไม่ต้องกด reject ทีละเล่ม  
✅ **ป้องกันความผิดพลาด**: ไม่มีโอกาสลืม reject หนังสือที่หมดสต็อก  
✅ **UI สะอาดขึ้น**: ไม่มีปุ่ม reject เยอะแยะ  
✅ **ชัดเจนขึ้น**: เลือกเฉพาะที่ต้องการยืนยัน ที่เหลือยกเลิกอัตโนมัติ  
✅ **Expiry ถูกต้อง**: set อัตโนมัติจากเวลาที่ยืนยัน ไม่ใช่ตอนสร้าง  
✅ **User Experience**: แสดงวันหมดอายุที่ถูกต้อง (3 วันจากที่ยืนยัน)

**Documentation:**

- ✅ สร้าง `/docs/reservation-dashboard-guide.md` - คู่มือการใช้งาน admin dashboard
- ✅ อัพเดท `/docs/data_dictionary.md` - business rules สำหรับ expires_at
- ✅ อัพเดท `/docs/ai-context.md` - workflow การยืนยันการจอง

---

## [Enhancement] - 2026-03-26 - User Can Cancel Reservations & Admin-Controlled Expiry

### 🔄 Reservation Cancellation & Expiry Management

**ปรับปรุงระบบการจองให้มีความยืดหยุ่นมากขึ้น**

**New Features:**

**1. User Can Cancel Pending Reservations**

- เพิ่ม `can_be_cancelled_by_user()` method ใน ReservationBatch
- User สามารถยกเลิกการจองที่อยู่ในสถานะ `pending` เท่านั้น
- เมื่อยกเลิก:
  - เปลี่ยน batch status เป็น `cancelled`
  - เปลี่ยน reservation items ทั้งหมดเป็น `cancelled`
  - Transaction-safe with rollback
- UI: ปุ่มยกเลิกแสดงเฉพาะ pending batches
- Confirmation dialog ป้องกันการกดผิด

**2. Admin-Controlled Expiry Date**

- `expires_at` เปลี่ยนเป็น nullable field
- **ไม่** set expires_at ตอนที่ user สร้างการจอง
- Admin กำหนด expires_at ตอน **ยืนยัน** การจอง
- Default: 3 วันจากวันที่ยืนยัน (configurable via `RESERVATION_EXPIRY_DAYS`)
- แสดงข้อความ "รอเจ้าหน้าที่ยืนยันและกำหนดวันหมดอายุ" สำหรับ pending batches

**Changes:**

**Model Changes** (`reservations/models.py`):

```python
# Before
expires_at = models.DateTimeField()

# After
expires_at = models.DateTimeField(
    null=True,
    blank=True,
    help_text='Will be set by admin when confirming reservation'
)
```

- ปรับ `is_expired()`: ตรวจสอบ null ก่อน
- ปรับ `can_be_confirmed()`: ไม่ตรวจสอบ expiry (admin กำหนดตอนยืนยัน)
- เพิ่ม `can_be_cancelled_by_user()`: user ยกเลิกได้เฉพาะ pending

**View Changes**:

1. `books/views.py` - `confirm_cart_view`:
   - ไม่ set expires_at ตอนสร้าง ReservationBatch
   - ส่งข้อความเปลี่ยนเป็น "กรุณารอการยืนยันจากเจ้าหน้าที่" (ไม่มี "ภายใน 3 วัน")

2. `reservations/views.py` - NEW: `cancel_reservation_view`:
   - POST-only, login required
   - ตรวจสอบ ownership (user ยกเลิกได้เฉพาะของตัวเอง)
   - ตรวจสอบ `can_be_cancelled_by_user()`
   - Transaction atomic
   - Update batch และ items status

**Admin Changes** (`reservations/admin.py`):

- ลบ `save_model` override (ไม่ set expires_at ตอนสร้าง)
- อัปเดต `confirm_reservations` action:
  - Set `expires_at = timezone.now() + timedelta(days=expiry_days)`
  - Success message แสดงจำนวนวันหมดอายุ
  - Configurable via `settings.RESERVATION_EXPIRY_DAYS`

**Template Changes** (`templates/reservations/my_reservations.html`):

- แสดง expires_at เฉพาะเมื่อมีค่า (ยืนยันแล้ว)
- แสดง badge "รอเจ้าหน้าที่ยืนยัน" สำหรับ pending batches ที่ยังไม่มี expires_at
- เพิ่มปุ่ม "ยกเลิกการจอง" สำหรับ pending batches
- Confirmation dialog ก่อนยกเลิก
- คำอธิบาย: "คุณสามารถยกเลิกการจองที่ยังไม่ได้รับการยืนยันได้"

**URL Changes** (`reservations/urls.py`):

```python
path('<int:batch_id>/cancel/', views.cancel_reservation_view, name='cancel_reservation')
```

**Migration**:

- `reservations/migrations/0003_alter_reservationbatch_expires_at.py`
- เปลี่ยน expires_at เป็น nullable

**Benefits:**

✅ **User Flexibility**: ยกเลิกการจองที่ไม่ต้องการได้ (ก่อน admin ยืนยัน)  
✅ **Admin Control**: admin กำหนดระยะเวลาหมดอายุเองได้ตอนยืนยัน  
✅ **Future-Ready**: พร้อมสำหรับ dashboard ที่ให้ admin กำหนด expiry_days แบบ dynamic  
✅ **Clear Status**: แยกชัดเจนระหว่าง pending (ยังไม่มี expiry) และ confirmed (มี expiry)  
✅ **Reduced Confusion**: user ไม่เห็นวันหมดอายุจนกว่า admin จะยืนยัน

**Workflow:**

**Before:**

1. User สร้างการจอง → expires_at = now + 3 days
2. User เห็นวันหมดอายุทันที (แต่ยังไม่ได้ยืนยัน)
3. ไม่สามารถยกเลิกได้

**After:**

1. User สร้างการจอง → expires_at = null
2. แสดง "รอเจ้าหน้าที่ยืนยัน"
3. **User สามารถยกเลิกได้** (ถ้ายังเป็น pending)
4. Admin ยืนยัน → set expires_at = now + 3 days
5. User เห็นวันหมดอายุจริง

**Files Modified:**

- `reservations/models.py` - expires_at nullable, add can_be_cancelled_by_user()
- `reservations/views.py` - add cancel_reservation_view
- `reservations/urls.py` - add cancel URL
- `reservations/admin.py` - set expires_at on confirm
- `books/views.py` - don't set expires_at on create
- `templates/reservations/my_reservations.html` - add cancel button, conditional expiry display
- `reservations/migrations/0003_alter_reservationbatch_expires_at.py` - NEW

**Settings:**

เพิ่ม optional setting:

```python
RESERVATION_EXPIRY_DAYS = 3  # Default if not set
```

---

## [Feature] - 2026-03-26 - Shopping Cart System for Book Reservations

### 🛒 Shopping Cart Workflow (Phase 8 Enhancement)

**เปลี่ยนจากการจองทีละเล่ม เป็นระบบตะกร้าที่สามารถเลือกหนังสือหลายเล่มก่อนยืนยัน**

**New Features:**

**1. Cart Utility Class** (`books/cart.py`)

- Session-based cart system
- Methods: `add()`, `remove()`, `clear()`, `get_book_ids()`, `count()`
- Persistent across requests
- No database required for cart items

**2. Cart Views** (`books/views.py`)

- `add_to_cart_view`: เพิ่มหนังสือไปยังตะกร้า
  - ตรวจสอบ availability
  - ป้องกันการเพิ่มซ้ำ
  - Success/info messages
- `view_cart`: แสดงรายการหนังสือในตะกร้า
  - แสดงรูปปก, ชื่อ, ผู้แต่ง
  - แสดงสถานะ available/unavailable
  - Real-time availability check
- `remove_from_cart_view`: ลบหนังสือออกจากตะกร้า
- `confirm_cart_view`: ยืนยันการจองทั้งหมด
  - สร้าง ReservationBatch
  - สร้าง Reservation items หลายรายการ
  - Transaction-safe
  - ตรวจสอบ availability ทุกเล่มก่อน confirm
  - Clear cart หลังยืนยันสำเร็จ

**3. Cart Template** (`templates/books/cart.html`)

- Responsive cart page with Bootstrap 5
- Table แสดงรายการหนังสือ:
  - ปกหนังสือ (thumbnail)
  - ชื่อและปีพิมพ์
  - ผู้แต่ง (badges)
  - สถานะพร้อมยืม (color-coded)
  - ปุ่มลบ
- Summary card:
  - จำนวนหนังสือทั้งหมด
  - ระยะเวลาจอง (3 วัน)
  - หมายเหตุและเงื่อนไข
  - ปุ่มยืนยันการจอง (disabled ถ้ามีหนังสือไม่พร้อมยืม)
- Empty cart state with call-to-action
- Breadcrumb navigation

**4. Updated Book Detail Page**

- เปลี่ยนปุ่ม "จองหนังสือ" → "เพิ่มไปยังตะกร้า"
- เพิ่มปุ่ม "ดูตะกร้า"
- ข้อความแจ้งเตือนใหม่: "เพิ่มหนังสือหลายเล่มแล้วค่อยยืนยันการจอง"

**5. Navigation Bar Enhancement** (`templates/base.html`)

- เพิ่ม Cart icon พร้อม badge แสดงจำนวน
- Badge สีแดงแสดงจำนวนหนังสือในตะกร้า
- Real-time update (via context processor)
- ปรากฏเฉพาะเมื่อล็อกอินแล้ว

**6. Context Processor** (`books/context_processors.py`)

- ทำให้ `cart_count` พร้อมใช้ในทุก template
- เพิ่มใน `settings.py` TEMPLATES configuration

**7. URL Configuration** (`books/urls.py`)

- `cart/` - view cart
- `<id>/add-to-cart/` - add book to cart
- `<id>/remove-from-cart/` - remove book from cart
- `cart/confirm/` - confirm reservation
- `<id>/reserve/` - deprecated (backward compatibility)

**Technical Details:**

- Session-based storage (no cart model required)
- Transaction safety with `@transaction.atomic()`
- Select for update locking to prevent race conditions
- Query optimization: `select_related()`, `prefetch_related()`
- Comprehensive error handling
- User-friendly messages in Thai
- Bootstrap 5 responsive design
- Accessibility features (ARIA labels, semantic HTML)

**Business Flow:**

1. User คลิก "เพิ่มไปยังตะกร้า" ในหน้า Book Detail
2. หนังสือถูกเพิ่มไปยัง session cart
3. Badge ใน navbar แสดงจำนวน
4. User สามารถเพิ่มหนังสือหลายเล่ม
5. User คลิก "ตะกร้า" เพื่อดูรายการ
6. ระบบตรวจสอบ availability real-time
7. User สามารถลบหนังสือที่ไม่ต้องการ
8. User คลิก "ยืนยันการจอง"
9. ระบบสร้าง ReservationBatch + Reservation items ทั้งหมด
10. Cart ถูกล้าง
11. Redirect ไปหน้า My Reservations

**Files Modified:**

- `books/cart.py` - NEW: Cart utility class
- `books/context_processors.py` - NEW: Cart context processor
- `books/views.py` - เพิ่ม cart views, deprecate old reserve_book_view
- `books/urls.py` - เพิ่ม cart URLs
- `templates/books/cart.html` - NEW: Cart page template
- `templates/books/book_detail.html` - เปลี่ยนจาก "จอง" เป็น "เพิ่มไปยังตะกร้า"
- `templates/base.html` - เพิ่ม cart icon ใน navbar
- `config/settings.py` - เพิ่ม cart context processor

**Benefits:**

✅ Better UX - เลือกหนังสือหลายเล่มในครั้งเดียว
✅ Flexibility - สามารถแก้ไขรายการก่อนยืนยัน
✅ Transparency - เห็นสถานะ availability ชัดเจน
✅ Efficiency - ลด admin workload (1 batch มีหลาย items)
✅ Consistency - ทุกหนังสือในตะกร้ายืนยันพร้อมกัน

---

## [Feature] - 2026-03-26 - Member Reservation Functionality

### 🎉 Member Can Reserve Books (Phase 8 Final)

**New Features:**

**1. Book Reservation View**

- สร้าง `reserve_book_view` ใน `books/views.py`
- POST-only endpoint สำหรับจองหนังสือ
- Requires login (`@login_required`)
- Transaction-safe (uses `@transaction.atomic`)
- Validation:
  - ตรวจสอบ `available_quantity > 0`
  - ป้องกันการจองหนังสือที่ไม่มีให้ยืม
- สร้าง `ReservationBatch` อัตโนมัติ
  - Status: `pending`
  - Expires in 3 days
  - User: ผู้ที่ล็อกอินอยู่
- สร้าง `Reservation` item สำหรับหนังสือที่เลือก
- Success/error messages
- Redirect to My Reservations หลังจองสำเร็จ

**2. Updated Book Detail Page**

- เปลี่ยนปุ่ม "จองหนังสือ" จาก disabled เป็นใช้งานได้
- เพิ่ม form with CSRF protection
- POST to `/books/<id>/reserve/`
- แสดงข้อความแจ้งเตือน "การจองจะหมดอายุภายใน 3 วัน"
- UI แยกชัดเจนระหว่าง:
  - มีหนังสือให้ยืม → แสดงปุ่มจอง
  - ไม่มีหนังสือ → แสดงปุ่ม disabled
  - ยังไม่ล็อกอิน → แสดงปุ่ม login

**3. URL Configuration**

- เพิ่ม path ใหม่: `books/<int:book_id>/reserve/`
- Name: `books:reserve_book`
- Maps to `reserve_book_view`

**Technical Details:**

- Import dependencies: `timezone`, `timedelta`, `transaction`, `messages`
- Import models: `ReservationBatch`, `Reservation`
- Error handling ครบถ้วน
- User-friendly error messages ภาษาไทย

**Business Flow:**

1. Member คลิกปุ่ม "จองหนังสือ" ในหน้า Book Detail
2. ระบบตรวจสอบ available_quantity
3. สร้าง ReservationBatch (expires ใน 3 วัน)
4. สร้าง Reservation item เชื่อมกับหนังสือ
5. แสดง success message
6. Redirect ไปหน้า My Reservations
7. Admin ต้องยืนยันการจองภายใน 3 วัน
8. เมื่อ admin confirm → ลด available_quantity

**Files Modified:**

- `books/views.py` - เพิ่ม reserve_book_view
- `books/urls.py` - เพิ่ม reserve_book path
- `templates/books/book_detail.html` - เปลี่ยนปุ่มเป็น form
- `docs/ai-context.md` - อัปเดต Phase 8 status
- `docs/plan.md` - อัปเดต Phase 8 เป็น COMPLETED
- `docs/README-AI.md` - อัปเดต current phase

**Phase 8 Status:** ✅ **COMPLETED**

All member-facing features are now fully functional:

- ✅ Authentication (Register, Login, Logout)
- ✅ Home Page
- ✅ Book List with Search/Filter
- ✅ Book Detail with Reservation
- ✅ My Reservations
- ✅ My Loans
- ✅ My Fines
- ✅ **Member Reservation Workflow**

---

## [Feature] - 2026-03-26

### 🎉 User Registration System (Phase 8 - Authentication)

**New Features:**

**1. User Registration**

- สร้าง `UserRegistrationForm` พร้อม validation
  - Username validation (Django standard)
  - Email validation (required)
  - Password strength validation (min 8 chars)
  - Phone number validation (10 digits, numbers only)
  - First name / Last name (optional)
- สร้าง `/users/register/` endpoint
- Bootstrap 5 form styling
- Field-level error messages
- Success message หลังลงทะเบียนสำเร็จ
- Redirect ไป login page หลังสำเร็จ

**2. User Login**

- สร้าง `UserLoginForm` with Bootstrap styling
- สร้าง `/users/login/` endpoint
- Remember me checkbox
- Support "next" parameter for redirect after login
- Success/error messages
- Link to register page

**3. User Logout**

- สร้าง `/users/logout/` endpoint
- Requires login (`@login_required`)
- Success message
- Redirect to home

**4. Home Page**

- สร้าง responsive home page (`/`)
- Hero section with call-to-action
- Feature cards (ค้นหา, จอง, ติดตาม)
- Dynamic content based on authentication status
- Different UI for logged in vs guest users

**5. Base Template & Navigation**

- สร้าง `templates/base.html` with Bootstrap 5
- Responsive navbar with:
  - Logo and site name
  - Navigation links (visible when logged in)
  - User dropdown menu (profile, admin, logout)
  - Login/Register links (visible when guest)
- Message alerts with auto-dismiss
- Footer section

**Files Created:**

- `users/forms.py` - Registration and login forms
- `users/urls.py` - User authentication URLs
- `templates/base.html` - Base template with navbar
- `templates/home.html` - Home page
- `templates/users/register.html` - Registration form
- `templates/users/login.html` - Login form

**Files Modified:**

- `users/views.py` - Added authentication views
- `config/urls.py` - Include users URLs and home route
- `config/settings.py`:
  - Added `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`
  - Added `LOGIN_URL = 'login'`
  - Added `LOGIN_REDIRECT_URL = 'home'`
  - Added `LOGOUT_REDIRECT_URL = 'home'`

**Configuration:**

- Login URL: `/users/login/`
- Default redirect after login: home page
- Default redirect after logout: home page

**Benefits:**

- ✅ Member สามารถลงทะเบียนและเข้าสู่ระบบได้
- ✅ Form validation ครบถ้วน
- ✅ Responsive design พร้อมใช้งานบนมือถือ
- ✅ User-friendly error messages
- ✅ เตรียมพร้อมสำหรับ Phase 8 ต่อ (Book List, My Pages)

**Next Steps:**

- Book List Page
- Book Detail Page with Reserve button
- My Reservations Page
- My Loans Page
- My Fines Page

**Documentation Updated:**

- `docs/README-AI.md` - Updated progress
- `docs/plan.md` - Marked Phase 8.0 and 8.1 as completed
- `docs/ai-context.md` - Added authentication documentation

---

## [Enhancement] - 2026-03-25

### ✨ Admin Can Create Reservations for Users

**Issue:** Admin ไม่สามารถสร้างการจองแทน user ได้ เพราะ `has_add_permission` return False

**Changes:**

- เปลี่ยน `ReservationBatchAdmin.has_add_permission()` จาก `return False` เป็น `return True`
- เปลี่ยน `ReservationAdmin.has_add_permission()` จาก `return False` เป็น `return True`
- **เปลี่ยน `ReservationInline.has_add_permission()` เป็น `return True` เพื่อให้เพิ่มหนังสือได้ใน Reservation Batch โดยตรง**
- **ลบ `'book'` ออกจาก `readonly_fields` ใน ReservationInline เพื่อให้เลือกหนังสือได้**
- **เพิ่ม `autocomplete_fields = ['book']` ใน ReservationInline สำหรับค้นหาหนังสือได้ง่าย**
- **เปลี่ยน `extra = 1` ใน ReservationInline เพื่อแสดง empty form 1 แถว**
- เพิ่ม `has_delete_permission` ใน ReservationBatchAdmin (return False)
- เพิ่ม `save_model` override ใน ReservationBatchAdmin เพื่อตั้งค่า `expires_at` อัตโนมัติ
- **สร้าง config `RESERVATION_EXPIRY_DAYS = 3` ใน settings.py เพื่อง่ายต่อ maintenance และ reuse ได้**
- ปรับ readonly_fields ใน ReservationAdmin: ลบ `reservation_batch` และ `book` ออกเพื่อให้ admin เลือกได้
- เพิ่ม import `timezone`, `timedelta`, `settings` และ `Book` model

**Workflow:**

1. Admin ไปทื่ Reservation Batches → Add Reservation Batch
2. เลือก User ที่ต้องการจองให้
3. **เพิ่มหนังสือที่ต้องการจองได้ทันทีใน Inline table ข้างล่าง** (คลิกเลือก Book จาก dropdown)
4. กด Save (ระบบจะตั้ง expires_at อัตโนมัติ)
5. เมื่อพร้อม ใช้ admin action "Confirm selected reservations" เพื่อยืนยันการจอง

**ทางเลือก (ถ้าไม่อยากใช้ Inline):**

- ไปที่ Reservations → Add Reservation → เลือก Batch และ Book

**Benefits:**

- ✅ Admin สามารถสร้างการจองแทน user ได้ (use case: user โทรมาจอง, walk-in reservation)
- ✅ **สามารถเพิ่มหนังสือได้ทันทีในหน้า Reservation Batch เดียว ไม่ต้องไปหน้าอื่น**
- ✅ **ใช้ autocomplete ค้นหาหนังสือได้ง่ายและรวดเร็ว**
- ✅ ระบบตั้งค่า expires_at อัตโนมัติ (3 วัน)
- ✅ **จำนวนวันหมดอายุอยู่ใน settings.py เพื่อง่ายต่อ maintenance และ reuse**
- ✅ Admin ยังคงใช้ admin action ยืนยัน/ยกเลิกการจองได้เหมือนเดิม
- ✅ ป้องกันการลบ reservation batch (ใช้ cancel แทน)

**Technical Details:**

- `save_model` ตรวจสอบว่าเป็นการสร้างใหม่ (`not change`) ก่อนตั้งค่า expires_at
- **ใช้ `getattr(settings, 'RESERVATION_EXPIRY_DAYS', 3)` เพื่อดึงค่า config จาก settings และมี fallback เป็น 3**
- **ReservationInline ใช้ `autocomplete_fields` เพื่อค้นหาหนังสือแบบ realtime**
- **ตั้ง `extra = 1` เพื่อแสดง empty form 1 แถวสำหรับเพิ่มหนังสือ**
- `has_delete_permission` return False เพื่อบังคับใช้ workflow cancel
- Validation เดิมยังคงทำงาน (ตรวจสอบ available_quantity ก่อน confirm)

---

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
