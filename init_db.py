from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables
load_dotenv(dotenv_path=".env")

def get_db_connection():
    """Establishes and returns a connection to the database."""
    return psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT')
    )

def setup_order_database(conn):
    """Creates the 'orders' table and inserts initial data."""
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS orders")

    cur.execute("""
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            ordering_timestamp TIMESTAMP NOT NULL,
            order_items JSONB NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(20),
            payment_status VARCHAR(20) DEFAULT 'unpaid',
            delivery_address TEXT,
            delivery_timestamp TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending'
        )
    """)

    cur.execute("""
        INSERT INTO orders (user_id, ordering_timestamp, order_items, total_price, payment_method, payment_status, delivery_address, delivery_timestamp, status)
        VALUES 
            (1, '2025-03-15 12:30:00', '[{"item": "Pizza", "quantity": 2, "price": 15.99}, {"item": "Soda", "quantity": 1, "price": 2.50}]'::jsonb, 34.48, 'credit_card', 'paid', '123 Main St, City', '2025-03-15 13:30:00', 'delivered'),
            (2, '2025-03-15 14:00:00', '[{"item": "Burger", "quantity": 1, "price": 9.99}, {"item": "Fries", "quantity": 1, "price": 3.50}]'::jsonb, 13.49, 'paypal', 'unpaid', '456 Elm St, City', NULL, 'pending'),
            (3, '2025-03-14 18:45:00', '[{"item": "Pasta", "quantity": 1, "price": 12.99}, {"item": "Garlic Bread", "quantity": 1, "price": 4.99}]'::jsonb, 17.98, 'cash_on_delivery', 'paid', '789 Oak St, City', '2025-03-14 19:30:00', 'delivered'),
            (4, '2025-03-16 10:15:00', '[{"item": "Sushi", "quantity": 3, "price": 8.50}, {"item": "Miso Soup", "quantity": 1, "price": 2.99}]'::jsonb, 28.49, 'credit_card', 'unpaid', '321 Pine St, City', NULL, 'processing'),
            (5, '2025-03-16 20:20:00', '[{"item": "Steak", "quantity": 1, "price": 25.99}, {"item": "Wine", "quantity": 1, "price": 14.99}]'::jsonb, 40.98, 'paypal', 'paid', '567 Maple St, City', '2025-03-16 21:30:00', 'delivered')
    """)
    
    conn.commit()
    cur.close()

def close_db_connection(conn):
    """Closes the connection to the database."""
    conn.close()

if __name__ == "__main__":
    setup_order_database(get_db_connection())
    
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM orders")
    # print(cur.fetchall())

    # sql = cur.mogrify("SELECT * FROM orders WHERE payment_status = %s", ("unpaid",))
    # cur.execute(sql)
    # print(cur.fetchall())

    close_db_connection(conn)
