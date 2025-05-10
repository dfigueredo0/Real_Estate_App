from connection import get_connection
from psycopg2 import sql, DatabaseError
from utils.forms import FormBuilder
from tkinter import *
from tkinter import ttk, messagebox


def book_property(parent, current_user):
    window = Toplevel(parent)
    window.title("Book Property")
    window.geometry("400x300")

    fields = {
        "Property ID": StringVar(),
        "Card Number": StringVar(),
        "Name on Card": StringVar()
    }

    form = FormBuilder(window)
    form.add_fields(fields)

    def submit():
        values = form.get_values()
        pid = values["Property ID"]
        card_num = values["Card Number"]
        cardholder_name = values["Name on Card"]
        renter_email = current_user["email"]

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT availability FROM property WHERE propertyid = %s", (pid,))
            result = cursor.fetchone()
            if not result or not result[0]:
                messagebox.showerror(
                    "Error", "Property not available for booking.")
                return

            cursor.execute(
                "SELECT * FROM booking WHERE propertyid = %s AND renteremail = %s", (pid, renter_email))
            if cursor.fetchone():
                messagebox.showerror(
                    "Error", "You have already booked this property.")
                return

            cursor.execute(
                "SELECT * FROM CreditCard WHERE cardnumber = %s AND renteremail = %s", (card_num, renter_email))
            if not cursor.fetchone():
                messagebox.showerror(
                    "Error", "Card not found. Please add a payment method first.")
                return

            cursor.execute(
                "SELECT 1 FROM RewardProgram WHERE Email = %s", (renter_email,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO RewardProgram (Email, TotalPoints) VALUES (%s, %s)", (renter_email, 0))

            cursor.execute("""
                INSERT INTO booking (propertyid, renteremail, rewardprogramemail, cardnumber, cardholdername)
                VALUES (%s, %s, %s, %s, %s)
            """, (pid, renter_email, renter_email, card_num, cardholder_name))

            cursor.execute(
                "UPDATE property SET availability = FALSE WHERE propertyid = %s", (pid,))

            conn.commit()
            messagebox.showinfo("Success", "Property booked successfully.")
            window.destroy()
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror(f"Database Error: {e}")
        finally:
            cursor.close()
            conn.close()

    form.add_submit_buttons(submit, window.destroy)


def view_user_bookings(parent, current_user):
    email = current_user["email"]
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT b.bookingid, p.propertyid, p.location
            FROM property p JOIN booking b ON p.propertyid = b.propertyid
            WHERE b.renteremail = %s
        """, (email,))
        bookings = cursor.fetchall()
        window = Toplevel(parent)
        window.title("Your Bookings")
        if not bookings:
            messagebox.showinfo("Info", "No bookings found.")
            return

        tree = ttk.Treeview(window, columns=(
            "Booking ID", "Property ID", "Location"), show="headings")
        for col in ("Booking ID", "Property ID", "Location"):
            tree.heading(col, text=col)
        for b in bookings:
            tree.insert("", END, values=b)
        tree.pack(fill="both", expand=True)
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror(f"Database Error: {e}")
    finally:
        cursor.close()
        conn.close()


def view_available_bookings(parent):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.bookingid, p.propertyid, p.location
            FROM property p LEFT JOIN booking b ON p.propertyid = b.propertyid
            WHERE p.availability = TRUE
        """)
        available = cursor.fetchall()
        window = Toplevel(parent)
        window.title("Available Properties")
        if not available:
            messagebox.showinfo("Info", "No available properties found.")
            return

        tree = ttk.Treeview(window, columns=(
            "Booking ID", "Property ID", "Location"), show="headings")
        for col in ("Booking ID", "Property ID", "Location"):
            tree.heading(col, text=col)
        for a in available:
            tree.insert("", END, values=a)
        tree.pack(fill="both", expand=True)
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror(f"Database Error: {e}")
    finally:
        cursor.close()
        conn.close()


def cancel_booking(current_user, booking_id):
    email = current_user["email"]
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT propertyid FROM booking WHERE bookingid = %s AND renteremail = %s", (booking_id, email))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "No booking found to cancel.")
            return
        pid = result[0]
        cursor.execute(
            "DELETE FROM booking WHERE bookingid = %s AND renteremail = %s", (booking_id, email))
        cursor.execute(
            "UPDATE Property SET availability = TRUE WHERE propertyid = %s", (pid,))
        conn.commit()
        messagebox.showinfo("Success", "Booking cancelled successfully.")
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror(f"Database Error: {e}")
    finally:
        cursor.close()
        conn.close()
