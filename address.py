from connection import get_connection
from utils.forms import FormBuilder
from tkinter import *
from tkinter import ttk, messagebox
from psycopg2 import DatabaseError


def manage_addresses(parent, current_user):
    window = Toplevel(parent)
    window.title("Manage Addresses")
    window.geometry("600x400")

    tree = ttk.Treeview(window, columns=("Address",), show="headings")
    tree.heading("Address", text="Address")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    def load_addresses():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT address FROM user_addresses WHERE email = %s", (current_user["email"],))
            for row in cursor.fetchall():
                tree.insert("", END, values=row)
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_address():
        addr_win = Toplevel(window)
        addr_win.title("Add Address")
        fields = {"Address": StringVar()}
        form = FormBuilder(addr_win)
        form.add_fields(fields)

        def submit():
            addr = fields["Address"].get()
            if not addr:
                messagebox.showerror("Error", "Address cannot be empty.")
                return

            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO user_addresses (address, email) VALUES (%s, %s)", (addr, current_user["email"]))
                conn.commit()
                messagebox.showinfo("Success", "Address added.")
                addr_win.destroy()
                load_addresses()
            except DatabaseError as e:
                conn.rollback()
                messagebox.showerror("Database Error", str(e))
            finally:
                cursor.close()
                conn.close()

        form.add_submit_buttons(submit, addr_win.destroy)

    def delete_address():
        selected = tree.selection()
        if not selected:
            return
        addr = tree.item(selected[0])["values"][0]

        # Check if address is used as payment address
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM creditcard WHERE paymentaddress = %s AND renteremail = %s", (addr, current_user["email"]))
            if cursor.fetchone():
                messagebox.showerror(
                    "Error", "Cannot delete address. It is used for a payment method.")
                return

            cursor.execute(
                "DELETE FROM user_addresses WHERE address = %s AND email = %s", (addr, current_user["email"]))
            conn.commit()
            messagebox.showinfo("Success", "Address deleted.")
            load_addresses()
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            cursor.close()
            conn.close()

    ttk.Button(window, text="Add Address", command=add_address).pack(pady=5)
    ttk.Button(window, text="Delete Selected Address",
               command=delete_address).pack(pady=5)

    load_addresses()
