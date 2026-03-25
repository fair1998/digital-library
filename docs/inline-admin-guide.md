# Django Admin Inline Guide - ManyToMany with Through Models

## ปัญหา: Fields ไม่แสดงในฟอร์ม

### Symptom

เมื่อเพิ่ม Book ใหม่ใน Django Admin **ไม่มี fields สำหรับเลือก Authors และ Categories** เลย

### Root Cause

#### Book Model Structure

```python
class Book(models.Model):
    # ... other fields ...

    authors = models.ManyToManyField(
        "Author",
        through="BookAuthor",  # ← ใช้ intermediate model
        related_name="books",
    )
    categories = models.ManyToManyField(
        "Category",
        through="BookCategory",  # ← ใช้ intermediate model
        related_name="books",
    )
```

#### Why Fields Don't Show Up

เมื่อ ManyToMany field ใช้ `through` parameter:

- ❌ Django **ไม่สามารถสร้าง form field อัตโนมัติ**
- ❌ ไม่สามารถใช้ `filter_horizontal` ได้
- ❌ ไม่สามารถใช้ `autocomplete_fields` โดยตรงได้
- ❌ ต้องจัดการผ่าน intermediate model แทน

**เหตุผล:**

- ManyToMany ธรรมดา: Django สร้างตารางเชื่อมอัตโนมัติ
- ManyToMany แบบ `through`: เราสร้างตารางเชื่อมเอง (BookAuthor, BookCategory)
- ตารางเชื่อมอาจมี fields เพิ่มเติม (เช่น date_added, order)
- Django ไม่รู้ว่าจะกำหนดค่า fields เหล่านั้นอย่างไร จึงไม่สร้าง form ให้

---

## วิธีแก้: ใช้ Inline Model Admin

### Solution Overview

แทนที่จะแก้ไข authors/categories โดยตรงใน Book form:

- สร้าง **Inline Admin** สำหรับ BookAuthor และ BookCategory
- แสดงเป็นตารางใต้ Book form
- แก้ไข relationships แบบ inline ได้ทันที

### Implementation

#### Step 1: สร้าง Inline Classes

```python
# books/admin.py

class BookAuthorInline(admin.TabularInline):
    """Inline admin for managing book-author relationships"""
    model = BookAuthor  # intermediate model
    extra = 1  # จำนวนแถวว่างที่แสดง (สำหรับเพิ่มใหม่)
    autocomplete_fields = ("author",)  # มีปุ่ม "+" สำหรับเพิ่ม author ใหม่

class BookCategoryInline(admin.TabularInline):
    """Inline admin for managing book-category relationships"""
    model = BookCategory  # intermediate model
    extra = 1  # จำนวนแถวว่างที่แสดง
    autocomplete_fields = ("category",)  # มีปุ่ม "+" สำหรับเพิ่ม category ใหม่
```

**TabularInline vs StackedInline:**

- `TabularInline`: แสดงเป็นตาราง (compact, เหมาะกับ fields น้อย)
- `StackedInline`: แสดงเป็น fieldset (เหมาะกับ fields เยอะ)

#### Step 2: เพิ่ม Inlines ใน BookAdmin

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # ... other configurations ...

    inlines = [BookAuthorInline, BookCategoryInline]

    # ลบ authors และ categories ออกจาก autocomplete_fields
    # เพราะจัดการผ่าน inlines แล้ว
    autocomplete_fields = ("publisher",)  # เหลือแค่ publisher
```

---

## UI ที่ได้

### Form Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Add Book                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Title: [___________________________________]                 │
│                                                              │
│ Description: [________________________________]              │
│                                                              │
│ Publisher: [Select publisher... ▼] [🟢 +]                  │
│                                                              │
│ Total quantity: [__]                                         │
│ Available quantity: [__]                                     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ BOOK AUTHORS                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Book          Author                            Delete       │
│ ──────────────────────────────────────────────────────────  │
│ [auto]   [Select author... ▼] [🟢 +]      [ ]              │
│ [auto]   [                 ▼] [🟢 +]      [ ]  ← extra row  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ BOOK CATEGORIES                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Book          Category                          Delete       │
│ ──────────────────────────────────────────────────────────  │
│ [auto]   [Select category... ▼] [🟢 +]    [ ]              │
│ [auto]   [                   ▼] [🟢 +]    [ ]  ← extra row  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
│ [Save and add another] [Save and continue editing] [Save]   │
└─────────────────────────────────────────────────────────────┘
```

