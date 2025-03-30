import unittest
import json
from app import app
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class TestDataAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DB_NAME'] = 'test_db'
        app.config['DB_USER'] = 'postgres'
        app.config['DB_PASSWORD'] = 'nicepassword'
        app.config['DB_HOST'] = 'localhost'
        
        
        self.create_test_db()
        
        self.init_test_data()
        
        self.app = app.test_client()
    
    def tearDown(self):
        
        self.clean_test_data()
    
    def create_test_db(self):
        """
        Create a test database
        """
        conn = psycopg2.connect(
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            host=app.config['DB_HOST']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
            if not cursor.fetchone():
                cursor.execute("CREATE DATABASE test_db")
        finally:
            cursor.close()
            conn.close()
    
    def init_test_data(self):
        """
        Initialize the test database
        """
        conn = psycopg2.connect(
            dbname=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            host=app.config['DB_HOST']
        )
        
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    email VARCHAR UNIQUE NOT NULL,
                    address VARCHAR,
                    phone VARCHAR
                )
            """)
            
            cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
            
            cur.execute("""
                INSERT INTO users (name, email, address, phone)
                VALUES ('Test User', 'test@example.com', '123 Main St', '555-1234')
            """)
            
            conn.commit()
        conn.close()
    
    def clean_test_data(self):
        """
        Delete all test data
        """
        conn = psycopg2.connect(
            dbname=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            host=app.config['DB_HOST']
        )
        
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
            conn.commit()
        conn.close()

    def test_get_users(self):
        """
        Test that get_users
        """
        response = self.app.get('/data/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], 'test@example.com')

    def test_create_user(self):
        """
        Test creating a user
        """
        new_user = {
            "name": "New User",
            "email": "new@example.com"
        }
        
        response = self.app.post(
            '/data/users',
            data=json.dumps(new_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        response = self.app.get('/data/users')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()