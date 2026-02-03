### QUERY

#### Table User
```sql
-- Tabel users (tanpa kolom role)
create table users (
	id SERIAL primary key,
	name varchar (100) not null,
	email varchar (150) unique not null,
	password varchar (255) not null,
	parent_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- NULL = bukan anak
	created_at TIMESTAMP default CURRENT_TIMESTAMP,
	updated_at TIMESTAMP default CURRENT_TIMESTAMP,
	is_active BOOLEAN default true 
);

-- Index untuk email (pencarian cepat saat login)
CREATE INDEX idx_users_email ON users(email);

CREATE INDEX idx_users_active ON users(is_active);

CREATE VIEW users_with_role AS
SELECT 
    u.*,
    CASE 
        WHEN u.parent_id IS NOT NULL THEN 'child'
        WHEN EXISTS (SELECT 1 FROM users WHERE parent_id = u.id) THEN 'parent'
        ELSE 'user'
    END AS role_type,
    (SELECT COUNT(*) FROM users WHERE parent_id = u.id) AS child_count
FROM users u;

SELECT * FROM users_with_role;

ALTER TABLE users 
ADD COLUMN role VARCHAR(50) DEFAULT 'user';

ALTER TABLE users 
ADD CONSTRAINT check_role_valid CHECK (role IN ('admin', 'user'));

```

#### Table Categories
```SQL 

-- Categories table (normalized for data integrity)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,          -- e.g., 'Shopping', 'Gaji', 'Transport'
    type VARCHAR(10) NOT NULL,          -- 'income' or 'expense'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, type)                  -- Prevent duplicate category names per type
);
```

#### Table Transactions
``` sql
-- Main transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,  -- Actual transaction date (not creation timestamp)
    description TEXT,
    payment_method VARCHAR(50),          -- e.g., 'cash', 'transfer', 'credit_card'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------

ALTER TABLE transactions 
ADD COLUMN budget_id INTEGER REFERENCES child_budgets(id) ON DELETE SET NULL;
```

#### Table Child
``` SQL
-- Tabel budget (hanya untuk relasi parent → child)
CREATE TABLE child_budgets (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    period VARCHAR(20) NOT NULL DEFAULT 'monthly',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_parent_child_different CHECK (parent_id != child_id),
    -- ✅ Hanya foreign key biasa, tanpa subquery
    CONSTRAINT fk_parent FOREIGN KEY (parent_id) REFERENCES users(id),
    CONSTRAINT fk_child FOREIGN KEY (child_id) REFERENCES users(id)
);
```

#### Sisa budget saat ini untuk budget_id = 1
```
SELECT 
    cb.amount - COALESCE(SUM(t.amount), 0) AS remaining
FROM child_budgets cb
LEFT JOIN transactions t ON t.budget_id = cb.id
WHERE cb.id = 1
GROUP BY cb.id, cb.amount;
```

