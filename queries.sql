SELECT parent_id, COUNT(*) as children_count
FROM categories
WHERE parent_id IS NOT NULL
GROUP BY parent_id;

WITH RECURSIVE category_tree AS (
    -- Базовый случай: берем категорию товара и поднимаемся вверх
    SELECT id, name, parent_id, id as original_id
    FROM categories
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.original_id
    FROM categories c
    JOIN category_tree ct ON c.id = ct.parent_id
),
root_categories AS (
    -- Выбираем только те записи, где parent_id IS NULL (корень)
    SELECT original_id, name as root_category_name
    FROM category_tree
    WHERE parent_id IS NULL
)
SELECT
    p.name as product_name,
    rc.root_category_name,
    SUM(oi.quantity) as total_sold
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
JOIN root_categories rc ON p.category_id = rc.original_id
WHERE o.created_at >= NOW() - INTERVAL '1 month'
GROUP BY p.id, p.name, rc.root_category_name
ORDER BY total_sold DESC
LIMIT 5;