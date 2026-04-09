# UI/UX Theme Guide - Digital Library

> **เอกสารแนวทาง UI/UX สำหรับการ Refactor Templates**  
> เวอร์ชัน: 1.0 | อัปเดตล่าสุด: 10 เมษายน 2026

---

## 1. Design Vision

**"Modern, Minimal, Professional Library System"**

เป็นระบบห้องสมุดดิจิทัลที่ออกแบบให้ใช้งานง่าย อ่านสบายตา และดูมีความเป็นมืออาชีพ โดยไม่ต้องพึ่งพาการออกแบบที่หลากสีหรือ effect ซับซ้อน

**เป้าหมายหลัก:**

- **ใช้งานง่าย** - ผู้ใช้สามารถทำงานสำคัญได้ภายใน 2-3 คลิก
- **อ่านง่าย** - เนื้อหาและข้อมูลต้องชัดเจน hierarchy ดี
- **โหลดเร็ว** - ไม่ใช้ resource หนัก ไม่ใช้ภาพขนาดใหญ่เกินจำเป็น
- **ดูสะอาด** - whitespace พอเหมาะ ไม่รกตา ไม่แน่นเกินไป
- **Professional** - ดูน่าเชื่อถือ สำหรับใช้งานจริง

---

## 2. Brand Personality & Mood

**Personality:**

- **Professional** - ไว้ใจได้ สำหรับการใช้งานจริง
- **Approachable** - เข้าถึงง่าย ไม่ซับซ้อน
- **Clean** - เรียบง่าย ไม่มีสิ่งรบกวนสายตา
- **Efficient** - ตรงประเด็น ใช้งานคล่องตัว

**Mood & Tone:**

- **สงบ** - ไม่ใช้สีฉูดฉาด ไม่มี animation รบกวน
- **มั่นใจ** - ใช้ contrast ที่พอดี typography ที่ชัดเจน
- **เป็นระเบียบ** - alignment ดี spacing สม่ำเสมอ
- **เป็นมิตร** - ใช้ภาษาที่เข้าใจง่าย icon ช่วยสื่อความหมาย

---

## 3. Design Principles

### 3.1 Simplicity (ความเรียบง่าย)

- ลดองค์ประกอบที่ไม่จำเป็นออก
- แต่ละหน้า focus ที่งานหลักอย่างเดียว
- ไม่ใส่ decoration เกินจำเป็น

### 3.2 Hierarchy (ลำดับความสำคัญ)

- ใช้ขนาดตัวอักษร, น้ำหนัก, และสีเพื่อแยก level ของข้อมูล
- ข้อมูลสำคัญเด่นชัด ข้อมูลรองอ่อนลง (text-muted)
- หัวข้อต้องโดดเด่นกว่าเนื้อหา action button ต้องเห็นชัด

### 3.3 Consistency (ความสม่ำเสมอ)

- ใช้ class pattern เดียวกันในสถานการณ์เดียวกัน
- ระยะห่าง, ขนาดปุ่ม, สี, typography ต้องสม่ำเสมอทั้งเว็บ
- component ประเภทเดียวกันต้องดูเหมือนกัน

### 3.4 Whitespace (การใช้พื้นที่ว่าง)

- ไม่แน่นเกินไป - ให้เนื้อหาหายใจได้
- ใช้ margin/padding พอเหมาะ เพื่อแยก section
- card ต้องมี padding เพียงพอ ไม่ให้ content ชิดขอบ

### 3.5 Readability (อ่านง่าย)

- font size ต้องอ่านสบาย (base: 16px หรือ 1rem)
- line-height พอเหมาะ ไม่แน่น (1.5-1.6 สำหรับ paragraph)
- contrast ระหว่างข้อความกับพื้นหลังต้องชัด
- จำกัดความยาว line (max-width) สำหรับ paragraph ยาว

---

## 4. Color System

**หลักการ:** ใช้สีจากระบบ Bootstrap เป็นหลัก ไม่เพิ่มสีพิเศษเอง เน้นการใช้เฉพาะสีที่มีความหมาย

### 4.1 Primary Colors (สีหลัก)

**Primary (น้ำเงิน)**

- ใช้: navbar, ปุ่มหลัก, link สำคัญ, badge สถานะ active
- Class: `bg-primary`, `text-primary`, `btn-primary`
- **ห้าม:** ใช้ primary ทุกที่ - ใช้เฉพาะ action หลักเท่านั้น

**Secondary (เทา)**

- ใช้: ปุ่มรอง, text-muted, border เบา ๆ
- Class: `bg-secondary`, `text-secondary`, `btn-secondary`, `text-muted`

### 4.2 Semantic Colors (สีที่มีความหมาย)

**Success (เขียว)**

- ใช้: สถานะสำเร็จ, available, approved, completed
- Class: `bg-success`, `text-success`, `alert-success`, `badge bg-success`

**Warning (เหลือง)**

- ใช้: คำเตือนเบา ๆ, pending, กำลังดำเนินการ
- Class: `bg-warning`, `text-warning`, `alert-warning`, `badge bg-warning`

**Danger (แดง)**

- ใช้: error, overdue, rejected, delete action
- Class: `bg-danger`, `text-danger`, `alert-danger`, `btn-danger`

**Info (ฟ้า)**

- ใช้: ข้อมูลทั่วไป, notice, tips
- Class: `bg-info`, `text-info`, `alert-info`, `badge bg-info`

### 4.3 Neutral Colors (สีกลาง ๆ)

**White & Light**

- `bg-white` - card, form, modal background
- `bg-light` - section พื้นหลัง, footer, secondary highlight

**Dark & Muted**

- `text-dark` - ข้อความหลัก
- `text-muted` - ข้อความรอง, timestamp, metadata

### 4.4 สีที่ห้ามใช้

- ❌ gradient (ถ้าไม่จำเป็นจริง ๆ)
- ❌ สีสดจัด (neon, fluorescent)
- ❌ มากกว่า 3 สีในหน้าเดียว (ไม่นับ semantic colors)

---

## 5. Typography Guideline

**Font Family:**

```css
font-family: "Prompt", sans-serif;
```

- ใช้ Prompt สำหรับภาษาไทย (readable, modern, professional)
- เป็น fallback ที่ดีสำหรับภาษาอังกฤษด้วย

### 5.1 Headings

**H1 - Page Title**

- Class: `h1` หรือตั้งขนาดตรง
- Use case: หัวข้อหน้าหลัก
- Weight: `fw-bold` หรือ `fw-semibold`
- Margin bottom: `mb-3` หรือ `mb-4`

**H2 - Section Header**

- Class: `h2` หรือ `fs-3`
- Use case: แยก section ใหญ่
- Weight: `fw-semibold`
- Margin bottom: `mb-3`

**H3 - Subsection**

- Class: `h3` หรือ `fs-4`
- Use case: หัวข้อย่อย
- Weight: `fw-medium` หรือ `fw-semibold`
- Margin bottom: `mb-2`

**H4-H6**

- ใช้เมื่อจำเป็น ไม่ควรซ้อนลึกเกินไป

### 5.2 Body Text

**Default Text**

- ขนาด base: `1rem` (16px)
- Line height: `1.5` (default Bootstrap)
- Color: `text-dark` หรือ default

**Small Text**

- Class: `small` หรือ `fs-6`
- Use case: metadata, timestamp, caption
- สามารถใช้กับ `text-muted` ร่วมกัน

**Lead Text**

- Class: `lead`
- Use case: intro paragraph, highlight description

### 5.3 Font Weights

- `fw-bold` - ข้อความสำคัญมาก
- `fw-semibold` - headings, labels
- `fw-medium` - ปกติ
- `fw-normal` - default
- `fw-light` - decorative only (ใช้น้อย)

### 5.4 Typography Rules

✅ **ควรทำ:**

- ใช้ `text-muted` สำหรับ secondary information
- ใช้ heading hierarchy อย่างถูกต้อง (h1 > h2 > h3)
- align text ให้เหมาะสม (ปกติ `start`, title `center` ได้)

❌ **ห้าม:**

- uppercase ทั้งประโยค (ยกเว้น badge, label เล็ก ๆ)
- underline ธรรมดา (ใช้ได้แค่ link)
- italic มากเกินไป

---

## 6. Spacing Guideline

**ใช้ระบบ spacing ของ Bootstrap:**  
`0, 1, 2, 3, 4, 5` = `0, 0.25rem, 0.5rem, 1rem, 1.5rem, 3rem`

### 6.1 Common Patterns

**Page Container**

```html
<div class="container mt-4">
  <!-- เนื้อหา -->
</div>
```

**Section Spacing**

- ระหว่าง section ใหญ่: `mb-4` หรือ `mb-5`
- ระหว่าง card: `mb-3` หรือ `mb-4`
- ภายใน card body: padding default (1.25rem) หรือ `p-3`, `p-4`

**Form Spacing**

- ระหว่าง form group: `mb-3`
- ระหว่าง label กับ input: `mb-2` (default)

**Grid Spacing**

- Row gap: `g-3` หรือ `g-4` (ใช้กับ row)
- Gutter: `gx-3`, `gy-4` (ถ้าต้องการแยก horizontal/vertical)

### 6.2 Rules

✅ **ควร:**

- ใช้ `mt-4` ที่ top ของ main content
- ใช้ `mb-4` หรือ `mb-5` แยก section ใหญ่
- card ต้องมี `mb-3` เพื่อไม่ให้ติดกัน

❌ **ห้าม:**

- ใช้ spacing เกิน `5` (3rem) เว้นแต่กรณีพิเศษ
- ใช้ inline style `style="margin-top: 30px"` - ต้องใช้ class
- ทำให้ spacing ไม่สม่ำเสมอ

---

## 7. Border, Shadow, Card & Container

### 7.1 Border Radius

ใช้ default ของ Bootstrap (`.25rem` หรือ 4px):

- `rounded` - มุมโค้งปกติ (card, button, input)
- `rounded-circle` - กลม (avatar)
- `rounded-pill` - แคปซูล (badge, tag)
- `rounded-0` - ไม่มีมุมโค้ง (ใช้เมื่อต้องการ)

❌ **ห้าม** ปรับ border-radius เองเป็นค่าแปลก ๆ

### 7.2 Shadows

**ใช้เบา ๆ เท่านั้น:**

- `shadow-sm` - card hover, dropdown, form focus
- `shadow` - modal, important card
- ❌ **ห้าม** `shadow-lg` เว้นแต่เป็น overlay สำคัญมาก

**Hover Effect:**

```html
<div class="card shadow-sm hover-shadow"></div>
```

ใช้ hover เพิ่ม shadow เล็กน้อย (optional)

### 7.3 Cards

**Standard Card:**

```html
<div class="card shadow-sm mb-3">
  <div class="card-body">
    <h5 class="card-title">ชื่อ</h5>
    <p class="card-text">เนื้อหา</p>
  </div>
</div>
```

**Card with Image:**

```html
<div class="card h-100 shadow-sm">
  <img src="..." class="card-img-top" alt="..." />
  <div class="card-body d-flex flex-column">
    <h5 class="card-title">ชื่อ</h5>
    <p class="card-text">รายละเอียด</p>
    <div class="mt-auto">
      <a href="#" class="btn btn-primary">ดูรายละเอียด</a>
    </div>
  </div>
</div>
```

**Card Header/Footer** (ใช้เมื่อจำเป็น):

```html
<div class="card">
  <div class="card-header">Header</div>
  <div class="card-body">Content</div>
  <div class="card-footer text-muted">Footer</div>
</div>
```

### 7.4 Container

**Page Container:**

```html
<div class="container mt-4">
  <!-- ใช้ container สำหรับหน้าปกติ -->
</div>
```

**Full Width Section:**

```html
<section class="bg-light py-5">
  <div class="container">
    <!-- เนื้อหา -->
  </div>
</section>
```

---

## 8. UI Components Guideline

### 8.1 Buttons

**Primary Action:**

```html
<button class="btn btn-primary">บันทึก</button>
<button class="btn btn-primary">
  <i class="bi bi-check-circle"></i> ยืนยัน
</button>
```

**Secondary Action:**

```html
<button class="btn btn-secondary">ยกเลิก</button>
<button class="btn btn-outline-primary">ดูเพิ่มเติม</button>
```

**Danger Action (delete, remove):**

```html
<button class="btn btn-danger"><i class="bi bi-trash"></i> ลบ</button>
```

**Button Sizes:**

- `btn-sm` - ปุ่มเล็ก (ใช้ใน table row actions)
- `btn` - default
- `btn-lg` - ปุ่มใหญ่ (CTA สำคัญ)

**Button Groups:**

```html
<div class="btn-group" role="group">
  <button class="btn btn-outline-primary">ตัวเลือก 1</button>
  <button class="btn btn-outline-primary">ตัวเลือก 2</button>
</div>
```

**Rules:**

- ✅ icon + text ดีกว่า text อย่างเดียว (สำหรับ action สำคัญ)
- ✅ ใช้ `btn-primary` กับ action หลักเท่านั้น (1 ปุ่มต่อ 1 section)
- ❌ ห้ามใช้ `btn-primary` หลายปุ่มในพื้นที่เดียวกัน
- ❌ ห้ามใช้สีที่ไม่มีความหมาย (เช่น `btn-info` สำหรับ delete)

### 8.2 Badges

**Status Badges:**

```html
<span class="badge bg-success">active</span>
<span class="badge bg-warning">pending</span>
<span class="badge bg-danger">overdue</span>
<span class="badge bg-secondary">inactive</span>
```

**Count Badges:**

```html
<span class="badge rounded-pill bg-primary">5</span>
```

**Pill badges** ดีกว่า squared สำหรับ count/notification

### 8.3 Forms & Inputs

**Form Group:**

```html
<div class="mb-3">
  <label for="fieldName" class="form-label">ชื่อฟิลด์</label>
  <input
    type="text"
    class="form-control"
    id="fieldName"
    placeholder="กรอกข้อมูล"
  />
  <div class="form-text">คำแนะนำ (ถ้ามี)</div>
</div>
```

**Select:**

```html
<select class="form-select" id="selectField">
  <option selected>เลือก...</option>
  <option value="1">ตัวเลือก 1</option>
</select>
```

**Checkbox/Radio:**

```html
<div class="form-check">
  <input class="form-check-input" type="checkbox" id="check1" />
  <label class="form-check-label" for="check1"> ตัวเลือก </label>
</div>
```

**Rules:**

- ✅ ทุก input ต้องมี label
- ✅ ใช้ placeholder เป็น hint ไม่ใช่แทน label
- ✅ required field ควรมี `*` หรือระบุชัดเจน
- ❌ ห้ามใช้ `form-control-lg` หรือ `form-control-sm` เว้นแต่จำเป็น

### 8.4 Search Bar

**Simple Search:**

```html
<form method="get" class="mb-4">
  <div class="input-group">
    <input
      type="text"
      class="form-control"
      name="search"
      placeholder="ค้นหา..."
    />
    <button class="btn btn-primary" type="submit">
      <i class="bi bi-search"></i> ค้นหา
    </button>
  </div>
</form>
```

**Search with Filters:**

