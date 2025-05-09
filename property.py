from connection import get_connection
from psycopg2 import sql, DatabaseError
# TODO: user auth logic, change to use CLI/GUI (i.e. tkinter)

from tkinter import *
from tkinter import ttk, messagebox

def property_menu():
    register_window = Toplevel()
    register_window.title("Property")
    register_window.geometry("800x600")

    ttk.Button(register_window, text="Add Property", command=add_property).grid(row=0, column=0, padx=10, pady=10, sticky=W)
    ttk.Button(register_window, text="Update Property", command=update_property).grid(row=1, column=0, padx=10, pady=10, sticky=W)
    ttk.Button(register_window, text="Delete Property", command=delete_property).grid(row=2, column=0, padx=10, pady=10, sticky=W)
    ttk.Button(register_window, text="Exit", command=register_window.destroy).grid(row=3, column=0, padx=10, pady=10, sticky=W)


def add_property():
    """ 
    AGENT ONLY: 
    Add a new property to the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    register_window = Toplevel()
    register_window.title("Add Property")
    register_window.geometry("800x600")
    ttk.Label(register_window, text="Property ID:").grid(row=1, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="City:").grid(row=2, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="State:").grid(row=3, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="Address:").grid(row=4, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="Description:").grid(row=5, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="Availability:").grid(row=6, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="Rental Price:").grid(row=7, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="Type:").grid(row=8, column=10, padx=10, pady=10)
    ttk.Label(register_window, text="Rooms:").grid(row=9, column=12, padx=10, pady=10)
    ttk.Label(register_window, text="Sqft:").grid(row=10, column=12, padx=10, pady=10)

    id_entry = ttk.Entry(register_window, width=35)
    city_entry = ttk.Entry(register_window, width=35)
    state_entry = ttk.Entry(register_window, width=35)
    address_entry = ttk.Entry(register_window, width=35)
    description_entry = ttk.Entry(register_window, width=35)
    availability_entry = ttk.Entry(register_window, width=35)
    price_entry = ttk.Entry(register_window, width=35)
    type_entry = ttk.Entry(register_window, width=35)
    room_entry = ttk.Entry(register_window, width=35)
    sqft_entry = ttk.Entry(register_window, width=35)

    id_entry.grid(row=1, column=11, padx=10, pady=10)
    city_entry.grid(row=2, column=11, padx=10, pady=10)
    state_entry.grid(row=3, column=11, padx=10, pady=10)
    address_entry.grid(row=4, column=11, padx=10, pady=10)
    description_entry.grid(row=5, column=11, padx=10, pady=10)
    availability_entry.grid(row=6, column=11, padx=10, pady=10)
    price_entry.grid(row=7, column=11, padx=10, pady=10)
    type_entry.grid(row=8, column=11, padx=10, pady=10)
    room_entry.grid(row=9, column=13, padx=10, pady=10)
    sqft_entry.grid(row=10, column=13, padx=10, pady=10)

    def submit():
        pid = id_entry.get()
        city = city_entry.get()
        state = state_entry.get()
        address = address_entry.get()
        desc = description_entry.get()
        avail = availability_entry.get()
        price = price_entry.get()
        type = type_entry.get()
        room = room_entry.get()
        sqft = sqft_entry.get()
        try:
            cursor.execute("""
                INSERT INTO property (propertyid, city, state, address, description, availability, rentalprice)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (pid, city, state, address, desc, avail, price))
            conn.commit()
            print(f"{cursor.rowcount} row(s) added.")
        except DatabaseError as e:
            conn.rollback()
            return f"Database error: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                return "Connection closed."
        
    ttk.Button(register_window, text="Submit", command=submit).grid(row=11, column=3, columnspan=2, pady=10)

def add_property_old():
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
    conn = get_connection()
    cursor = conn.cursor()

    try:
        id = input("Enter Property ID: ")
        i = True
        while i:
            selectData = input("What data do you want to modify? Select from the list\n\tA) City\n\tB) State\n\tC) Address\n\tD) Description\n\tE) Availability\n\tF) Rental Price\n\tG) Murder\n\tH) Robbery\n\tI) Battery\n\tJ) Nearby Schools\n\tK) Location\n\tL) Type\n")
            if selectData in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
                match selectData:
                    case 'A':
                        modify = input("Enter City: ")
                        cursor.execute("UPDATE Property SET City = %s WHERE PropertyID = %s", (modify, id))
                    case 'B':
                        modify = input("Enter State: ")
                        cursor.execute("UPDATE Property SET State = %s WHERE PropertyID = %s", (modify, id))
                    case 'C':
                        modify = input("Enter Address: ")
                        cursor.execute("UPDATE Property SET Address = %s WHERE PropertyID = %s", (modify, id))
                    case 'D':
                        modify = input("Enter Description: ")
                        cursor.execute("UPDATE Property SET Description = %s WHERE PropertyID = %s", (modify, id))
                    case 'E':
                        modify = input("Enter Availability: ")
                        cursor.execute("UPDATE Property SET Availability = %s WHERE PropertyID = %s", (modify, id))
                    case 'F':
                        modify = input("Enter Rental Price: ")
                        cursor.execute("UPDATE Property SET RentalPrice = %s WHERE PropertyID = %s", (modify, id))
                    case 'G':
                        modify = input("Enter Murder #: ")
                        cursor.execute("UPDATE Property SET Murder = %s WHERE PropertyID = %s", (modify, id))
                    case 'H':
                        modify = input("Enter Robbery #: ")
                        cursor.execute("UPDATE Property SET Robbery = %s WHERE PropertyID = %s", (modify, id))
                    case 'I':
                        modify = input("Enter Battery #: ")
                        cursor.execute("UPDATE Property SET Battery = %s WHERE PropertyID = %s", (modify, id))
                    case 'J':
                        modify = input("Enter Nearby Schools: ")
                        cursor.execute("UPDATE Property SET NearbySchools = %s WHERE PropertyID = %s", (modify, id))
                    case 'K':
                        modify = input("Enter Location: ")
                        cursor.execute("UPDATE Property SET Location = %s WHERE PropertyID = %s", (modify, id))
                    case 'L':
                        modify = input("Enter Type: ")
                        cursor.execute("UPDATE Property SET Type = %s WHERE PropertyID = %s", (modify, id))
                conn.commit()
                print(f"{cursor.rowcount} row(s) updated.")
                i = False
                

    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed"

def delete_property():
    """
    AGENT ONLY:
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        id = input("Enter Property ID to delete: ")
        cursor.execute("DELETE FROM Property WHERE PropertyID = %s", id)
        conn.commit()
        print(f"{cursor.rowcount} row(s) deleted.")

    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            return "Connection closed"