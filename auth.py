import psycopg2
import re
import bcrypt
from psycopg2 import sql, DatabaseError
from connection import get_connection
from tkinter import simpledialog, messagebox


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


def valid_email(email):
    return bool(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email))


def register_user(email, first_name, last_name, password, role, extra_info=None):
    if not valid_email(email):
        return "Invalid email format."

    if len(password) < 8:
        return "Password must be at least 8 characters long."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
        if cursor.fetchone():
            return "User already exists."

        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (Email, FirstName, LastName, HashPassword, RoleType) VALUES (%s, %s, %s, %s, %s)",
                       (email, first_name, last_name, hashed_pw, role.capitalize()))

        if role.lower() == "agent":
            job_title = extra_info.get("job_title")
            agency = extra_info.get("agency")
            phone_number = extra_info.get("phone_number")
            cursor.execute("INSERT INTO agent (Email, JobTitle, Agency, Phone) VALUES (%s, %s, %s, %s)",
                           (email, job_title, agency, phone_number))
        else:
            budget = extra_info.get("budget")
            loc = extra_info.get("location")
            cursor.execute("INSERT INTO renter (Email, Budget, PreferredLocation) VALUES (%s, %s, %s)",
                           (email, budget or None, loc or None))

        conn.commit()
        return "User registered successfully."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT hashpassword FROM users WHERE Email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            return "User not found."

        stored_password = result[0]
        if verify_password(stored_password, password):
            return "Login successful."
        else:
            return "Invalid password."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def handle_login(email, password):
    if not email:
        return "Please enter an email address"
    if not password:
        return "Please enter a password"
    if not email or not password:
        return "Please enter both email and password"

    result = login_user(email, password)
    return result


def process_registration_form(fields, is_agent, agent_fields, renter_fields):
    email = fields["Email"].get()
    first_name = fields["First Name"].get()
    last_name = fields["Last Name"].get()
    password = fields["Password"].get()
    role = "agent" if is_agent.get() else "renter"

    extra_info = {
        "job_title": agent_fields["Job Title"].get() if is_agent.get() else None,
        "agency": agent_fields["Agency"].get() if is_agent.get() else None,
        "phone_number": agent_fields["Phone Number"].get() if is_agent.get() else None,
        "budget": renter_fields["Budget"].get() if not is_agent.get() else None,
        "location": renter_fields["Preferred Location"].get() if not is_agent.get() else None
    }

    return register_user(email, first_name, last_name, password, role, extra_info)


def get_user_role(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT RoleType FROM users WHERE Email = %s", (email,))
        result = cursor.fetchone()
        return result[0].lower() if result else None
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def reset_password(email):
    new_password = simpledialog.askstring(
        "Reset Password", f"Enter new password for {email}:", show='*')
    if not new_password or len(new_password) < 8:
        messagebox.showerror(
            "Error", "Password must be at least 8 characters long.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET HashPassword = %s WHERE Email = %s", (hashed_pw, email))
        conn.commit()
        messagebox.showinfo("Success", "Password reset successfully.")
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