```html
<form method="get" class="row g-3">
  <div class="col-md-6">
    <input
      type="text"
      class="form-control"
      name="search"
      placeholder="ค้นหา..."
    />
  </div>
  <div class="col-md-3">
    <select class="form-select" name="category">
      <option value="">หมวดหมู่ทั้งหมด</option>
    </select>
  </div>
  <div class="col-md-3">
    <button type="submit" class="btn btn-primary w-100">
      <i class="bi bi-search"></i> ค้นหา
    </button>
  </div>
</form>
```

### 8.5 Tables

**Responsive Table:**

```html
<div class="table-responsive">
  <table class="table table-hover">
    <thead class="table-light">
      <tr>
        <th>คอลัมน์ 1</th>
        <th>คอลัมน์ 2</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>ข้อมูล 1</td>
        <td>ข้อมูล 2</td>
        <td>
          <a href="#" class="btn btn-sm btn-outline-primary">แก้ไข</a>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Rules:**

- ✅ ใช้ `table-responsive` เสมอ
- ✅ ใช้ `table-hover` เพื่อให้ hover effect
- ✅ thead ควรเป็น `table-light` เพื่อแยกจาก body
- ✅ action column ใช้ `btn-sm`

### 8.6 Empty State

```html
<div class="text-center py-5">
  <i class="bi bi-inbox display-1 text-muted"></i>
  <p class="lead text-muted mt-3">ไม่พบข้อมูล</p>
  <p class="text-muted">ลองค้นหาด้วยคำอื่น หรือเพิ่มข้อมูลใหม่</p>
  <a href="#" class="btn btn-primary mt-2">เพิ่มข้อมูล</a>
</div>
```

**Rules:**

- ต้องมี icon ขนาดใหญ่
- ข้อความอธิบายสั้น ๆ
- CTA button (ถ้ามี action ที่ทำได้)

### 8.7 Alerts

**Alert Types:**

```html
<div class="alert alert-success" role="alert">
  <i class="bi bi-check-circle"></i> บันทึกสำเร็จ
</div>

<div class="alert alert-warning" role="alert">
  <i class="bi bi-exclamation-triangle"></i> กรุณาตรวจสอบข้อมูล
</div>

<div class="alert alert-danger" role="alert">
  <i class="bi bi-x-circle"></i> เกิดข้อผิดพลาด
</div>

<div class="alert alert-info" role="alert">
  <i class="bi bi-info-circle"></i> ข้อมูลทั่วไป
</div>
```

**Dismissible Alert:**

```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
  <i class="bi bi-check-circle"></i> บันทึกสำเร็จ
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 8.8 Modals

```html
<div class="modal fade" id="exampleModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">ยืนยันการลบ</h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
        ></button>
      </div>
      <div class="modal-body">
        <p>คุณแน่ใจหรือไม่ว่าต้องการลบรายการนี้?</p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
          ยกเลิก
        </button>
        <button type="button" class="btn btn-danger">ลบ</button>
      </div>
    </div>
  </div>
</div>
```

**Rules:**

- ใช้ modal สำหรับ confirmation, quick form, detail view
- ❌ ห้ามใส่เนื้อหายาวเกินไปใน modal
- modal-footer: action ยกเลิกอยู่ซ้าย, action หลักอยู่ขวา

### 8.9 Pagination

```html
<nav aria-label="Page navigation">
  <ul class="pagination justify-content-center">
    <li class="page-item disabled">
      <a class="page-link" href="#" tabindex="-1">ก่อนหน้า</a>
    </li>
    <li class="page-item active"><a class="page-link" href="#">1</a></li>
    <li class="page-item"><a class="page-link" href="#">2</a></li>
    <li class="page-item"><a class="page-link" href="#">3</a></li>
    <li class="page-item">
      <a class="page-link" href="#">ถัดไป</a>
    </li>
  </ul>
</nav>
```

### 8.10 Breadcrumbs

```html
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="#">หน้าแรก</a></li>
    <li class="breadcrumb-item"><a href="#">รายการ</a></li>
    <li class="breadcrumb-item active" aria-current="page">รายละเอียด</li>
  </ol>
</nav>
```

---

## 9. Navbar, Footer, Page Header, Section Header

### 9.1 Navbar

**Structure:**

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <div class="container">
    <a class="navbar-brand fw-bold" href="/">
      <i class="bi bi-book"></i> Digital Library
    </a>
    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarNav"
    >
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a class="nav-link" href="#">หน้าแรก</a>
        </li>
      </ul>
      <ul class="navbar-nav">
        <!-- User menu -->
      </ul>
    </div>
  </div>
</nav>
```

**Rules:**

- ใช้ `navbar-dark bg-primary` สำหรับ navbar หลัก
- brand ควรมี icon
- mobile: ใช้ `navbar-toggler`
- แยก navigation ซ้าย (`me-auto`) กับ user menu ขวา

### 9.2 Footer

```html
<footer class="bg-light mt-5 py-4">
  <div class="container">
    <div class="row">
      <div class="col-md-6">
        <p class="text-muted mb-0">
          &copy; 2026 Digital Library. All rights reserved.
        </p>
      </div>
      <div class="col-md-6 text-md-end">
        <a href="#" class="text-muted text-decoration-none me-3">เกี่ยวกับ</a>
        <a href="#" class="text-muted text-decoration-none me-3">ติดต่อ</a>
        <a href="#" class="text-muted text-decoration-none">ความเป็นส่วนตัว</a>
      </div>
    </div>
  </div>
