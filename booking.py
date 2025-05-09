from connection import get_connection
from psycopg2 import sql, DatabaseError

def book_property():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        pid = input("Enter Property ID: ")
        renter_email = input("Enter your email: ")
        card_num = input("Enter your credit card number: ")

        cursor.execute("SELECT availability FROM property WHERE propertyid = %s", (pid,))
        result = cursor.fetchone()
        if not result:
            return "Property not available for booking."
        
        cursor.execute("""
            INSERT INTO booking (propertyid, renteremail, cardnum)
            VALUES (%s, %s, %s)
                      """, (pid, renter_email, card_num))
        
        cursor.execute("UPDATE property SET availability = FALSE WHERE propertyid = %s", (pid,))
        
        conn.commit()
        print("Property booked successfully.")
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed."