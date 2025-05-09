from connection import get_connection
from utils.forms import FormBuilder
from psycopg2 import sql, DatabaseError

from tkinter import *
from tkinter import ttk, messagebox


def add_property(parent):
    add_prop_win = Toplevel(parent)

    fields = {
        "Property ID": StringVar(),
        "City": StringVar(),
        "State": StringVar(),
        "Address": StringVar(),
        "Description": StringVar(),
        "Rental Price": DoubleVar(),
        "Murder": IntVar(),
        "Robbery": IntVar(),
        "Battery": IntVar(),
        "Nearby Schools": StringVar(),
        "Type": StringVar(),
        "Number Of Rooms": IntVar(),
        "Square Footage": IntVar()
    }

    form = FormBuilder(add_prop_win)
    form.add_fields(fields)

    def submit():
        conn = get_connection()
        cursor = conn.cursor()
        values = form.get_values()

        location = f"{values['Address']}, {values['City']}, {values['State']}"
        pid = values['Property ID']

        try:
            cursor.execute(
                "SELECT 1 FROM property WHERE propertyid = %s", (pid,))
            if cursor.fetchone():
                messagebox.showerror(
                    message=f"Duplicate Entry, Property ID {pid} already exists.")
                return

            cursor.execute("""
                            INSERT INTO property (propertyid, city, state, address, description, rentalprice, 
                            murder, robbery, battery, nearbyschools, location, type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (
                pid, values['City'], values['State'], values['Address'], values['Description'],
                values['Rental Price'], values['Murder'], values['Robbery'], values['Battery'],
                values['Nearby Schools'], location, values['Type']
            ))

            ptype = values['Type'].lower()
            rooms = values['Number Of Rooms']
            sqft = values['Square Footage']

            match ptype:
                case 'house':
                    cursor.execute(
                        "INSERT INTO house (propertyid, numberofrooms, squarefootage) VALUES (%s, %s, %s)", (pid, rooms, sqft))
                case 'apartment':
                    cursor.execute(
                        "INSERT INTO apartment (propertyid, numberofrooms, squarefootage, buildingtype) VALUES (%s, %s, %s, %s)", (pid, rooms, sqft, "Standard"))
                case 'commercialbuilding':
                    cursor.execute(
                        "INSERT INTO commercialbuilding (propertyid, squarefootage, businesstype) VALUES (%s, %s, %s)", (pid, sqft, "General"))
                case 'vacationhomes':
                    cursor.execute(
                        "INSERT INTO vacationhomes (propertyid, numberofrooms, squarefootage) VALUES (%s, %s, %s)", (pid, rooms, sqft))
                case 'land':
                    cursor.execute(
                        "INSERT INTO land (propertyid, squarefootage) VALUES (%s, %s, %s)", (pid, rooms, sqft))
                case _:
                    return messagebox.showwarning(message=f"Property type: {ptype} unsuporrted")

            conn.commit()
            messagebox.showinfo("Success", "Property added.")
            add_prop_win.destroy()
        except DatabaseError as e:
            conn.rollback()
            return f"Database Error: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    form.add_submit_buttons(submit, add_prop_win.destroy, "Exit")


def search_property(parent, current_user):
    search_prop_win = Toplevel(parent)

    fields = {
        "City": StringVar(),
        "State": StringVar(),
        "Minimum Price": DoubleVar(),
        "Maximum Price": DoubleVar()
    }

    form = FormBuilder(search_prop_win)
    form.add_fields(fields)

    conn = get_connection()
    cursor = conn.cursor()

    def submit():
        values = form.get_values()

        min_price = values["Minimum Price"] if values["Minimum Price"] else 0
        max_price = values["Maximum Price"] if values["Maximum Price"] else 9999999999

        if min_price > max_price:
            messagebox.showerror(
                "Invalid Price Range", "Minimum Price cannot be greater than Maximum Price.")
            return

        base_query = """
            SELECT propertyid, city, state, address, description, rentalprice
            FROM property
            WHERE availability = TRUE
        """

        conditions = []
        params = []

        if values["City"]:
            conditions.append("city = %s")
            params.append(values["City"])

        if values["State"]:
            conditions.append("state = %s")
            params.append(values["State"])

        conditions.append("rentalprice BETWEEN %s AND %s")
        params.extend([min_price, max_price])

        final_query = base_query
        if conditions:
            final_query += " AND " + " AND ".join(conditions)

        try:
            cursor.execute(final_query, tuple(params))
            properties = cursor.fetchall()

            if not properties:
                messagebox.showinfo(
                    "No Results", "No properties found matching the criteria.")
                return

            result_window = Toplevel(search_prop_win)
            result_window.title("Search Results")

            columns = ["propertyid", "city", "state",
                       "address", "description", "rentalprice"]
            result_tree = ttk.Treeview(
                result_window, columns=columns, show="headings")
            for col in columns:
                result_tree.heading(col, text=col.capitalize())
                result_tree.column(col, anchor=CENTER)

            result_tree.pack(fill=BOTH, expand=True)
            for property in properties:
                result_tree.insert("", "end", values=property)

            if current_user["role"] == "agent":
                result_tree.bind("<Double-1>", lambda event: update_property(
                    result_window, result_tree.item(result_tree.selection())["values"][0]))

            result_window.protocol("WM_DELETE_WINDOW", lambda: (
                result_window.destroy(), search_prop_win.deiconify()))
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror(message=f"Database Error: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    form.add_submit_buttons(submit, search_prop_win.destroy, "Exit")


def update_property(parent, property_id):
    update_prop_win = Toplevel(parent)
    update_prop_win.title(f"Update Property {property_id}")

    valid_fields = {
        "City": StringVar(),
        "State": StringVar(),
        "Address": StringVar(),
        "Description": StringVar(),
        "Availability": BooleanVar(),
        "RentalPrice": DoubleVar(),
        "Murder": IntVar(),
        "Robbery": IntVar(),
        "Battery": IntVar(),
        "NearbySchools": StringVar(),
        "Type": StringVar()
    }

    map = {field: field.lower().replace(" ", "").replace("_", "")
           for field in valid_fields.keys()}
    map["Location"] = "location"
    map["PropertyID"] = "propertyid"

    form = FormBuilder(update_prop_win)
    form.add_fields(valid_fields)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT type FROM property WHERE propertyid = %s", (property_id,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror(
                message=f"Property ID {property_id} not found.")
            update_prop_win.destroy()
            return
        ptype = result[0].lower()

        type_fields = {}
        if ptype in {"house", "vacationhomes", "apartment"}:
            type_fields["NumberOfRooms"] = IntVar()
            type_fields["SquareFootage"] = IntVar()
        elif ptype in {"commercialbuilding", "land"}:
            type_fields["SquareFootage"] = IntVar()

        form.add_fields(type_fields)

        if not form.load_from_db(cursor, "property", "propertyid", property_id, valid_fields):
            messagebox.showerror(
                message=f"Property ID {property_id} does not exist.")
            update_prop_win.destroy()
            return

        if not form.load_from_db(cursor, ptype, "propertyid", property_id, type_fields):
            messagebox.showerror(
                message=f"Property ID {property_id} does not exist.")
            update_prop_win.destroy()
            return
    except DatabaseError as e:
        conn.rollback()
        messagebox.showerror(message=f"Database Error: {e}")
        update_prop_win.destroy()
        return

    def submit():
        values = form.get_values()
        update_values = []
        update_columns = []

        for field, value in values.items():
            if field in valid_fields and value not in (None, "", 0):
                update_columns.append(map[field])
                update_values.append(value)

        if any(values.get(k) for k in ["Address", "City", "State"]):
            location = f"{values.get('Address', '')}, {values.get('City', '')}, {values.get('State', '')}"
            update_columns.append("location")
            update_values.append(location)

        if not update_columns:
            messagebox.showinfo(
                "No Updates", "Please fill in at least one field to update.")
            return

        update_values.append(property_id)

        assignments = [
            sql.SQL("{} = %s").format(sql.Identifier(col)) for col in update_columns
        ]
        query = sql.SQL("UPDATE Property SET {} WHERE propertyid = %s").format(
            sql.SQL(", ").join(assignments)
        )

        try:
            cursor.execute(query, tuple(update_values))

            type_update_values = []
            type_update_columns = []
            if "NumberOfRooms" in values:
                type_update_columns.append("numberofrooms")
                type_update_values.append(values["NumberOfRooms"])
            if "SquareFootage" in values:
                type_update_columns.append("squarefootage")
                type_update_values.append(values["SquareFootage"])

            if type_update_columns:
                set_clause = ", ".join(
                    f"{col} = %s" for col in type_update_columns)
                type_update_values.append(property_id)
                cursor.execute(
                    f"UPDATE {ptype} SET {set_clause} WHERE propertyid = %s",
                    tuple(type_update_values)
                )

            conn.commit()
            messagebox.showinfo("Success", "Property updated.")
            update_prop_win.destroy()
        except DatabaseError as e:
            conn.rollback()
            messagebox.showerror(message=f"Database Error: {e}")
        finally:
            cursor.close()
            conn.close()

    form.add_submit_buttons(submit, update_prop_win.destroy, "Exit")

    def on_close():
        cursor.close()
        conn.close()
        update_prop_win.destroy()

    update_prop_win.protocol("WM_DELETE_WINDOW", on_close)


def delete_property(property_id):
    if not property_id:
        messagebox.showerror("Missing Input", "Property ID cannot be empty.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT type FROM property WHERE propertyid = %s", (property_id,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror(
                message=f"Property ID {property_id} does not exists.")
            return

        ptype = result[0].lower()

        cursor.execute(sql.SQL("DELETE FROM {} WHERE propertyid = %s").format(
            sql.Identifier(ptype)), (property_id,))
        cursor.execute(
            "DELETE FROM Property WHERE propertyid = %s", (property_id,))

        conn.commit()
        messagebox.showinfo("Success", "Property deleted.")
    except DatabaseError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
