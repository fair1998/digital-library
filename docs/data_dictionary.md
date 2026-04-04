# Data Dictionary: Digital Library System

This document describes the database schema for a digital library management system. The database consists of multiple tables that manage users, books, reservations, loans, and fines.

---

## Table: `users` (User Model)

**Base Model:** Django's built-in `AbstractUser` model (provides default authentication fields)

**Custom Fields Added:**

| Field          | Type        | Constraints | Description                                      |
| -------------- | ----------- | ----------- | ------------------------------------------------ |
| `phone_number` | varchar(10) | nullable    | User's phone number (10 digits) for contact info |

**Standard Django User Fields (Inherited):**

- `id`: Primary key (auto-increment integer)
- `username`: Unique username for login (varchar 150)
- `password`: Hashed password (varchar 128)
- `first_name`: User's first name (varchar 150)
- `last_name`: User's last name (varchar 150)
- `email`: Unique email address (varchar 254)
- `is_active`: Account active status (boolean, default True)
- `is_superuser`: Admin privileges flag (boolean, default False)
- `last_login`: Timestamp of last login (nullable)
- `date_joined`: Account creation timestamp (auto-set on creation)

**Purpose:** Stores all user accounts in the system, extending Django's built-in User model with phone number field

---

## Table: `books` (Book Catalog)

| Field                | Type         | Constraints                         | Description                                                        |
| -------------------- | ------------ | ----------------------------------- | ------------------------------------------------------------------ |
| `id`                 | int          | PK, increment                       | Primary key - Unique book identifier                               |
| `title`              | varchar(255) | not null                            | Book title                                                         |
| `description`        | text         | nullable                            | Book description or summary                                        |
| `image_url`          | varchar(255) | nullable                            | File path / URL to book cover image (stored by Django file fields) |
| `total_quantity`     | int          | not null, default `0`, check `>= 0` | Total copies of this book in the library (including borrowed ones) |
| `available_quantity` | int          | not null, default `0`, check `>= 0` | Number of copies currently available for borrowing or reservation  |
| `publish_year`       | int          | nullable, check `>= 0`              | Year the book was published                                        |
| `publisher_id`       | int          | FK -> `publishers.id`, nullable     | Foreign key reference to publisher                                 |
| `updated_at`         | timestamp    | default `now()`                     | Timestamp of last update                                           |
| `created_at`         | timestamp    | default `now()`                     | Timestamp when book was added to system                            |

**Purpose:** Stores all book records in the library system. Each book can have multiple copies tracked via `total_quantity` and `available_quantity`.

---

## Table: `authors` (Book Authors)

| Field        | Type         | Constraints     | Description                     |
| ------------ | ------------ | --------------- | ------------------------------- |
| `id`         | int          | PK, increment   | Primary key - Author identifier |
| `name`       | varchar(255) | not null        | Author's name                   |
| `updated_at` | timestamp    | default `now()` | Timestamp of last update        |
| `created_at` | timestamp    | default `now()` | Timestamp when author was added |

**Purpose:** Stores information about book authors. Authors have a many-to-many relationship with books via `book_authors` table.

---

## Table: `categories` (Book Categories)

| Field        | Type         | Constraints      | Description                                            |
| ------------ | ------------ | ---------------- | ------------------------------------------------------ |
| `id`         | int          | PK, increment    | Primary key - Category identifier                      |
| `name`       | varchar(255) | not null, unique | Category name (must be unique, e.g., Fiction, Science) |
| `updated_at` | timestamp    | default `now()`  | Timestamp of last update                               |
| `created_at` | timestamp    | default `now()`  | Timestamp when category was created                    |

**Purpose:** Stores book categories/genres. Books have a many-to-many relationship with categories via `book_categories` table.

---

## Table: `publishers` (Book Publishers)

| Field        | Type         | Constraints      | Description                        |
| ------------ | ------------ | ---------------- | ---------------------------------- |
| `id`         | int          | PK, increment    | Primary key - Publisher identifier |
| `name`       | varchar(255) | not null, unique | Publisher name (must be unique)    |
| `updated_at` | timestamp    | default `now()`  | Timestamp of last update           |
| `created_at` | timestamp    | default `now()`  | Timestamp when publisher was added |

**Purpose:** Stores information about book publishers. Referenced by books through `publisher_id` foreign key.

---

## Table: `book_authors` (Many-to-Many: Books ↔ Authors)

| Field       | Type | Constraints                  | Description                      |
| ----------- | ---- | ---------------------------- | -------------------------------- |
| `id`        | int  | PK, increment                | Primary key - Junction record ID |
| `book_id`   | int  | not null, FK -> `books.id`   | Foreign key reference to book    |
| `author_id` | int  | not null, FK -> `authors.id` | Foreign key reference to author  |

**Unique Constraint:** (`book_id`, `author_id`) - Prevents duplicate book-author pairs