### การใช้งาน

#### เพิ่ม Author ให้หนังสือ

1. **เลือกจาก dropdown:**
   - คลิกที่ Author field ในแถว inline
   - พิมพ์ชื่อเพื่อค้นหา (autocomplete)
   - เลือกจาก dropdown

2. **เพิ่ม Author ใหม่:**
   - คลิกปุ่ม "🟢 +" ข้าง Author field
   - Popup เปิดขึ้นมา
   - กรอกชื่อ Author → Save
   - Popup ปิด, Author ใหม่ถูกเลือกอัตโนมัติ

3. **เพิ่มหลาย Authors:**
   - แถวแรก: เลือก Author A
   - แถวที่สอง (extra row): เลือก Author B
   - Django จะเพิ่มแถวว่างใหม่ให้อัตโนมัติ

4. **ลบ Author:**
   - เช็ค checkbox "Delete" ในแถวที่ต้องการลบ
   - กด Save

---

## Inline Configuration Options

### Basic Options

```python
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor

    # จำนวนแถวว่างที่แสดง
    extra = 1  # default: 3

    # จำนวนแถวว่างเพิ่มเติมเมื่อแก้ไข
    max_num = 10  # จำกัดจำนวนสูงสุด
    min_num = 1   # จำนวนขั้นต่ำที่ต้องมี

    # ซ่อนแถวว่างเมื่อมีข้อมูลครบแล้ว
    # extra = 0  # ไม่แสดงแถวว่าง (ต้องกด "Add another" เอง)
```

### Field Configuration

```python
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor

    # กำหนด fields ที่แสดง
    fields = ("author",)  # แสดงเฉพาะ author

    # หรือใช้ autocomplete
    autocomplete_fields = ("author",)

    # readonly fields
    readonly_fields = ("created_at",)

    # ซ่อน fields
    exclude = ("id",)
```

### Display Options

```python
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor

    # แสดง verbose name
    verbose_name = "Author"
    verbose_name_plural = "Authors"

    # เรียงลำดับ
    ordering = ("author__name",)

    # แสดง fieldsets (ใช้กับ StackedInline)
    # fieldsets = (...)
```

### Permissions

```python
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor

    # ปิดการเพิ่ม
    def has_add_permission(self, request, obj=None):
        return False

    # ปิดการลบ
    def has_delete_permission(self, request, obj=None):
        return False

    # ปิดการแก้ไข
    def has_change_permission(self, request, obj=None):
        return False
```

---

## Advanced: Inline with Extra Fields

### Scenario: BookAuthor มี field เพิ่มเติม

```python
class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # ← เพิ่ม field
    order = models.IntegerField(default=0)  # ← เพิ่ม field
```

### Inline Configuration

```python
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1
    autocomplete_fields = ("author",)

    # แสดง fields เพิ่มเติม
    fields = ("author", "role", "order")

    # หรือใช้ fieldsets (สำหรับ StackedInline)
    # fieldsets = (
    #     (None, {
    #         'fields': ('author', 'role', 'order')
    #     }),
    # )
```

### UI Result

```
BOOK AUTHORS
Book    Author                    Role          Order    Delete
──────────────────────────────────────────────────────────────
[auto]  [John Doe      ▼] [+]   [Main Author] [1]      [ ]
[auto]  [Jane Smith    ▼] [+]   [Co-Author  ] [2]      [ ]
[auto]  [              ▼] [+]   [           ] [0]      [ ]
```

---

## เปรียบเทียบแนวทาง

### 1. ไม่ใช้ Through Model (ManyToMany ธรรมดา)

```python
class Book(models.Model):
    authors = models.ManyToManyField("Author")
```

**Admin:**

```python
class BookAdmin(admin.ModelAdmin):
    filter_horizontal = ("authors",)
    # หรือ
    autocomplete_fields = ("authors",)
```

