from connection import get_connection
from psycopg2 import sql, DatabaseError

def add_card(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        card_num = input("Enter your credit card number: ")
        cardholder_name = input("Enter the name on the card: ")
        exp_date = input("Enter the expiration date (MM/YY): ")
        cvv = input("Enter the CVV: ")
        billing_address = input("Enter the billing address: ")
        
        cursor.execute("INSERT INTO CreditCard (cardnum, cardholdername, expdate, cvv, billingaddress, email) VALUES (%d, %s, %s, %s, %d, %s, %s)", (card_num, cardholder_name, exp_date, cvv, billing_address, email))

        cursor.commit()
        print("Card added successfully.")
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed."