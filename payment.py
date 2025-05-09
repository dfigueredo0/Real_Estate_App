from connection import get_connection
from psycopg2 import sql, DatabaseError

def add_card(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        card_num = input("Enter your credit card number: ")
        if not card_num.isdigit() or len(card_num) != 16:
            return "Invalid card number. Please enter a 16-digit number."
        
        cardholder_name = input("Enter the name on the card: ")
        exp_date = input("Enter the expiration date (MM/YY): ")
        if not exp_date or len(exp_date) != 5 or exp_date[2] != '/':
            return "Invalid expiration date format. Please use MM/YY."
        
        cvv = input("Enter the CVV: ")
        if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
            return "Invalid CVV. Please enter a 3 or 4 digit number."
        
        billing_address = input("Enter the billing address: ")
        
        cursor.execute("SELECT * FROM CreditCard WHERE cardnum = %s AND RenterEmail = %s", (card_num, email))
        if cursor.fetchone():
            return "Card already exists. Please use a different card number."
        
        cursor.execute("INSERT INTO CreditCard (cardnum, cardholdername, expdate, cvv, PaymentAddress, RenterEmail) VALUES (%s, %s, %s, %s, %s, %s)", (card_num, cardholder_name, exp_date, cvv, billing_address, email))

        conn.commit()
        print("Card added successfully.")
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
def set_default_card(email, card_num):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnum = %s", (email, card_num))
        if not cursor.fetchone():
            return "Card not found. Please add a payment method first."

        cursor.execute("UPDATE CreditCard SET defaultcard = TRUE WHERE RenterEmail = %s AND cardnum = %s", (email, card_num))
        cursor.execute("UPDATE CreditCard SET defaultcard = FALSE WHERE RenterEmail = %s AND cardnum != %s", (email, card_num))

        conn.commit()
        return "Default card set successfully."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_default_card(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT cardnum, cardholdername, expdate, cvv, PaymentAddress FROM CreditCard WHERE RenterEmail = %s AND defaultcard = TRUE", (email,))
        default_card = cursor.fetchone()
        if not default_card:
            return "No default card found."
        return (default_card[0][:4] + " **** **** " + default_card[0][-4:],) + default_card[1]
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def view_cards(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT cardnum, cardholdername, expdate, cvv, PaymentAddress FROM CreditCard WHERE RenterEmail = %s", (email,))
        cards = cursor.fetchall()
        if not cards:
            return "No cards found."
        return [{
            "Card Number": card[0][:4] + " **** **** " + card[0][-4:],
            "Name": card[1],
            "Expiration": card[2],
            "Address": card[4]
        } for card in cards]
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_card(email, card_num):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnum = %s AND defaultcard = TRUE", (email, card_num))
        if cursor.fetchone():
            return "Cannot delete the default card. Please set another card as default first."

        cursor.execute("DELETE FROM CreditCard WHERE RenterEmail = %s AND cardnum = %s", (email, card_num))
        conn.commit()
        return "Card deleted successfully."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_card(email, card_num):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cardholder_name = input("Enter the new name on the card: ")
        exp_date = input("Enter the new expiration date (MM/YY): ")
        cvv = input("Enter the new CVV: ")
        billing_address = input("Enter the new billing address: ")

        cursor.execute("""
            UPDATE CreditCard
            SET cardholdername = %s, expdate = %s, cvv = %s, PaymentAddress = %s
            WHERE RenterEmail = %s AND cardnum = %s
        """, (cardholder_name, exp_date, cvv, billing_address, email, card_num))

        conn.commit()
        return "Card updated successfully."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()