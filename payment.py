from connection import get_connection
from utils.forms import FormBuilder

from datetime import datetime
from psycopg2 import sql, DatabaseError
from tkinter import *
from tkinter import ttk, messagebox


def validate_entries(values):
    try:
        if not values["Card Number"].isdigit() or len(values["Card Number"]) != 16:
            messagebox.showerror(
                message="Invalid card number. Please enter a 16-digit number.")
            return None

        if not values["Name on Card"]:
            messagebox.showerror(message="Cardholder name cannot be empty.")
            return None

        if not values["Expiration Date (MM/YY)"] or len(values["Expiration Date (MM/YY)"]) != 5 or values["Expiration Date (MM/YY)"][2] != '/':
            messagebox.showerror(
                message="Invalid expiration date format. Please use MM/YY.")
            return None

        if not values["CVV"].isdigit() or len(values["CVV"]) not in [3, 4]:
            messagebox.showerror(
                message="Invalid CVV. Please enter a 3 or 4 digit number.")
            return None

        if not values["Billing Address"]:
            messagebox.showerror(message="Billing address cannot be empty.")
            return None

        exp_date = datetime.strptime(
            values["Expiration Date (MM/YY)"], "%m/%y").date().replace(day=1)
        if exp_date < datetime.now().date().replace(day=1):
            messagebox.showerror(
                message="Card has expired. Please enter a valid expiration date.")
            return None

        return exp_date
    except ValueError:
        messagebox.showerror(
            message="Invalid expiration date format. Please use MM/YY.")
        return None


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

        exp_date = validate_entries(values)
        if not exp_date:
            return

        try:

            cursor.execute("SELECT 1 FROM CreditCard WHERE cardnumber = %s AND cardholdername = %s",
                           (str(values["Card Number"]), values["Name on Card"]))
            if cursor.fetchone():
                messagebox.showerror(
                    message="Card already exists on file, cannot add it. Please use a different card number.")
                return

            cursor.execute(
                "SELECT COUNT(*) FROM CreditCard WHERE RenterEmail = %s", (current_user["email"],))
            first_card = cursor.fetchone()[0] == 0

            cursor.execute("""
                           INSERT INTO CreditCard (cardnumber, cardholdername, expirationdate, cvv, defaultcard, PaymentAddress, RenterEmail) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                           (str(values["Card Number"]), values["Name on Card"], exp_date, values["CVV"],
                            first_card, values["Billing Address"], current_user["email"])
                           )
            conn.commit()
            messagebox.showinfo(message="Card added successfully.")
            add_card_window.destroy()
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
        cursor.execute(
            "SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s", (email, str(card_num)))
        if not cursor.fetchone():
            return "Card not found. Please add a payment method first."

        cursor.execute(
            "UPDATE CreditCard SET defaultcard = TRUE WHERE RenterEmail = %s AND cardnumber = %s", (email, str(card_num)))
        cursor.execute(
            "UPDATE CreditCard SET defaultcard = FALSE WHERE RenterEmail = %s AND cardnumber != %s", (email, str(card_num)))

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
        cursor.execute(
            "SELECT cardnumber, cardholdername, expirationdate, cvv, PaymentAddress FROM CreditCard WHERE RenterEmail = %s AND defaultcard = TRUE", (email,))
        default_card = cursor.fetchone()
        if not default_card:
            return "No default card found."
        return ("**** **** **** " + default_card[0][-4:],) + default_card[1]
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_cardnumber_by_last_four(email, last_four):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT cardnumber FROM CreditCard WHERE RenterEmail = %s AND cardnumber LIKE %s", (email, f"%{last_four}"))
        result = cursor.fetchone()
        return str(result[0]) if result else None
    finally:
        cursor.close()
        conn.close()


def view_cards(parent, current_user):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
                       SELECT cardnumber, cardholdername, expirationdate, cvv, 
                       defaultcard, PaymentAddress FROM CreditCard WHERE RenterEmail = %s""",
                       (current_user["email"],)
                       )
        cards = cursor.fetchall()
        if not cards:
            messagebox.showinfo(message="No cards found.")
            return

        result_window = Toplevel(parent)
        result_window.title("Cards")
        columns = ["Card Number", "Name", "Expiration",
                   "CVV", "Address", "Default Card", "__internal"]

        result_tree = ttk.Treeview(
            result_window, columns=columns, show="headings")
        for col in columns[:-1]:
            result_tree.heading(col, text=col)
            result_tree.column(col, anchor="center")

        result_tree.column("__internal", width=0, stretch=False)

        result_tree.pack(expand=True, fill="both")
        for card in cards:
            masked = "**** **** **** " + card[0][-4:]
            result_tree.insert("", "end", values=(
                masked, card[1], card[2], card[3], card[5], "Yes" if card[4] else "No", str(card[0])))

        def on_double_click(event):
            selected_item = result_tree.selection()
            if not selected_item:
                return
            item = result_tree.item(selected_item)
            unmasked_card = str(item["values"][6])
            update_card(parent, current_user, unmasked_card)
            result_window.destroy()
            view_cards(parent, current_user)

        def on_set_default():
            selected_item = result_tree.selection()
            if not selected_item:
                return
            item = result_tree.item(selected_item)
            unmasked_card_num = str(item["values"][6])
            set_default_card(current_user["email"], unmasked_card_num)
            result_window.destroy()
            view_cards(parent, current_user)

        def on_delete(event):
            selected_item = result_tree.selection()
            if not selected_item:
                return
            item = result_tree.item(selected_item)
            unmasked_card_num = str(item["values"][6])
            delete_card(current_user["email"], unmasked_card_num)
            result_window.destroy()
            view_cards(parent, current_user)

        result_tree.bind("<Double-1>", on_double_click)
        result_tree.bind("<Delete>", on_delete)

        set_default_btn = ttk.Button(
            result_window, text="Set as Default", command=on_set_default)
        set_default_btn.pack(pady=10)
    except DatabaseError as e:
        conn.rollback()
        messagebox(message=f"Database error: {e}")
        return
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_card(email, card_num):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s AND defaultcard = TRUE", (email, str(card_num)))
        if cursor.fetchone():
            return "Cannot delete the default card. Please set another card as default first."

        cursor.execute(
            "DELETE FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s", (email, str(card_num)))
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


