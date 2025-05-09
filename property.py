from connection import get_connection
from psycopg2 import sql, DatabaseError
# TODO: user auth logic, change to use CLI/GUI (i.e. tkinter)

def add_property():
    """ 
    AGENT ONLY: 
    Add a new property to the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        pid = input("Enter Property ID: ")
        city = input("City: ")
        state = input("State: ")
        address = input("Address: ")
        desc = input("Description: ")
        avail = input("Availability: ")
        price = float(input("Rental Price: "))
        ptype = input("Type (house/apartment/commercial): ").lower()
    
        cursor.execute("""
            INSERT INTO property (propertyid, city, state, address, description, availability, rentalprice)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (pid, city, state, address, desc, avail, price))

        if ptype == "house":
            rooms = input("rooms: ")
            sqft = input("sqft: ")
        elif ptype == "apartment":
            rooms = input("rooms: ")
            sqft = input("sqft: ")
        elif ptype == "commercialbuilding":
            rooms = input("rooms: ")
            sqft = input("sqft: ")
        elif ptype == "vacationhomes":
            rooms = input("rooms: ")
            sqft = input("sqft: ")
        elif ptype == "land":
            sqft = input("sqft: ")
        else:
            return "Invalid property type."
            

        conn.commit()
        print("Property added.")
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed."

def search_property():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        city = input("Enter city: ")
        state = input("Enter state: ")
        min_price = float(input("Enter minimum price: "))
        max_price = float(input("Enter maximum price: "))

        cursor.execute("""
            SELECT * FROM property 
            WHERE city = %s AND state = %s AND rentalprice BETWEEN %s AND %s AND availability = 'Y'
        """, (city, state, min_price, max_price))

        properties = cursor.fetchall()
        if not properties:
            return "No properties found."

        for prop in properties:
            print(prop)
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed."
        
def update_property():
    """
    AGENT ONLY:
    """
    pass

def delete_property():
    """
    AGENT ONLY:
    """
    pass