**✅ Pros:**

- ง่าย setup ง่าย
- มี widget พร้อมใช้

**❌ Cons:**

- ไม่สามารถเก็บข้อมูลเพิ่มเติมใน relationship (role, order)
- ไม่ยืดหยุ่น

### 2. ใช้ Through Model + Inline Admin

```python
class Book(models.Model):
    authors = models.ManyToManyField("Author", through="BookAuthor")
```

**Admin:**

```python
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    autocomplete_fields = ("author",)

class BookAdmin(admin.ModelAdmin):
    inlines = [BookAuthorInline]
```

**✅ Pros:**

- ยืดหยุ่น เก็บข้อมูลเพิ่มได้
- ควบคุม relationship ได้ดี
- เหมาะกับระบบที่ซับซ้อน

**❌ Cons:**

- ต้อง setup inline
- code เยอะขึ้นเล็กน้อย

---

## Troubleshooting

### Inline ไม่แสดง

**Symptom:** Inline section ไม่ปรากฏในฟอร์ม

**Possible Causes:**

1. ❌ ลืมเพิ่ม `inlines = [...]` ใน BookAdmin
2. ❌ Inline class ไม่ได้ inherit จาก `TabularInline` หรือ `StackedInline`
3. ❌ `model` ไม่ได้ชี้ไปที่ intermediate model

**Fix:**

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookAuthorInline, BookCategoryInline]  # ✅ เพิ่มบรรทัดนี้
```

### ปุ่ม "+" ไม่แสดง

**Symptom:** Autocomplete dropdown แสดง แต่ไม่มีปุ่ม "+"

**Possible Causes:**

1. ❌ Related Admin ไม่มี `search_fields`
2. ❌ User ไม่มี permission เพิ่ม Author/Category

**Fix:**

```python
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ("name",)  # ✅ จำเป็นสำหรับ autocomplete
```

### Inline ซ้ำซ้อน

**Symptom:** มีหลายแถวของ Author เดียวกัน

**Cause:** ไม่มี unique constraint

**Fix:**

```python
class BookAuthor(models.Model):
    # ...
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["book", "author"],
                name="unique_book_author"
            )
        ]
```

---

## Best Practices

### 1. ใช้ TabularInline สำหรับ Simple Relationships

```python
class BookAuthorInline(admin.TabularInline):  # ✅ compact
    model = BookAuthor
```

### 2. ใช้ StackedInline สำหรับ Complex Forms

```python
class OrderItemInline(admin.StackedInline):  # ใช้เมื่อมี fields เยอะ
    model = OrderItem
```

### 3. จำกัดจำนวนแถว

```python
class BookAuthorInline(admin.TabularInline):
    extra = 1        # แสดง 1 แถวว่าง
    max_num = 5      # จำกัดสูงสุด 5 authors
```

### 4. ใช้ Autocomplete สำหรับข้อมูลเยอะ

```python
class BookAuthorInline(admin.TabularInline):
    autocomplete_fields = ("author",)  # ✅ ดีกว่า dropdown ธรรมดา
```

### 5. เพิ่ม Verbose Names

```python
class BookAuthorInline(admin.TabularInline):
    verbose_name = "Author"
    verbose_name_plural = "Authors"  # แสดงในหัวตาราง
```

---

## Summary

### ปัญหา

- ManyToMany with `through` model → Django ไม่สร้าง form field อัตโนมัติ

### วิธีแก้

- ใช้ **Inline Model Admin** (TabularInline หรือ StackedInline)

### ประโยชน์

- ✅ จัดการ relationships แบบ inline ได้
- ✅ มีปุ่ม "+" สำหรับเพิ่มรายการใหม่
- ✅ รองรับ fields เพิ่มเติมใน relationship
- ✅ UI ชัดเจน เห็นภาพรวมได้ดี

### Code Pattern

```python
# 1. Create Inline
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1
    autocomplete_fields = ("author",)

# 2. Add to Parent Admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookAuthorInline, BookCategoryInline]
```

**Result:** Admin สามารถเพิ่ม/แก้ไข Authors และ Categories ได้ทันทีในหน้า Book form! 🎉
