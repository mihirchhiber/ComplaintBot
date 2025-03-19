from dotenv import load_dotenv
from langchain.agents import tool
import os
import psycopg2

# Load environment variables from a .env file
load_dotenv(dotenv_path=".env")

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host="localhost",
        dbname="postgres",  # Database name
        user="postgres",  # Database username
        password=os.getenv('POSTGRES_PASSWORD'),  # Retrieves the password from the environment variable
        port=os.getenv('POSTGRES_PORT')  # Retrieves the port from the environment variable
    )

def setup_order_database(conn):
    """Creates the 'orders' table and inserts initial data for testing."""
    cur = conn.cursor()

    # Drop the 'orders' table if it exists (for clean setup)
    cur.execute("DROP TABLE IF EXISTS orders")

    # Create the 'orders' table with the necessary columns
    cur.execute("""
        CREATE TABLE orders (
            order_id VARCHAR(10) PRIMARY KEY,
            email_id VARCHAR(255) NOT NULL,
            ordering_timestamp TIMESTAMP NOT NULL,
            order_items JSONB NOT NULL,  # JSONB field to store order details
            total_price DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(20),
            payment_status VARCHAR(20) DEFAULT 'unpaid',
            delivery_address TEXT,
            delivery_timestamp TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending'
        )
    """)

    # Insert sample orders into the 'orders' table
    cur.execute("""
        INSERT INTO orders (order_id, email_id, ordering_timestamp, order_items, total_price, payment_method, payment_status, delivery_address, delivery_timestamp, status)
        VALUES 
            ('2743', 'user1@example.com', '2025-03-19 12:30:00', '[{"item": "Pizza", "quantity": 2, "price": 15.99}, {"item": "Soda", "quantity": 1, "price": 2.50}]'::jsonb, 34.48, 'credit_card', 'paid', '123 Main St, City', '2025-03-19 16:30:00', 'late delivery'),
            ('2744', 'user2@example.com', '2025-03-19 14:00:00', '[{"item": "Burger", "quantity": 1, "price": 9.99}, {"item": "Fries", "quantity": 1, "price": 3.50}]'::jsonb, 13.49, 'paypal', 'unpaid', '456 Elm St, City', NULL, 'pending'),
            ('2745', 'user3@example.com', '2025-03-19 18:45:00', '[{"item": "Pasta", "quantity": 1, "price": 12.99}, {"item": "Garlic Bread", "quantity": 1, "price": 4.99}]'::jsonb, 17.98, 'cash_on_delivery', 'paid', '789 Oak St, City', '2025-03-14 19:30:00', 'delivered'),
            ('2746', 'user4@example.com', '2025-03-19 10:15:00', '[{"item": "Sushi", "quantity": 3, "price": 8.50}, {"item": "Miso Soup", "quantity": 1, "price": 2.99}]'::jsonb, 28.49, 'credit_card', 'unpaid', '321 Pine St, City', NULL, 'processing'),
            ('2647', 'user5@example.com', '2025-03-19 20:20:00', '[{"item": "Steak", "quantity": 1, "price": 25.99}, {"item": "Wine", "quantity": 1, "price": 14.99}]'::jsonb, 40.98, 'paypal', 'paid', '567 Maple St, City', '2025-03-16 21:30:00', 'delivered')
    """)
    
    # Commit the changes to the database
    conn.commit()
    cur.close()

@tool
def get_order_status(order_id: str):
    """Returns the payment status and current status of the order based on the order ID."""
    cur = conn.cursor()

    try:
        # Fetch order details using the provided order_id
        sql = cur.mogrify("SELECT payment_status, status FROM orders WHERE order_id = %s", (order_id,))
        cur.execute(sql)
        result = cur.fetchone()

        if result:
            return result  # Return the payment status and order status if found
        else:
            return "Order not found"  # Return this message if the order does not exist
    except:
        return "Wrong input given, please provide order no."  # Return this if there's an error with the query

@tool
def get_email_for_order(order_id: str):
    """Returns the email associated with the given order ID."""
    cur = conn.cursor()

    try:
        # Fetch the email_id associated with the provided order_id
        sql = cur.mogrify("SELECT email_id FROM orders WHERE order_id = %s", (order_id,))
        cur.execute(sql)
        result = cur.fetchone()

        if result:
            return result  # Return the email_id if found
        else:
            return "Order not found"  # Return this message if the order does not exist
    except:
        return "Wrong input given, please provide order no."  # Return this if there's an error with the query

@tool
def set_humancheck_status(order_id: str):
    """Sets the status of the order to 'humancheck' to indicate manual review is required."""
    cur = conn.cursor()
    sql = cur.mogrify("UPDATE orders SET status = 'humancheck' WHERE order_id = %s", (str(order_id),))
    cur.execute(sql)
    conn.commit()  # Commit the change to the database
    return "Status set to humancheck"  # Return confirmation message

@tool
def set_refund_status(order_id: str):
    """Sets the status of the order to 'refund' to indicate the order is being refunded."""
    cur = conn.cursor()
    sql = cur.mogrify("UPDATE orders SET status = 'refund' WHERE order_id = %s", (str(order_id),))
    cur.execute(sql)
    conn.commit()  # Commit the change to the database
    return "Status set to refund"  # Return confirmation message

def close_db_connection(conn):
    """Closes the connection to the database."""
    conn.close()

# Establish a database connection and setup the database
conn = get_db_connection()

setup_order_database(conn)

if __name__ == "__main__":
    
    # Re-setup the database (you may want to avoid doing this in a production system)
    setup_order_database(get_db_connection())
    
    # Example: Print order details for a given order_id (commented out line)
    # set_humancheck_status("1")
    print(get_order_status("1"))  # Fetch order status for order ID "1"
    
    # Close the database connection after all operations are done
    close_db_connection(conn)