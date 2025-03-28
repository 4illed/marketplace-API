-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    address VARCHAR,
    phone VARCHAR
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL NOT NULL,
    category VARCHAR NOT NULL
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR NOT NULL
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL NOT NULL
);

-- Insert sample user
INSERT INTO users (name, email, address, phone)
VALUES ('John Doe', 'john@example.com', '123 Main St', '555-1234')
ON CONFLICT DO NOTHING;

-- Insert sample product
INSERT INTO products (name, description, price, category)
VALUES ('Sample Product', 'This is a sample product.', 19.99, 'Category A')
ON CONFLICT DO NOTHING;