</footer>
```

**Rules:**

- `bg-light` พื้นหลังอ่อน
- `text-muted` สำหรับข้อความ
- ง่าย ๆ ไม่ซับซ้อน

### 9.3 Page Header

```html
<div class="container mt-4">
  <div class="row mb-4">
    <div class="col-md-8">
      <h1 class="mb-2">รายการหนังสือทั้งหมด</h1>
      <p class="text-muted">ค้นหาและจองหนังสือที่คุณสนใจ</p>
    </div>
    <div
      class="col-md-4 text-md-end d-flex align-items-center justify-content-md-end"
    >
      <a href="#" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> เพิ่มหนังสือ
      </a>
    </div>
  </div>
</div>
```

**Alternative (Simple):**

```html
<div class="container mt-4">
  <h1 class="mb-4">รายการหนังสือ</h1>
</div>
```

### 9.4 Section Header

```html
<div class="d-flex justify-content-between align-items-center mb-3">
  <h3 class="mb-0">หมวดหมู่ยอดนิยม</h3>
  <a href="#" class="btn btn-sm btn-outline-primary">ดูทั้งหมด</a>
</div>
```

---

## 10. List, Grid, Card Layout

### 10.1 Card Grid (สำหรับหนังสือ, สินค้า)

```html
<div class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
  {% for item in items %}
  <div class="col">
    <div class="card h-100 shadow-sm">
      <img src="..." class="card-img-top" alt="..." />
      <div class="card-body d-flex flex-column">
        <h5 class="card-title">{{ item.title }}</h5>
        <p class="card-text text-muted small">{{ item.author }}</p>
        <div class="mt-auto">
          <a href="#" class="btn btn-primary btn-sm w-100">ดูรายละเอียด</a>
        </div>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
```

**Rules:**

- `row-cols-*` responsive: 1 col บน mobile, 3 บน tablet, 4 บน desktop
- `g-4` gap สม่ำเสมอ
- `h-100` ให้ card สูงเท่ากัน
- `mt-auto` ดัน action button ลงล่างสุด

### 10.2 List Layout (รายการ transaction, logs)

```html
<div class="list-group">
  <a href="#" class="list-group-item list-group-item-action">
    <div class="d-flex w-100 justify-content-between">
      <h6 class="mb-1">ชื่อรายการ</h6>
      <small class="text-muted">3 วันที่แล้ว</small>
    </div>
    <p class="mb-1">คำอธิบาย</p>
    <small class="text-muted">ข้อมูลเพิ่มเติม</small>
  </a>
</div>
```

### 10.3 Table Layout (ข้อมูลแบบตาราง)

**ใช้เมื่อ:**

- ข้อมูลมีหลายคอลัมน์
- ต้องการเปรียบเทียบข้อมูล
- มี action หลายรายการ

---

## 11. Icon Usage (Bootstrap Icons)

### 11.1 Icon Guidelines

**ขนาด:**

- Default: `bi-*` (16px)
- Medium: `fs-5` หรือ `fs-4` ใช้ร่วมกับ icon
- Large: `display-1`, `display-2` สำหรับ empty state, hero

**สี:**

- `text-primary`, `text-success`, `text-danger`, `text-muted`

### 11.2 Common Icons

**Navigation & Actions:**

- `bi-house` - home
- `bi-search` - search
- `bi-plus-circle` - add, create
- `bi-pencil` - edit
- `bi-trash` - delete
- `bi-x` - close, cancel
- `bi-check` - confirm, success

**Status:**

- `bi-check-circle` - success, completed
- `bi-exclamation-triangle` - warning
- `bi-x-circle` - error, failed
- `bi-clock` - pending, waiting

**Library Specific:**

- `bi-book` - book
- `bi-book-fill` - book (filled)
- `bi-bookmark` - bookmark, save
- `bi-bookmark-check` - reserved, booked
- `bi-person` - user, author
- `bi-calendar` - date, schedule
- `bi-list-check` - list, checklist

**Rules:**

- ✅ ใช้ icon คู่กับข้อความสำคัญ (button, link)
- ✅ empty state ต้องมี icon ขนาดใหญ่
- ❌ ห้ามใช้ icon ที่ไม่ตรงความหมาย
- ❌ ห้ามใช้ icon มากเกินไปจนรก

---

## 12. UX Rules & States

### 12.1 Loading State

**Spinner:**

```html
<div class="text-center py-5">
  <div class="spinner-border text-primary" role="status">
    <span class="visually-hidden">กำลังโหลด...</span>
  </div>
  <p class="text-muted mt-3">กำลังโหลดข้อมูล...</p>
</div>
```

**Button Loading:**

```html
<button class="btn btn-primary" disabled>
  <span class="spinner-border spinner-border-sm me-2"></span>
  กำลังบันทึก...
</button>
```

### 12.2 Empty State

```html
<div class="text-center py-5">
  <i class="bi bi-inbox display-1 text-muted"></i>
  <p class="lead text-muted mt-3">ไม่พบข้อมูล</p>
  <p class="text-muted">คำแนะนำหรือคำอธิบาย</p>
  <a href="#" class="btn btn-primary">Action (ถ้ามี)</a>
</div>
```

### 12.3 Error State

**Inline Error:**

```html
<div class="mb-3">
  <label class="form-label">Email</label>
  <input type="email" class="form-control is-invalid" />
  <div class="invalid-feedback">กรุณากรอก email ที่ถูกต้อง</div>
</div>
```

**Page Error:**

```html
<div class="alert alert-danger">
  <i class="bi bi-x-circle"></i>
  <strong>เกิดข้อผิดพลาด</strong> ไม่สามารถโหลดข้อมูลได้
</div>
```

### 12.4 Success Feedback

**Toast Notification:**

```html
<div class="toast-container position-fixed top-0 end-0 p-3">
  <div class="toast show" role="alert">
    <div class="toast-header bg-success text-white">
      <i class="bi bi-check-circle me-2"></i>
      <strong class="me-auto">สำเร็จ</strong>
      <button
        type="button"
        class="btn-close btn-close-white"
        data-bs-dismiss="toast"
      ></button>
    </div>
    <div class="toast-body">บันทึกข้อมูลเรียบร้อยแล้ว</div>
  </div>
</div>
```

**Alert:**

```html
<div class="alert alert-success alert-dismissible">
  <i class="bi bi-check-circle"></i> บันทึกสำเร็จ
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 12.5 Confirmation Actions

**สำหรับ destructive actions (delete, remove):**

```html
<!-- Trigger Button -->
<button
  class="btn btn-danger"
  data-bs-toggle="modal"
  data-bs-target="#confirmModal"
>
  <i class="bi bi-trash"></i> ลบ
</button>

<!-- Confirmation Modal -->
<div class="modal fade" id="confirmModal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">ยืนยันการลบ</h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
        ></button>
      </div>
      <div class="modal-body">
        <p>
          คุณแน่ใจหรือไม่ว่าต้องการลบรายการนี้? การกระทำนี้ไม่สามารถย้อนกลับได้
        </p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
          ยกเลิก
        </button>
        <button type="button" class="btn btn-danger">ยืนยันการลบ</button>
      </div>
    </div>
  </div>
</div>
```

---

## 13. Responsive Guideline

### 13.1 Breakpoints (Bootstrap)

- **xs:** < 576px (mobile)
- **sm:** ≥ 576px
- **md:** ≥ 768px (tablet)
- **lg:** ≥ 992px (desktop)
- **xl:** ≥ 1200px
- **xxl:** ≥ 1400px

### 13.2 Responsive Patterns

**Grid:**

```html
<div class="row">
  <div class="col-12 col-md-6 col-lg-4">
    <!-- Full width บน mobile, ครึ่งบน tablet, 1/3 บน desktop -->
  </div>
</div>
```

**Text Alignment:**

```html
<div class="text-center text-md-start">
  <!-- Center บน mobile, left บน tablet ขึ้นไป -->
</div>
```

**Display:**

```html
<div class="d-none d-md-block">
  <!-- ซ่อนบน mobile, แสดงบน tablet ขึ้นไป -->
</div>
```

**Button/Flex:**

```html
<div class="d-grid d-md-flex gap-2">
  <!-- Stack บน mobile, horizontal บน tablet ขึ้นไป -->
  <button class="btn btn-primary">ปุ่ม 1</button>
  <button class="btn btn-secondary">ปุ่ม 2</button>
</div>
```

### 13.3 Mobile-First Rules

✅ **ควรทำ:**

- เริ่มออกแบบจาก mobile ก่อน
- ใช้ `col-12` เป็น default แล้วค่อย override ด้วย `col-md-*`
- ใช้ `.table-responsive` กับตาราง
- ทดสอบใน viewport เล็ก

❌ **ห้าม:**

- fixed width ที่ไม่ responsive
- ซ่อนข้อมูลสำคัญใน mobile
- ปุ่มเล็กเกินไปบน mobile (ควรใช้ `w-100` หรือ `d-grid`)

---

## 14. Accessibility Guideline

### 14.1 Color Contrast

- ข้อความต้องมี contrast ratio อย่างน้อย **4.5:1** กับพื้นหลัง
- ใช้ `text-dark` บน background สว่าง, `text-white` บน background เข้ม
- ❌ ห้ามใช้ text สีเทาอ่อน ๆ บนพื้นขาว (ใช้ `text-muted` แทน)

### 14.2 Focus States

- ทุก interactive element ต้อง focus ได้
- Bootstrap ใช้ outline ธรรมดา - **ห้ามปิด** `outline: none` เว้นแต่มี custom focus style แทน

### 14.3 Labels & ARIA

**Forms:**

```html
<label for="email" class="form-label">Email</label>
<input
  type="email"
  id="email"
  class="form-control"
  aria-describedby="emailHelp"
/>
<div id="emailHelp" class="form-text">ใส่ email ที่ใช้งานจริง</div>
```

