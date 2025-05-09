import psycopg2 
from psycopg2 import sql, DatabaseError
from connection import get_connection
# TODO: change to use CLI/GUI (i.e. tkinter)

def register_user():
    # TODO: Implement user registration logic
    # For now, simple cmd inputs
    email = input("Enter your email: ")
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    role = input("Enter your role (admin/user): ")

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM user WHERE email = %s", (email))
        if cursor.fetchone():
            return "User already exists."
        
        cursor.execute("INSERT INTO user (Email, FirstName, LastName) VALUES (%s, %s, %s)", (email, first_name, last_name))

        if role == "admin":
            job_title = input("Enter your job title: ")
            agency = input("Enter your agency: ")
            phone_number = input("Enter your phone number: ")
            cursor.execute("INSERT INTO agent VALUES (%s, %s, %s, %s)", (email, job_title, agency, phone_number))
        elif role == "user":
            budget = input("Enter your budget: ")
            loc = input("Enter your preffered location: ")
            cursor.execute("INSERT INTO user (Email, FirstName, LastName) VALUES (%s, %s, %s)", (email, budget, loc))

        conn.commit()
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed."
    
    return "User registered successfully."