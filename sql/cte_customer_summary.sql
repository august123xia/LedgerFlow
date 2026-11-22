-- Standalone SQLite demo using synthetic data.
-- Run only in an in-memory or disposable database.
-- This script drops and recreates the invoices table.
-- Fixed report date: 2026-09-16.

DROP TABLE IF EXISTS invoices;

CREATE TABLE invoices (
    invoice_id INTEGER,
    customer TEXT,
    amount INTEGER,
    status TEXT,
    invoice_date TEXT,
    due_date TEXT
);

INSERT INTO invoices VALUES
(1, 'Google', 1200, 'paid', '2026-07-01', '2026-07-31'),
(2, 'Amazon', 3500, 'unpaid', '2026-06-15', '2026-07-15'),
(3, 'Ali', 800, 'unpaid', '2026-08-01', '2026-08-31'),
(4, 'Canva', 2200, 'paid', '2026-07-10', '2026-08-09'),
(5, 'Dnata', 5000, 'unpaid', '2026-05-01', '2026-05-31'),
(6, 'Google', 1800, 'unpaid', '2026-07-20', '2026-08-19'),
(7, 'Amazon', 2700, 'paid', '2026-08-05', '2026-09-04');

WITH invoice_with_days AS (
    SELECT
        customer,
        amount,
        status,
        due_date,
        CAST(julianday('2026-09-16') - julianday(due_date) AS INTEGER) AS days_overdue
    FROM invoices
),

overdue_invoices AS (
    SELECT
        customer,
        amount,
        days_overdue
    FROM invoice_with_days
    WHERE status = 'unpaid'
    AND days_overdue > 0
)

SELECT
    customer,
    COUNT(*) AS overdue_count,
    SUM(amount) AS total_overdue,
    CASE
        WHEN SUM(amount) >= 5000 THEN 'High'
        WHEN SUM(amount) >= 3000 THEN 'Medium'
        ELSE 'Low'
    END AS priority
FROM overdue_invoices
GROUP BY customer
ORDER BY total_overdue DESC;