def update_card(parent, current_user, card_number):
    update_card_window = Toplevel(parent)
    update_card_window.title("Update Card")
    update_card_window.geometry("400x300")

    fields = {
        "Card Number": StringVar(value=str(card_number)),
        "Name on Card": StringVar(),
        "Expiration Date (MM/YY)": StringVar(),
        "CVV": StringVar(),
        "Billing Address": StringVar(),
        "Email": StringVar(value=current_user["email"])
    }

    map = {
        "Card Number": "cardnumber",
        "Name on Card": "cardholdername",
        "Expiration Date (MM/YY)": "expirationdate",
        "CVV": "cvv",
        "Billing Address": "paymentaddress",
        "Email": "renteremail"
    }

    form = FormBuilder(update_card_window)
    form.add_fields(fields)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM CreditCard WHERE RenterEmail = %s AND cardnumber = %s", (current_user["email"], str(card_number)))
        cards = cursor.fetchall()
        if not cards:
            messagebox.showerror(message="No cards found.")
            return

        if not form.load_from_db_explicit(cursor, "creditcard", "cardnumber", str(card_number), map):
            messagebox.showerror(message="Card not found.")
            update_card_window.destroy()
            return
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror(message=f"Database error: {e}")
        return

    def submit():
        values = form.get_values()

        exp_date = validate_entries(values)
        if not exp_date:
            return

        update_values = []
        update_columns = []

        for field, value in values.items():
            if field in fields and value not in (None, ""):
                update_columns.append(map[field])
                update_values.append(str(value))

        if not update_columns:
            messagebox.showinfo(
                "No Updates", "Please fill in at least one field to update.")
            return

        assignments = [
            sql.SQL("{} = %s").format(sql.Identifier(col))
            for col in update_columns
        ]
        query = sql.SQL("UPDATE CreditCard SET {} WHERE cardnumber = %s").format(
            sql.SQL(", ").join(assignments))

        try:
            update_values.append(str(card_number))
            cursor.execute(query, tuple(update_values))
            conn.commit()
            messagebox.showinfo("Success", "Credit Card updated.")
            update_card_window.destroy()
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror(message=f"Database Error: {e}")
        finally:
            cursor.close()
            conn.close()

    form.add_submit_buttons(submit, update_card_window.destroy)

    update_card_window.bind('<Return>', lambda event: submit())
    update_card_window.bind(
        '<Escape>', lambda event: update_card_window.destroy())
