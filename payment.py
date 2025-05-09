from connection import get_connection
from utils.forms import FormBuilder

from datetime import datetime
from psycopg2 import sql, DatabaseError
from tkinter import *
from tkinter import ttk, messagebox

def add_card(parent, current_user):
    add_card_window = Toplevel(parent)

    fields = {
        "Card Number": StringVar(),
        "Name on Card": StringVar(),
        "Expiration Date (MM/YY)": StringVar(),
        "CVV": StringVar(),
        "Billing Address": StringVar()
    }

    form = FormBuilder(add_card_window)
    form.add_fields(fields)

    def submit():
        conn = get_connection()
        cursor = conn.cursor()
        values = form.get_values()

        try:
            if not values["Card Number"].isdigit() or len(values["Card Number"]) != 16:
                messagebox.showerror(message="Invalid card number. Please enter a 16-digit number.")
                return 
            if not values["Name on Card"]:
                messagebox.showerror(message="Cardholder name cannot be empty.")
                return 
            if not values["Expiration Date (MM/YY)"] or len(values["Expiration Date (MM/YY)"]) != 5 or values["Expiration Date (MM/YY)"][2] != '/':
                messagebox.showerror(message="Invalid expiration date format. Please use MM/YY.")
                return 
            if not values["CVV"].isdigit() or len(values["CVV"]) not in [3, 4]:
                messagebox.showerror(message="Invalid CVV. Please enter a 3 or 4 digit number.")
                return 
            if not values["Billing Address"]:
                messagebox.showerror(message="Billing address cannot be empty.")
                return
            
            try:
                exp_date = datetime.strptime(values["Expiration Date (MM/YY)"], "%m/%y").date().replace(day=1)
                if exp_date < datetime.now().date().replace(day=1):
                    messagebox.showerror(message="Card has expired. Please enter a valid expiration date.")
                    return
            except ValueError:
                messagebox.showerror(message="Invalid expiration date format. Please use MM/YY.")
                return
            
            cursor.execute("SELECT 1 FROM CreditCard WHERE cardnumber = %s AND cardholdername = %s", (values["Card Number"], values["Name on Card"]))
            if cursor.fetchone():
                messagebox.showerror(message="Card already exists on file, cannot add it. Please use a different card number.")
                return 
            
            cursor.execute("SELECT COUNT(*) FROM CreditCard WHERE RenterEmail = %s", (current_user["email"],))
            first_card = cursor.fetchone()[0] == 0

            cursor.execute("""
                           INSERT INTO CreditCard (cardnumber, cardholdername, expirationdate, cvv, defaultcard, PaymentAddress, RenterEmail) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                           (values["Card Number"], values["Name on Card"], exp_date, values["CVV"], 
                            first_card, values["Billing Address"], current_user["email"])
                        )
            conn.commit()
            messagebox.showinfo(message="Card added successfully.")
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror(message=f"Database error: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    form.add_submit_buttons(submit, add_card_window.destroy)
        
def set_default_card(email, card_num):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s", (email, card_num))
        if not cursor.fetchone():
            return "Card not found. Please add a payment method first."

        cursor.execute("UPDATE CreditCard SET defaultcard = TRUE WHERE RenterEmail = %s AND cardnumber = %s", (email, card_num))
        cursor.execute("UPDATE CreditCard SET defaultcard = FALSE WHERE RenterEmail = %s AND cardnumber != %s", (email, card_num))

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
        cursor.execute("SELECT cardnumber, cardholdername, expirationdate, cvv, PaymentAddress FROM CreditCard WHERE RenterEmail = %s AND defaultcard = TRUE", (email,))
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
        cursor.execute("SELECT cardnumber, cardholdername, expirationdate, cvv, PaymentAddress FROM CreditCard WHERE RenterEmail = %s", (email,))
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
        cursor.execute("SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s AND defaultcard = TRUE", (email, card_num))
        if cursor.fetchone():
            return "Cannot delete the default card. Please set another card as default first."

        cursor.execute("DELETE FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s", (email, card_num))
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
            SET cardholdername = %s, expirationdate = %s, cvv = %s, PaymentAddress = %s
            WHERE RenterEmail = %s AND cardnumber = %s
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