# Admin Reservation Dashboard Guide

## Overview

Admin dashboard ที่ `/dashboard/reservations` ช่วยให้เจ้าหน้าที่สามารถจัดการการจองของ user ได้อย่างมีประสิทธิภาพ โดยสามารถเลือกยืนยันเฉพาะหนังสือที่มีสต็อกเท่านั้น

## การเข้าถึง Dashboard

- **URL**: `/dashboard/reservations`
- **Permission**: Staff members only (`@staff_member_required`)
- **Navigation**: Sidebar → Reservations

## ฟีเจอร์หลัก

### 1. Reservation List View

แสดงรายการ reservation batches ทั้งหมดพร้อมข้อมูลสำคัญ:

- User ที่จอง
- จำนวนหนังสือในการจอง
- สถานะ (Pending/Confirmed/Cancelled)
- วันที่สร้าง
- วันหมดอายุ (สำหรับ confirmed reservations)

**ฟิลเตอร์สถานะ:**

- All - ทุกสถานะ
- Pending - รอยืนยัน
- Confirmed - ยืนยันแล้ว
- Cancelled - ยกเลิกแล้ว

### 2. Reservation Detail View

แสดงรายละเอียดการจอง 1 batch พร้อม:

#### User Information Card

- Username
- Full name
- Email
- Created date
- Expiry date (ถ้ายืนยันแล้ว)
- Total books

#### Books List Table

แสดงหนังสือแต่ละเล่มพร้อม:

| Column             | Description                                     |
| ------------------ | ----------------------------------------------- |
| Checkbox           | สำหรับเลือกหนังสือที่จะยืนยัน (เฉพาะที่มีสต็อก) |
| Book Title         | ชื่อหนังสือ + ISBN                              |
| Author             | ชื่อผู้แต่ง                                     |
| Publisher          | สำนักพิมพ์                                      |
| Stock Status       | 🟢 Available / 🔴 Out of Stock                  |
| Reservation Status | Pending/Confirmed/Cancelled                     |

**Stock Status Indicators:**

- 🟢 **Green Badge**: มีสต็อกพร้อมยืนยัน - แสดงจำนวน "X/Y available"
- 🔴 **Red Badge**: Out of Stock - ไม่สามารถยืนยันได้

## Workflow การยืนยันการจอง

### สถานการณ์: การจองมี 5 หนังสือ แต่มีสต็อกเพียง 3 เล่ม

```
Step 1: Admin เปิด Reservation Detail
┌────────────────────────────────────────────────────┐
│ Reservation #123 - john_doe                        │
├────────────────────────────────────────────────────┤
│ ☑ Select All                                       │
├────────────────────────────────────────────────────┤
│ ☑  Book A    🟢 3/5 available      Pending         │
│ ☑  Book B    🟢 1/2 available      Pending         │
│ ☑  Book C    🟢 2/3 available      Pending         │
│ ☐  Book D    🔴 0/1 Out of Stock   Pending         │
│ ☐  Book E    🔴 0/2 Out of Stock   Pending         │
└────────────────────────────────────────────────────┘

Step 2: Admin เลือกเฉพาะหนังสือที่มีสต็อก
- Book A, B, C ถูกเลือก (checkbox checked)
- Book D, E ไม่ได้เลือก (ไม่มีสต็อก)

Step 3: Admin กด "Confirm Selected Books"

Step 4: ระบบดำเนินการ (atomic transaction):
✅ Book A → status = 'confirmed', stock ลดลง 1
✅ Book B → status = 'confirmed', stock ลดลง 1
✅ Book C → status = 'confirmed', stock ลดลง 1
❌ Book D → status = 'cancelled' (auto-rejected)
❌ Book E → status = 'cancelled' (auto-rejected)
✅ Batch expires_at = now() + 3 days
✅ Batch status = 'confirmed'

Step 5: แสดงผลลัพธ์
✅ "ดำเนินการสำเร็จ: ยืนยัน 3 เล่ม, ยกเลิก 2 เล่ม"
```

## ฟีเจอร์สำคัญ

### 1. Auto-Rejection สำหรับหนังสือที่ไม่เลือก

**เดิม (ปัญหา):**

- Admin ต้องกด Reject ทีละเล่มสำหรับหนังสือที่ไม่มีสต็อก
- ใช้เวลานานและเสี่ยงต่อความผิดพลาด

**ใหม่ (แก้ไข):**

- เลือกเฉพาะที่ต้องการยืนยัน
- ที่เหลือ = ยกเลิกอัตโนมัติ
- ประหยัดเวลาและลดข้อผิดพลาด

### 2. Stock Checking

```python
# ระบบตรวจสอบสต็อกก่อนยืนยัน
if book.available_quantity > 0:
    # ✅ สามารถยืนยันได้
    reservation.status = 'confirmed'
    book.available_quantity -= 1
else:
    # ❌ ไม่สามารถยืนยัน (checkbox disabled)
    # จะถูก auto-reject ถ้าไม่เลือก
```

### 3. Automatic Expiry Setting

