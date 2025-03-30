import unittest
import json
import psycopg2
from app import app


class TestProductsAPI(unittest.TestCase):
    @classmethod
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.init_test_db()

    @classmethod
    def init_test_db(cls):
        """Инициализация тестовой базы данных"""
        conn = psycopg2.connect(
            dbname=app.config["DB_NAME"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            host=app.config["DB_HOST"],
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        description TEXT,
                        price DECIMAL NOT NULL,
                        category VARCHAR
                    );
                    TRUNCATE TABLE products RESTART IDENTITY CASCADE;
                    INSERT INTO products (name, description, price, category)
                    VALUES 
                        ('Test Product 1', 'Desc 1', 10.99, 'Category A'),
                        ('Test Product 2', 'Desc 2', 20.50, 'Category B');
                """
                )
                conn.commit()
        finally:
            conn.close()

    def test_get_products(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Test Product 1")

    def test_create_product(self):
        new_product = {
            "name": "New Test Product",
            "description": "New Desc",
            "price": 30.00,
            "category": "Category C",
        }
        response = self.client.post(
            "/products", data=json.dumps(new_product), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "New Test Product")

    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов"""
        conn = psycopg2.connect(
            dbname=app.config["DB_NAME"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            host=app.config["DB_HOST"],
        )
        try:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS products CASCADE;")
                conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
