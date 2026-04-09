CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price DECIMAL(12, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price_at_order DECIMAL(12, 2) NOT NULL, -- Фиксация цены на момент заказа
    UNIQUE(order_id, product_id)
);
