# Shopping Cart System Documentation

## Overview

ระบบตะกร้าจองหนังสือ (Shopping Cart) สำหรับให้ member เลือกหนังสือหลายเล่มก่อนยืนยันการจองในคครั้งเดียว

## Architecture

### Session-Based Storage

- ใช้ Django session เก็บรายการหนังสือในตะกร้า
- ไม่ต้องสร้าง model แยกสำหรับ cart
- Persistent ตลอดการใช้งาน (จนกว่าจะ logout หรือ clear cart)

### Cart Class (`books/cart.py`)

```python
class Cart:
    def __init__(self, request)
    def add(self, book_id)
    def remove(self, book_id)
    def clear(self)
    def get_book_ids(self)
    def count(self)
```

**Session Structure:**

```json
{
  "cart": {
    "1": { "book_id": 1 },
    "5": { "book_id": 5 },
    "12": { "book_id": 12 }
  }
}
```

## Workflow

### 1. Add to Cart

1. User คลิกปุ่ม "เพิ่มไปยังตะกร้า" ในหน้า Book Detail
2. ระบบตรวจสอบ `available_quantity > 0`
3. เรียก `cart.add(book_id)`
4. แสดง success message
5. Badge ใน navbar อัปเดตทันที

### 2. View Cart

1. User คลิก Cart icon ใน navbar
2. ระบบ query หนังสือทั้งหมดจาก `cart.get_book_ids()`
3. ตรวจสอบ availability real-time
4. แสดงรายการพร้อมสถานะ (มี/ไม่มีให้ยืม)
5. แสดง summary และปุ่มยืนยัน

### 3. Remove from Cart

1. User คลิกปุ่มลบในหน้า Cart
2. เรียก `cart.remove(book_id)`
3. แสดง success message
4. Reload cart page

### 4. Confirm Reservation

1. User คลิก "ยืนยันการจอง"
2. ระบบตรวจสอบ availability ทุกเล่ม (with `select_for_update()`)
3. ถ้ามีหนังสือไม่พร้อมยืม → แสดง error
4. สร้าง `ReservationBatch` (expires ใน 3 วัน)
5. สร้าง `Reservation` items สำหรับทุกเล่ม
6. เรียก `cart.clear()`
7. แสดง success message
8. Redirect ไป My Reservations

## Views

### `add_to_cart_view(request, book_id)`

- POST only
- Login required
- ตรวจสอบ availability
- เพิ่มไปยัง session cart

### `view_cart(request)`

- GET
- Login required
- Query books from cart IDs
- Check availability real-time
- แสดง cart template

### `remove_from_cart_view(request, book_id)`

- POST only
- Login required
- ลบออกจาก session cart

### `confirm_cart_view(request)`

- POST only
- Login required
- Transaction atomic
- Select for update (prevent race condition)
- สร้าง ReservationBatch + Reservations
- Clear cart

## URLs

```python
path('cart/', views.view_cart, name='view_cart')
path('<int:book_id>/add-to-cart/', views.add_to_cart_view, name='add_to_cart')
path('<int:book_id>/remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart')
path('cart/confirm/', views.confirm_cart_view, name='confirm_cart')
```

## Templates

### `templates/books/cart.html`

**Components:**

- Breadcrumb navigation
- Cart items table:
  - Book cover thumbnail
  - Title and year
  - Authors (badges)
  - Availability status (color-coded)
  - Remove button
- Summary card:
  - Total books count
  - Reservation duration (3 days)
  - Terms and conditions
  - Confirm button (disabled if unavailable books exist)
- Empty cart state

### `templates/base.html` (navbar)

**Cart Icon:**

```html
<a class="nav-link position-relative" href="{% url 'books:view_cart' %}">
  <i class="bi bi-cart3"></i> ตะกร้า {% if cart_count > 0 %}
  <span class="badge rounded-pill bg-danger">{{ cart_count }}</span>
  {% endif %}
</a>
```

## Context Processor

### `books/context_processors.py`

```python
def cart_context(request):
    cart = Cart(request)
    return {'cart_count': cart.count()}
```

**เพิ่มใน settings.py:**

```python
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            ...
            'books.context_processors.cart_context',
        ],
    },
}]
```

## Security Considerations

### Race Conditions

