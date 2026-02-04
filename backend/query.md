### QUERY

#### Table User
```sql
-- Tabel users (tanpa kolom role)
-- Struktur users tetap sederhana
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    parent_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- ✅ Cukup ini saja!
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
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

-- Step 1: Parent buat invitation (temporary table)
CREATE TABLE child_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id INTEGER NOT NULL REFERENCES users(id),
    child_email VARCHAR(150) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'accepted', 'expired'
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '7 days',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Anak terima email → klik link → buat akun
INSERT INTO users (name, email, password, role, parent_id) VALUES
('Ani', 'ani@email.com', 'hashed_new_pwd', 'user', 1);  -- parent_id langsung di-set

-- Step 3: Update invitation status
UPDATE child_invitations SET status = 'accepted' WHERE id = '...';

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
    name VARCHAR(50) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    scope VARCHAR(20) DEFAULT 'personal' CHECK (scope IN ('personal', 'business', 'both')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, type, scope)  -- Hindari duplikat
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



### business Model
Membuat Modal bisnis
```
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,           -- "Jualan Gorengan", "Dropship Baju", dll
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'inactive'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_businesses_user ON businesses(user_id);
```

```
CREATE TABLE business_capitals (
    id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    description TEXT,
    capital_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_business_capitals_business ON business_capitals(business_id);
```


```
CREATE TABLE business_transactions (
    id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),  -- ✅ Reuse categories existing
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_business_transactions_business ON business_transactions(business_id);
CREATE INDEX idx_business_transactions_date ON business_transactions(transaction_date);
```