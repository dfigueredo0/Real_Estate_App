import psycopg2 
import re
import bcrypt
from psycopg2 import sql, DatabaseError
from connection import get_connection

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
        cursor.execute("INSERT INTO users (Email, FirstName, LastName, HashPassword) VALUES (%s, %s, %s, %s)", (email, first_name, last_name, hashed_pw))

        if role == "admin":
            job_title = extra_info.get("job_title")
            agency = extra_info.get("agency")
            phone_number = extra_info.get("phone_number")
            cursor.execute("INSERT INTO agent VALUES (%s, %s, %s, %s)", (email, job_title, agency, phone_number))
        elif role == "user":
            budget = extra_info.get("budget")
            loc = extra_info.get("location")
            cursor.execute("INSERT INTO renter (Email, Budget, PreferredLocation) VALUES (%s, %s, %s)", (email, budget or None, loc or None))

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
        cursor.execute("SELECT hashpassword FROM users WHERE Email = %s", (email,))
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