**Purpose:** Junction table enabling many-to-many relationship between books and authors. One book can have multiple authors, and one author can write multiple books.

---

## Table: `book_categories` (Many-to-Many: Books ↔ Categories)

| Field         | Type | Constraints                     | Description                       |
| ------------- | ---- | ------------------------------- | --------------------------------- |
| `id`          | int  | PK, increment                   | Primary key - Junction record ID  |
| `book_id`     | int  | not null, FK -> `books.id`      | Foreign key reference to book     |
| `category_id` | int  | not null, FK -> `categories.id` | Foreign key reference to category |

**Unique Constraint:** (`book_id`, `category_id`) - Prevents duplicate book-category pairs

**Purpose:** Junction table enabling many-to-many relationship between books and categories. One book can belong to multiple categories, and one category can contain multiple books.

---

## Table: `reservation_batches` (Reservation Transactions)

| Field        | Type        | Constraints                                                                                      | Description                                                                                                                                                                        |
| ------------ | ----------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`         | int         | PK, increment                                                                                    | Primary key - Reservation batch identifier                                                                                                                                         |
| `user_id`    | int         | not null, FK -> `users.id`                                                                       | Foreign key to user who made the reservation                                                                                                                                       |
| `status`     | varchar(20) | not null, default `pending`, check (`pending`, `confirmed`, `completed`, `expired`, `cancelled`) | Batch status: `pending` = awaiting approval, `confirmed` = approved/pending pickup, `completed` = user picked up books, `expired` = pickup window expired, `cancelled` = cancelled |
| `expires_at` | timestamp   | **nullable**                                                                                     | Expiry time for confirmed reservation - **Automatically set to 3 days from confirmation when admin confirms reservation** (null for pending reservations awaiting confirmation)    |
| `updated_at` | timestamp   | default `now()`                                                                                  | Timestamp of last update                                                                                                                                                           |
| `created_at` | timestamp   | default `now()`                                                                                  | Timestamp when reservation batch was created                                                                                                                                       |

**Purpose:** Header/parent record for a single reservation transaction. One reservation batch can contain multiple books (stored in `reservations` table).

**Business Rules:**

- `expires_at` is **null** when user creates reservation (status = `pending`)
- Admin confirms reservation → `expires_at` is **automatically set** to 3 days from confirmation time (configurable via `RESERVATION_EXPIRY_DAYS` setting)
- เมื่อผู้ใช้มารับหนังสือแล้ว ให้เปลี่ยน `status` เป็น `completed`
- User must pick up books before `expires_at` or the reservation will be cancelled
- User can cancel reservation while status is `pending`
- Once confirmed, only admin can cancel

---

## Table: `reservations` (Individual Reserved Books)

| Field                  | Type        | Constraints                                                              | Description                                                                                 |
| ---------------------- | ----------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `id`                   | int         | PK, increment                                                            | Primary key - Individual reservation item identifier                                        |
| `book_id`              | int         | not null, FK -> `books.id`                                               | Foreign key to the book being reserved                                                      |
| `reservation_batch_id` | int         | not null, FK -> `reservation_batches.id`                                 | Foreign key to parent reservation batch                                                     |
| `status`               | varchar(20) | not null, default `pending`, check (`pending`, `confirmed`, `cancelled`) | Item status: `pending` = awaiting approval, `confirmed` = reserved, `cancelled` = cancelled |
| `updated_at`           | timestamp   | default `now()`                                                          | Timestamp of last update                                                                    |
| `created_at`           | timestamp   | default `now()`                                                          | Timestamp when reservation item was created                                                 |

**Purpose:** Child/detail records for individual books within a reservation batch. Each record represents one book reserved in a transaction.

---

## Table: `loan_batches` (Loan Transactions)

| Field        | Type        | Constraints                                               | Description                                                                                                      |
| ------------ | ----------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `id`         | int         | PK, increment                                             | Primary key - Loan batch identifier                                                                              |
| `user_id`    | int         | not null, FK -> `users.id`                                | Foreign key to user who borrowed the books                                                                       |
| `status`     | varchar(20) | not null, default `active`, check (`active`, `completed`) | Batch status: `active` = ยังมีหนังสือที่ยังไม่คืน, `completed` = คืนครบหรือสถานะทุกรายการเป็น returned/lost แล้ว |
| `due_date`   | timestamp   | nullable                                                  | Due date - when all books in this batch must be returned                                                         |
| `updated_at` | timestamp   | default `now()`                                           | Timestamp of last update                                                                                         |
| `created_at` | timestamp   | default `now()`                                           | Timestamp when loan batch was created                                                                            |

**Purpose:** Header/parent record for a single borrowing transaction. One loan batch can contain multiple books (stored in `loan_items` table).

**Business Rules:**

- `status` เริ่มต้นเป็น `active` เสมอเมื่อสร้างรายการยืมใหม่
- เมื่อ admin บันทึก returned หรือ lost ให้ loan item ใดก็ตาม ระบบจะตรวจสอบว่ายังมี item ที่สถานะเป็น `borrowed` เหลืออยู่หรือไม่
- ถ้าไม่มี `borrowed` item เหลือแล้ว → `status` ของ batch จะเปลี่ยนเป็น `completed` อัตโนมัติ
- หน้า Active Loans สามารถ filter ได้ด้วย status ของ batch (`active` / `completed`)

---

## Table: `loan_items` (Individual Borrowed Books)

| Field            | Type        | Constraints                                                          | Description                                                                                                                |
| ---------------- | ----------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `id`             | int         | PK, increment                                                        | Primary key - Individual loan item identifier                                                                              |
| `book_id`        | int         | not null, FK -> `books.id`                                           | Foreign key to the book being borrowed                                                                                     |
| `loan_batch_id`  | int         | not null, FK -> `loan_batches.id`                                    | Foreign key to parent loan batch                                                                                           |
| `reservation_id` | int         | nullable, **unique**, FK -> `reservations.id`                        | Foreign key to reservation (if this loan originated from a reservation) — **one reservation item can only be loaned once** |
| `status`         | varchar(20) | not null, default `borrowed`, check (`borrowed`, `returned`, `lost`) | Item status: `borrowed` = currently out, `returned` = returned, `lost` = lost/missing                                      |
| `returned_at`    | timestamp   | nullable                                                             | Actual return timestamp (null if not yet returned)                                                                         |
| `updated_at`     | timestamp   | default `now()`                                                      | Timestamp of last update                                                                                                   |
| `created_at`     | timestamp   | default `now()`                                                      | Timestamp when loan item was created                                                                                       |

**Purpose:** Child/detail records for individual books within a loan batch. Each record represents one book borrowed in a transaction. Links to `reservations` if the loan was made from a prior reservation.

---

## Table: `fines` (Library Fines/Penalties)

| Field          | Type          | Constraints                                          | Description                                                                      |
| -------------- | ------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------- |
| `id`           | int           | PK, increment                                        | Primary key - Fine record identifier                                             |
| `loan_item_id` | int           | not null, FK -> `loan_items.id`                      | Foreign key to loan item that incurred the fine                                  |
| `amount`       | decimal(10,2) | not null                                             | Fine amount in currency (2 decimal places)                                       |
| `type`         | varchar(20)   | not null, check (`late_return`, `lost`, `damaged`)   | Fine type: `late_return` = overdue, `lost` = book lost, `damaged` = book damaged |
| `reason`       | text          | nullable                                             | Additional details or notes about the fine                                       |
| `status`       | varchar(20)   | not null, default `unpaid`, check (`unpaid`, `paid`) | Payment status: `unpaid` = not yet paid, `paid` = paid                           |
| `paid_at`      | timestamp     | nullable                                             | Timestamp when fine was paid (null if unpaid)                                    |
| `updated_at`   | timestamp     | default `now()`                                      | Timestamp of last update                                                         |
| `created_at`   | timestamp     | default `now()`                                      | Timestamp when fine was created                                                  |

**Purpose:** Stores fines/penalties associated with loan items. Fines are created for late returns, lost books, or damaged books. Each fine is linked to a specific loan item.

---

## Database Relationships Summary

### Book-Related Relationships:

- `books.publisher_id` → `publishers.id` (Many books to one publisher)
- `book_authors.book_id` → `books.id` (Many-to-many junction)
- `book_authors.author_id` → `authors.id` (Many-to-many junction)
- `book_categories.book_id` → `books.id` (Many-to-many junction)
- `book_categories.category_id` → `categories.id` (Many-to-many junction)

### Reservation Workflow:

- `reservation_batches.user_id` → `users.id` (Many reservation batches per user)
- `reservations.book_id` → `books.id` (Each reservation item references a book)
- `reservations.reservation_batch_id` → `reservation_batches.id` (Many items in one batch)

### Loan Workflow:

- `loan_batches.user_id` → `users.id` (Many loan batches per user)
- `loan_items.book_id` → `books.id` (Each loan item references a book)
- `loan_items.loan_batch_id` → `loan_batches.id` (Many items in one batch)
- `loan_items.reservation_id` → `reservations.id` (Optional: links loan to original reservation)

### Fines:

- `fines.loan_item_id` → `loan_items.id` (Each fine is associated with a specific loan item)

---

## System Flow

1. **User Registration**: Users are managed via Django's built-in User model with custom `phone_number` field
2. **Book Catalog**: Books can have multiple authors and categories through junction tables
3. **Reservation Process**: Users create reservation batches containing multiple books, with expiration dates
4. **Loan Process**: Books can be borrowed either from reservations or directly. Loan batches track multiple books with a common due date
5. **Fine Management**: Overdue, lost, or damaged books generate fines that must be paid