```python
# เมื่อยืนยันการจอง
expiry_days = settings.RESERVATION_EXPIRY_DAYS  # default: 3
batch.expires_at = timezone.now() + timedelta(days=expiry_days)
```

**User ต้องมารับหนังสือภายใน 3 วัน**

- หลังจากนั้น admin ควรยกเลิกและคืนสต็อก

### 4. Batch Status Logic

```python
if has_confirmed_items:
    batch.status = 'confirmed'
elif all_items_cancelled:
    batch.status = 'cancelled'
else:
    batch.status = 'pending'  # ยังมีบางเล่มรอดำเนินการ
```

## Actions ที่มีให้

### สำหรับ Pending Batches:

1. **Confirm Selected Books** - ยืนยันหนังสือที่เลือก + auto-reject ที่ไม่เลือก
2. **Cancel All** - ยกเลิกการจองทั้งหมด

### สำหรับ Confirmed Batches:

1. **Cancel This Reservation** - ยกเลิกและคืนสต็อก

## Best Practices

### ✅ Do's

- ตรวจสอบ stock status ก่อนยืนยันเสมอ
- เลือกเฉพาะหนังสือที่มีสต็อกจริง
- ใช้ "Select All" เฉพาะเมื่อทุกเล่มมีสต็อก
- ติดตามวันหมดอายุของการจองที่ยืนยันแล้ว

### ❌ Don'ts

- ห้ามยืนยันหนังสือที่ Out of Stock (checkbox disabled อยู่แล้ว)
- ห้าม refresh หน้าระหว่างกดยืนยัน (เสี่ยง duplicate)
- ห้ามลืมเช็ค expires_at หลังยืนยัน

## Messages และการแจ้งเตือน

### Success Messages

```
✅ "ดำเนินการสำเร็จ: ยืนยัน 3 เล่ม, ยกเลิก 2 เล่ม"
✅ "ยืนยันการจอง #123 สำเร็จ (5 เล่ม, User: john_doe)"
```

### Warning Messages

```
⚠️ "กรุณาเลือกหนังสือที่ต้องการยืนยัน"
⚠️ "ไม่สามารถยืนยันหนังสือต่อไปนี้ได้ (สต็อคไม่พอ): Book D, Book E"
```

### Error Messages

```
❌ "ไม่สามารถยืนยันการจอง #123 ได้ (สถานะ: Confirmed)"
❌ "เกิดข้อผิดพลาด: [error message]"
```

## Technical Details

### URLs

```python
# List view
/dashboard/reservations/

# Detail view
/dashboard/reservations/<batch_id>/

# Actions
/dashboard/reservations/<batch_id>/confirm-selected/  # POST
/dashboard/reservations/<batch_id>/cancel/            # POST
```

### Permissions

```python
@staff_member_required
def admin_reservation_detail_view(request, batch_id):
    # Only staff members can access
```

### Transaction Safety

```python
with transaction.atomic():
    # ทุกอย่างใน block นี้จะ commit พร้อมกัน
    # หรือ rollback ทั้งหมดถ้าเกิด error
```

## Configuration

### Settings

```python
# config/settings.py
RESERVATION_EXPIRY_DAYS = 3  # วันหมดอายุหลังยืนยัน
```

### Customization

ถ้าต้องการเปลี่ยนจำนวนวัน:

```python
RESERVATION_EXPIRY_DAYS = 7  # เปลี่ยนเป็น 7 วัน
```

## Troubleshooting

### ปัญหา: ไม่เห็นปุ่ม Confirm

**สาเหตุ:** Batch status ไม่ใช่ 'pending'  
**วิธีแก้:** ตรวจสอบสถานะ - Confirmed/Cancelled batches ไม่สามารถยืนยันซ้ำได้

### ปัญหา: Checkbox disabled ทั้งหมด

**สาเหตุ:** ไม่มีหนังสือเล่มใดที่มีสต็อก  
**วิธีแก้:** ต้องยกเลิกการจองนี้ หรือรอจนมีสต็อก

### ปัญหา: กด Confirm แล้ว หนังสือบางเล่มไม่ถูกยืนยัน

**สาเหตุ:** หนังสือเหล่านั้นไม่ได้ถูกเลือก (checkbox unchecked)  
**ผลลัพธ์:** ถูก auto-reject แล้ว (ตามที่ออกแบบไว้)

## Summary

Admin Reservation Dashboard ช่วยให้การจัดการการจองมีประสิทธิภาพด้วย:

1. ✅ **เลือกยืนยันได้เฉพาะที่มีสต็อก** - checkbox disabled สำหรับ out of stock
2. ✅ **Auto-reject unselected** - ไม่ต้องกด reject ทีละเล่ม
3. ✅ **Auto-set expires_at** - กำหนดวันหมดอายุอัตโนมัติ (3 วัน)
4. ✅ **Transaction-safe** - ไม่มี partial updates
5. ✅ **Clear indicators** - แยกสีชัดเจนระหว่างมีสต็อก/หมดสต็อก
6. ✅ **Informative messages** - บอกผลลัพธ์ชัดเจน

---

**Last Updated:** 2026-03-26  
**Version:** 1.0
