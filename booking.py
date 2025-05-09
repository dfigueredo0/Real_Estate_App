from connection import get_connection
from psycopg2 import sql, DatabaseError

def book_property(pid, renter_email, card_num, cardholder_name):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT availability FROM property WHERE propertyid = %s", (pid,))
        result = cursor.fetchone()
        if not result or not result[0]:
            return "Property not available for booking."
        
        cursor.execute("SELECT * FROM booking WHERE propertyid = %s AND renteremail = %s", (pid, renter_email))
        if cursor.fetchone():
            return "You have already booked this property."

        cursor.execute("SELECT * FROM CreditCard WHERE cardnum = %s AND email = %s", (card_num, renter_email))
        if not cursor.fetchone():
            return "Card not found. Please add a payment method first."

        cursor.execute("""
            INSERT INTO booking (propertyid, renteremail, cardnum, cardholdername)
            VALUES (%s, %s, %s, %s)
                      """, (pid, renter_email, card_num, cardholder_name))
        
        cursor.execute("UPDATE property SET availability = FALSE WHERE propertyid = %s", (pid,))

        conn.commit()
        return "Property booked successfully."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def view_user_bookings(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.propertyid, p.propertyname, p.location, b.bookingdate
            FROM property p JOIN booking b ON p.propertyid = b.propertyid
            WHERE b.renteremail = %s
                       """, (email,))
        bookings = cursor.fetchall()
        if not bookings:
            return "No bookings found."
        return bookings
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def view_available_bookings():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.propertyid, p.propertyname, p.location
            FROM property p LEFT JOIN booking b ON p.propertyid = b.propertyid
            WHERE p.availability = TRUE
                       """)
        available_bookings = cursor.fetchall()
        if not available_bookings:
            return "No available bookings found."
        return available_bookings
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def cancel_booking(booking_id, email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT propertyid FROM booking WHERE booking_id = %s AND renteremail = %s
                       """, (email,))
        booking = cursor.fetchone()
        if not booking:
            return "No booking found to cancel."
        
        property_id = booking[0]
        cursor.execute("DELETE FROM booking WHERE booking_id = %s AND renteremail = %s", (booking_id, email))
        cursor.execute("UPDATE property SET availability = TRUE WHERE propertyid = %s", (property_id,))

        conn.commit()
        return "Booking cancelled successfully."
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()