**Buttons:**

```html
<button type="button" class="btn-close" aria-label="ปิด"></button>
```

**Icons (without text):**

```html
<button class="btn btn-primary" aria-label="ค้นหา">
  <i class="bi bi-search"></i>
</button>
```

### 14.4 Semantic HTML

✅ **ใช้:**

- `<nav>` สำหรับ navigation
- `<main>` สำหรับเนื้อหาหลัก
- `<header>`, `<footer>`, `<section>` ตามความเหมาะสม
- `<button>` สำหรับ action (not `<a>` ที่ไม่มี href)
- `<a>` สำหรับ link (ต้องมี href)

### 14.5 Alt Text

```html
<img src="book.jpg" alt="หนังสือเล่มนี้" />
```

ทุกภาพต้องมี alt (หรือ alt="" สำหรับ decorative image)

---

## 15. ข้อห้าม (Don'ts)

### 15.1 สี

❌ ห้ามใช้สีเกิน 3-4 สีหลักในหน้าเดียว (ไม่นับ semantic colors)  
❌ ห้ามใช้สีฉูดฉาด (neon, bright pink, bright yellow)  
❌ ห้ามใช้ gradient เยอะ (ถ้าใช้ ใช้เบา ๆ)  
❌ ห้ามใช้สีที่ไม่มีความหมาย (เช่น purple ไม่มีใน Bootstrap semantic)

### 15.2 Shadow & Effects

❌ ห้ามใช้ `shadow-lg` เว้นแต่เป็น modal/overlay  
❌ ห้ามใช้ `drop-shadow` หนัก  
❌ ห้ามใช้ `blur` filter (ทำให้โหลดช้า)  
❌ ห้ามใช้ `transform` ที่ซับซ้อน

### 15.3 Animation

❌ ห้ามใช้ animation ไม่จำเป็น (spinning text, bouncing button)  
❌ ห้ามใช้ `transition` นานเกิน 0.3s  
❌ ห้ามใช้ infinite animation เว้นแต่ loading spinner

### 15.4 Typography

❌ ห้าม uppercase ทั้งประโยค (ยกเว้น badge, label เล็ก ๆ)  
❌ ห้ามใช้ font เกิน 2 ตระกูล (ใช้ Prompt อย่างเดียว)  
❌ ห้าม font size เล็กกว่า 14px (ยกเว้น caption, metadata)

### 15.5 Layout

❌ ห้ามใช้ fixed width (px) เว้นแต่จำเป็น  
❌ ห้ามซ่อนข้อมูลสำคัญบน mobile  
❌ ห้ามให้ content ชิดขอบ (ต้องมี padding/margin)  
❌ ห้ามใช้ `!important` เว้นแต่จำเป็นจริง ๆ

### 15.6 General

❌ ห้ามใช้ไฟล์ภาพใหญ่เกิน 500KB (optimize ก่อน)  
❌ ห้ามใช้ external font หนัก ๆ (Google Fonts 1-2 weights enough)  
❌ ห้าม inline CSS (ยกเว้น case พิเศษ)  
❌ ห้ามใช้ deprecated HTML tags (`<center>`, `<font>`)

---

## 16. Bootstrap Class Patterns (ใช้ซ้ำ)

### 16.1 Card Standard

```html
<div class="card shadow-sm mb-3">
  <div class="card-body">...</div>
</div>
```

### 16.2 Button with Icon

```html
<button class="btn btn-primary"><i class="bi bi-plus-circle"></i> เพิ่ม</button>
```

### 16.3 Empty State

```html
<div class="text-center py-5">
  <i class="bi bi-inbox display-1 text-muted"></i>
  <p class="lead text-muted mt-3">ไม่พบข้อมูล</p>
</div>
```

### 16.4 Page Header with Action

```html
<div class="d-flex justify-content-between align-items-center mb-4">
  <h1 class="mb-0">หัวข้อ</h1>
  <a href="#" class="btn btn-primary">Action</a>
</div>
```

### 16.5 Form Group

```html
<div class="mb-3">
  <label for="id" class="form-label">Label</label>
  <input type="text" class="form-control" id="id" />
</div>
```

### 16.6 Badge Status

```html
<span class="badge bg-success">Active</span>
<span class="badge bg-warning text-dark">Pending</span>
<span class="badge bg-danger">Overdue</span>
```

### 16.7 Alert with Icon

```html
<div class="alert alert-success">
  <i class="bi bi-check-circle"></i> ข้อความ
</div>
```

### 16.8 Responsive Grid (4 columns)

```html
<div class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
  <div class="col">
    <div class="card h-100">...</div>
  </div>
</div>
```

### 16.9 List Group Item

```html
<div class="list-group">
  <a href="#" class="list-group-item list-group-item-action">
    <div class="d-flex justify-content-between">
      <span>ชื่อ</span>
      <small class="text-muted">time</small>
    </div>
  </a>
</div>
```

### 16.10 Modal Confirmation

```html
<div class="modal-footer">
  <button class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
  <button class="btn btn-danger">ยืนยัน</button>
</div>
```

---

