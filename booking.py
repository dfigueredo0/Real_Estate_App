from connection import get_connection
from psycopg2 import sql, DatabaseError
from utils.forms import FormBuilder
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox


def book_property(parent, current_user):
    window = Toplevel(parent)
    window.title("Book Property")
    window.geometry("400x400")

    fields = {
        "Property ID": StringVar(),
        "Card Number": StringVar(),
        "Name on Card": StringVar(),
        "Start Date (YYYY-MM-DD)": StringVar(),
        "End Date (YYYY-MM-DD)": StringVar()
    }

    form = FormBuilder(window)
    form.add_fields(fields)

    def submit():
        values = form.get_values()
        pid = values["Property ID"]
        card_num = values["Card Number"]
        cardholder_name = values["Name on Card"]
        start_date_str = values["Start Date (YYYY-MM-DD)"]
        end_date_str = values["End Date (YYYY-MM-DD)"]
        renter_email = current_user["email"]

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date <= start_date:
                messagebox.showerror(
                    "Error", "End date must be after start date.")
                return
        except ValueError:
            messagebox.showerror(
                "Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT availability, rentalprice FROM property WHERE propertyid = %s", (pid,))
            result = cursor.fetchone()
            if not result or not result[0]:
                messagebox.showerror(
                    "Error", "Property not available for booking.")
                return
            rental_price = result[1]

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

            days = (end_date - start_date).days
            total_cost = days * float(rental_price)

            cursor.execute("""
                INSERT INTO booking (propertyid, renteremail, rewardprogramemail, cardnumber, cardholdername, startdate, enddate, totalcost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (pid, renter_email, renter_email, card_num, cardholder_name, start_date, end_date, total_cost))

            cursor.execute(
                "UPDATE property SET availability = FALSE WHERE propertyid = %s", (pid,))

            conn.commit()
            messagebox.showinfo("Success", "Property booked successfully.")
            window.destroy()
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror("Database Error", str(e))
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
            SELECT p.propertyid, p.propertyname, p.location, b.startdate, b.enddate, b.totalcost
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
            "ID", "Name", "Location", "Start Date", "End Date", "Cost"), show="headings")
        for col in ("ID", "Name", "Location", "Start Date", "End Date", "Cost"):
            tree.heading(col, text=col)
        for b in bookings:
            tree.insert("", END, values=b)
        tree.pack(fill="both", expand=True)
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()


def view_available_bookings(parent):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.propertyid, p.propertyname, p.location, p.rentalprice, p.description
            FROM property p
            WHERE p.availability = TRUE
        """)
        available = cursor.fetchall()
        window = Toplevel(parent)
        window.title("Available Properties")
        if not available:
            messagebox.showinfo("Info", "No available properties found.")
            return

        tree = ttk.Treeview(window, columns=(
            "ID", "Name", "Location", "Price", "Description"), show="headings")
        for col in ("ID", "Name", "Location", "Price", "Description"):
            tree.heading(col, text=col)
        for a in available:
            tree.insert("", END, values=a)
        tree.pack(fill="both", expand=True)
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()


def view_agent_bookings(parent, current_user):
    agent_email = current_user["email"]
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.bookingid, u.firstname || ' ' || u.lastname AS renter, p.propertyid, b.startdate, b.enddate, b.totalcost, b.cardnumber
            FROM booking b
            JOIN property p ON b.propertyid = p.propertyid
            JOIN users u ON b.renteremail = u.email
            WHERE p.agentemail = %s
        """, (agent_email,))
        bookings = cursor.fetchall()
        window = Toplevel(parent)
        window.title("Agent Property Bookings")
        if not bookings:
            messagebox.showinfo("Info", "No bookings found.")
            return

        tree = ttk.Treeview(window, columns=("Booking ID", "Renter", "Property ID",
                            "Start", "End", "Cost", "Card Number"), show="headings")
        for col in ("Booking ID", "Renter", "Property ID", "Start", "End", "Cost", "Card Number"):
            tree.heading(col, text=col)
        for row in bookings:
            tree.insert("", END, values=row)
        tree.pack(fill="both", expand=True)
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()


def cancel_booking(current_user, booking_id):
    email = current_user["email"]
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT propertyid FROM booking WHERE booking_id = %s AND renteremail = %s", (booking_id, email))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "No booking found to cancel.")
            return
        pid = result[0]
        cursor.execute(
            "DELETE FROM booking WHERE booking_id = %s AND renteremail = %s", (booking_id, email))
        cursor.execute(
            "UPDATE property SET availability = TRUE WHERE propertyid = %s", (pid,))
        conn.commit()
        messagebox.showinfo("Success", "Booking cancelled successfully.")
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()