- ใช้ `select_for_update()` ตอน confirm
- Wrap ใน `transaction.atomic()`
- ตรวจสอบ availability ก่อน commit

### Session Security

- Cart เป็น session-based → ต้อง login
- แต่ละ user มี cart แยกกัน
- Session expire ตาม Django settings

### Validation

- ตรวจสอบ availability ทุกจุดที่สำคัญ:
  - Add to cart
  - View cart (real-time check)
  - Confirm reservation
- ป้องกันการจองหนังสือที่ไม่มีให้ยืม

## UX Features

### Visual Feedback

- ✅ Success messages เมื่อเพิ่ม/ลบ/ยืนยัน
- ❌ Error messages เมื่อไม่สามารถดำเนินการได้
- ℹ️ Info messages เมื่อหนังสืออยู่ในตะกร้าแล้ว
- 🔴 Badge แสดงจำนวนหนังสือ real-time
- 🚫 Disabled button เมื่อมีหนังสือไม่พร้อมยืม

### Responsive Design

- Mobile-friendly table
- Sticky summary card
- Bootstrap 5 grid system
- Icon + text for better UX

### Accessibility

- ARIA labels
- Semantic HTML
- Color + text (not color alone)
- Keyboard navigation support

## Benefits

| Feature         | Before (Single Book) | After (Shopping Cart)         |
| --------------- | -------------------- | ----------------------------- |
| Selection       | 1 เล่มต่อครั้ง       | หลายเล่มต่อครั้ง              |
| Workflow        | จอง → รอ admin       | เลือกหลายเล่ม → จองครั้งเดียว |
| Flexibility     | ไม่สามารถแก้ไข       | แก้ไขได้ก่อนยืนยัน            |
| Admin Work      | หลาย batches         | 1 batch (หลาย items)          |
| User Experience | กดจองซ้ำหลายรอบ      | จองครั้งเดียวจบ               |

## Future Enhancements

### Possible Improvements

- [ ] เพิ่มจำนวนเล่มต่อหนังสือ (quantity per book)
- [ ] Save for later (wishlist)
- [ ] Auto-remove unavailable books option
- [ ] Cart expiration (auto-clear after X days)
- [ ] Share cart (for group reservations)
- [ ] Email cart items

### Performance Optimization

- [ ] Cache cart count
- [ ] Lazy load book images
- [ ] Pagination for large carts

## Testing Checklist

### Manual Testing

- [ ] เพิ่มหนังสือไปยังตะกร้า
- [ ] เพิ่มหนังสือเดิมซ้ำ (ควรแสดง info message)
- [ ] ดูตะกร้า (แสดงรายการถูกต้อง)
- [ ] ลบหนังสือออกจากตะกร้า
- [ ] ยืนยันการจองด้วยหนังสือที่มีให้ยืม
- [ ] ยืนยันการจองด้วยหนังสือที่ไม่มีให้ยืม (ควร error)
- [ ] ตรวจสอบ badge count อัปเดตถูกต้อง
- [ ] ตรวจสอบ cart ว่างเปล่า (แสดง empty state)
- [ ] ทดสอบบน mobile/tablet

### Edge Cases

- [ ] Cart ว่าง → กด confirm (ควรแจ้งเตือน)
- [ ] หนังสือหมดระหว่างอยู่ใน cart
- [ ] Session expire ระหว่างใช้งาน
- [ ] เพิ่มหนังสือหลายเล่มพร้อมกัน (race condition)
- [ ] Logout → cart ถูกเคลียร์

## Troubleshooting

### Cart count ไม่อัปเดต

- ตรวจสอบ context processor ใน settings.py
- ตรวจสอบ `cart.save()` ถูกเรียกหรือไม่

### หนังสือหายจาก cart

- ตรวจสอบ session settings
- ตรวจสอบ `SESSION_COOKIE_AGE`

### Confirm ล้มเหลว

- ตรวจสอบ transaction error log
- ตรวจสอบ available_quantity
- ตรวจสอบ database locks

## Related Files

```
books/
├── cart.py                    # Cart utility class
├── context_processors.py      # Cart context processor
├── views.py                   # Cart views
├── urls.py                    # Cart URLs
templates/books/
├── cart.html                  # Cart page
└── book_detail.html           # Add to cart button
templates/
└── base.html                  # Cart icon in navbar
config/
└── settings.py                # Context processor config
```