## 17. Definition of Done (สำหรับการ Refactor แต่ละหน้า)

เมื่อ refactor template page แล้ว ต้องผ่านเกณฑ์เหล่านี้:

### ✅ Visual Quality

- [ ] ใช้ color system ตามที่กำหนด (primary, secondary, semantic)
- [ ] ใช้ spacing สม่ำเสมอ (mb-3, mb-4, g-3, g-4)
- [ ] typography hierarchy ชัดเจน (h1 > h2 > body)
- [ ] card มี shadow-sm และ spacing เหมาะสม
- [ ] ไม่มีสี/effect/animation ที่ไม่จำเป็น

### ✅ UX Quality

- [ ] ทุก state มีการจัดการ: loading, empty, error, success
- [ ] ปุ่ม action หลักชัดเจน (btn-primary 1 ปุ่มต่อ section)
- [ ] destructive actions มี confirmation
- [ ] ทุก form ใช้งานได้ และมี validation feedback
- [ ] ทุก icon มีความหมายตรงกับ context

### ✅ Responsive

- [ ] ใช้ responsive grid (row-cols-\*)
- [ ] ทดสอบใน mobile/tablet/desktop
- [ ] ไม่มี horizontal scroll (ยกเว้น table-responsive)
- [ ] ปุ่มใช้งานง่ายบน mobile (ขนาดพอดี, spacing เพียงพอ)

### ✅ Accessibility

- [ ] ทุก input มี label
- [ ] ทุกภาพมี alt
- [ ] button ที่มีแต่ icon ต้องมี aria-label
- [ ] color contrast ผ่านเกณฑ์
- [ ] focus state ใช้งานได้

### ✅ Code Quality

- [ ] ใช้ Bootstrap classes เป็นหลัก
- [ ] ไม่มี inline CSS (ยกเว้นจำเป็น)
- [ ] ไม่มี !important
- [ ] class names สม่ำเสมอกับหน้าอื่น ๆ
- [ ] semantic HTML ถูกต้อง

### ✅ Performance

- [ ] ไม่มีภาพขนาดใหญ่เกิน 500KB
- [ ] ไม่มี external resource ที่ไม่จำเป็น
- [ ] ไม่มี animation/transition หนัก

---

## 18. เมื่อต้อง Refactor Template ให้ตัดสินใจอย่างไร

### ขั้นตอนการคิด

**1. ทำความเข้าใจหน้า**

- หน้านี้มีหน้าที่อะไร? (list, detail, form, dashboard)
- action หลักคืออะไร? (add, search, view, edit)
- ข้อมูลอะไรสำคัญที่สุด?

**2. วาง Layout หลัก**

- ใช้ container หรือ container-fluid?
- แบ่ง section อย่างไร? (header, filter, content, footer)
- responsive breakpoint: mobile 1 col, tablet 2-3 col, desktop 4 col?

**3. เลือก Components**

- ข้อมูลแสดงแบบ card, list, หรือ table?
- form ใช้ layout แบบไหน? (1 column, 2 columns, inline)
- ต้องมี search/filter ไหม?
- ต้องมี pagination ไหม?

**4. กำหนด Hierarchy**

- h1 สำหรับ page title
- h2-h3 สำหรับ section header
- เน้น action หลักด้วย btn-primary (1 ปุ่มต่อ section)
- secondary info ใช้ text-muted, small

**5. ใส่ States**

- empty state: แสดง icon + message + CTA
- loading state: spinner + text
- error state: alert-danger
- success state: alert-success หรือ toast

**6. ตรวจสอบ Accessibility**

- label ครบไหม?
- alt text ครบไหม?
- aria-label สำหรับ icon-only button?
- color contrast ดีไหม?

**7. ทดสอบ Responsive**

- ลองย่อ browser เป็น mobile size
- ทุกอย่างอ่านได้ ใช้งานได้ไหม?
- ปุ่มกดง่ายไหม?

**8. ปรับแต่งสุดท้าย**

- spacing สม่ำเสมอไหม?
- alignment ถูกต้องไหม?
- มีอะไรไม่จำเป็นให้ลบออก

---

## สรุป

เอกสารนี้เป็น **practical guideline** สำหรับการทำ UI/UX refactor ของโปรเจกต์ Digital Library

**หลักการหลัก:**

1. **Modern Minimal Clean** - เรียบง่าย ไม่ซับซ้อน
2. **Bootstrap-first** - ใช้ Bootstrap classes เป็นหลัก
3. **Consistent** - ใช้ pattern เดียวกันทั้งเว็บ
4. **Accessible** - ใช้งานได้สำหรับทุกคน
5. **Functional** - เน้นใช้งานจริง ไม่ใช่แค่สวย

**เมื่อสงสัย:**

- เลือกทางที่เรียบง่ายกว่า
- ลดสิ่งที่ไม่จำเป็นออก
- เน้น function มากกว่า decoration
- ถามว่า "ผู้ใช้ได้ประโยชน์อะไร?"

---

**จัดทำโดย:** Digital Library Team  
**ใช้สำหรับ:** AI-driven UI/UX Refactoring  
**อัปเดต:** 10 เมษายน 2026
