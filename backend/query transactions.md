### Query Transactions

```
-- Admin
INSERT INTO users (name, email, password, role, parent_id) VALUES
(
	'Super Admin', 
	'admin@finance.com', 
	'$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', -- password: admin123
	'admin', 
NULL);

-- Orang tua
INSERT INTO users (name, email, password, role, parent_id) VALUES
(
	'Budi', 
	'budi@email.com', 
	'$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', -- password: admin123
	'user', 
NULL);

-- Anak
INSERT INTO users (name, email, password, role, parent_id) VALUES
(
	'Ani', 
	'ani@email.com', 
	'$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', -- password: admin123
	'user', 
2);

-- User biasa
INSERT INTO users (name, email, password, role, parent_id) VALUES
(
	'Rudi', 
	'rudi@email.com', 
	'$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', -- password: admin123
	'user', 
NULL);

select * 
from child_budgets
```

```
-- Reset SEMUA tabel + SEMUA sequence dalam 1 perintah
TRUNCATE TABLE 
    child_budgets, 
    transactions, 
    users 
RESTART IDENTITY CASCADE;
```

#### INSERT DATA BUDGET
```
-- Insert data yang valid
INSERT INTO child_budgets (parent_id, child_id, amount, start_date, end_date) VALUES
(2, 3, 1000000, '2026-02-01', '2026-02-28');  -- ✅ Valid
```



### INSERT CATEGORIES
```
INSERT INTO categories (name, type) VALUES
('Gaji', 'income'),
('Bonus', 'income'),
('Makanan', 'expense'),
('Transport', 'expense'),
('Shopping', 'expense');
```

### INSERT TRANSACTION
```
INSERT INTO transactions (id_user, category_id, amount, transaction_date, description) VALUES
(1, 1, 15000000, '2026-02-01', 'Gaji admin'),
(2, 1, 12000000, '2026-02-01', 'Gaji Budi'),
(3, 3, 25000, '2026-02-05', 'Jajan sekolah');
```

### Query Transactional SELECT
```
select * 
from transactions t 
left join child_budgets cb 
on t.budget_id = cb.id
where t.budget_id is null 
WHERE cb.id = 1

-- Sisa budget saat ini untuk budget_id = 1
SELECT 
    cb.amount - COALESCE(SUM(t.amount), 0) AS remaining
FROM child_budgets cb
LEFT JOIN transactions t ON t.budget_id = cb.id
WHERE cb.id = 1
GROUP BY cb.id, cb.amount;

select * 
from transactions t 
left join categories c 
on t.category_id = c.id
where t.id_user = 1
```


```
-- Total income vs expense untuk user ID = X dalam bulan Februari 2026
SELECT 
    c.type AS transaction_type,
    COUNT(t.id) AS total_transactions,
    SUM(t.amount) AS total_amount
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1  -- Ganti dengan user ID yang diinginkan
  AND t.transaction_date BETWEEN '2026-02-01' AND '2026-02-28'
GROUP BY c.type
ORDER BY c.type DESC;

-- Summary lengkap: income, expense, net, dan rata-rata per transaksi
SELECT 
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS total_expense,
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) - 
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS net_balance,
    AVG(t.amount) AS avg_transaction_amount
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1
  AND t.transaction_date BETWEEN '2026-02-01' AND '2026-02-28';

  -- Detail per kategori (income & expense)
SELECT 
    c.name AS category_name,
    c.type AS category_type,
    COUNT(t.id) AS transaction_count,
    SUM(t.amount) AS total_amount,
    ROUND(SUM(t.amount) * 100.0 / SUM(SUM(t.amount)) OVER (PARTITION BY c.type), 2) AS percentage_of_type
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1
  AND t.transaction_date BETWEEN '2026-02-01' AND '2026-02-28'
GROUP BY c.id, c.name, c.type
ORDER BY c.type DESC, total_amount DESC;


-- Parent lihat summary semua anak dalam sebulan
SELECT 
    u.name AS child_name,
    u.id AS child_id,
    COUNT(t.id) AS total_transactions,
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS total_expense,
    cb.amount AS budget_total,
    cb.amount - SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS remaining_budget,
    ROUND(SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) * 100.0 / cb.amount, 2) AS percentage_used
FROM users u
JOIN child_budgets cb ON u.id = cb.child_id
LEFT JOIN transactions t ON t.id_user = u.id 
    AND t.transaction_date BETWEEN cb.start_date AND cb.end_date
LEFT JOIN categories c ON t.category_id = c.id
WHERE cb.parent_id = 1  -- Parent ID
  AND cb.is_active = TRUE
  AND CURRENT_DATE BETWEEN cb.start_date AND cb.end_date
GROUP BY u.id, u.name, cb.id, cb.amount
ORDER BY u.name;


SELECT 
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1
  AND t.transaction_date >= DATE_TRUNC('month', CURRENT_DATE)
  AND t.transaction_date < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month';


SELECT 
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1
  AND t.transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
  AND t.transaction_date < DATE_TRUNC('month', CURRENT_DATE);


SELECT 
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1
  AND t.transaction_date >= DATE_TRUNC('year', CURRENT_DATE)
  AND t.transaction_date < DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '1 year';


-- Trend 6 bulan terakhir (income vs expense per bulan)
SELECT 
    TO_CHAR(t.transaction_date, 'YYYY-MM') AS month,
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS total_expense,
    SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) - 
    SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) AS net_balance
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.id_user = 1
  AND t.transaction_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY TO_CHAR(t.transaction_date, 'YYYY-MM')
ORDER BY month DESC;
```