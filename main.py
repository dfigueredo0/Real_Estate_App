from tkinter import *
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring

from auth import *
from property import *
from payment import *
from booking import *
from address import *


class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(expand=True, fill='both')
        self.init_UI()
        self.init_login()

    def init_UI(self):
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Contact", command=self.show_contact)
        menubar.add_cascade(label="Help", menu=help_menu)

    def init_login(self):
        container = ttk.Frame(self)
        container.pack(expand=True, fill='both')

        container.rowconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)  # for spacing
        container.columnconfigure(0, weight=1)

        login_frame = ttk.Frame(container)
        login_frame.grid(row=1, column=0, sticky=NSEW)  # row 1 = center row.

        login_frame.columnconfigure(1, weight=1)

        login_frame.rowconfigure(0, weight=1)

        ttk.Label(login_frame, text="Email:").grid(
            row=0, column=0, padx=10, pady=10, sticky=E)
        ttk.Label(login_frame, text="Password:").grid(
            row=1, column=0, padx=10, pady=10, sticky=E)

        self.email_entry = ttk.Entry(login_frame, width=30)
        self.password_entry = ttk.Entry(login_frame, width=30, show='*')

        self.email_entry.grid(row=0, column=1, padx=10, pady=10, sticky=EW)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=EW)

        ttk.Button(login_frame, text='Login', command=self.login).grid(
            row=3, column=0, columnspan=2, pady=5)
        ttk.Button(login_frame, text='Register', command=self.register).grid(
            row=4, column=0, columnspan=2, pady=5)
        ttk.Button(login_frame, text='Forgot Password', command=self.forgot_password).grid(
            row=2, column=0, columnspan=2, pady=5)
        ttk.Button(login_frame, text='Exit', command=self.quit).grid(
            row=5, column=0, columnspan=2, pady=10)

        # Bind Enter key to login
        self.parent.bind('<Return>', lambda event: self.login())

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        result = handle_login(email, password)

        if result == "Login successful.":
            role = get_user_role(email)
            self.current_user = {
                "email": email,
                "role": role
            }

            self.property()
            if role == "renter":
                self.renter_dashboard()
            else:
                self.booking()

            print("finished 😫")
        else:
            messagebox.showinfo(result)

    def renter_dashboard(self):
        dashboard = Toplevel(self.parent)
        dashboard.title("Renter Dashboard")
        dashboard.geometry("500x400")

        ttk.Button(dashboard, text="Manage Bookings", command=lambda: self.booking_window(
            dashboard)).grid(row=0, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(dashboard, text="Manage Payment", command=lambda: self.payment_window(
            dashboard)).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(dashboard, text="Manage Addresses", command=lambda: manage_addresses(
            dashboard, self.current_user)).grid(row=2, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(dashboard, text="Exit", command=dashboard.destroy).grid(
            row=3, column=0, padx=10, pady=10, sticky=W)

    def booking_window(self, parent):
        booking_window = Toplevel(parent)
        booking_window.title("Booking")
        booking_window.geometry("400x300")

        ttk.Button(booking_window, text="Add Booking", command=lambda: book_property(
            booking_window, self.current_user)).grid(row=0, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(booking_window, text="View My Bookings",
                   command=lambda: view_user_bookings(booking_window, self.current_user)).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(booking_window, text="View Available Bookings", command=lambda: view_available_bookings(
            booking_window)).grid(row=1, column=1, padx=10, pady=10, sticky=W)
        ttk.Button(booking_window, text="Cancel Booking", command=lambda: cancel_booking(
            self.current_user, self.prompt_booking_id())).grid(row=2, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(booking_window, text="Exit", command=booking_window.destroy).grid(
            row=3, column=0, padx=10, pady=10, sticky=W)

    def payment_window(self, parent):
        payment_window = Toplevel(parent)
        payment_window.title("Payment")
        payment_window.geometry("400x300")

        ttk.Button(payment_window, text="Add Card", command=lambda: add_card(
            payment_window, self.current_user)).grid(row=0, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(payment_window, text="Update Card", command=lambda: update_card(
            payment_window, self.current_user, self.prompt_card_number())).grid(row=0, column=1, padx=10, pady=10, sticky=W)
        ttk.Button(payment_window, text="View Cards", command=lambda: view_cards(
            payment_window, self.current_user)).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(payment_window, text="Delete Card", command=lambda: delete_card(
            payment_window, self.current_user)).grid(row=2, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(payment_window, text="Exit", command=payment_window.destroy).grid(
            row=3, column=0, padx=10, pady=10, sticky=W)

    def register(self):
        register_window = Toplevel(self.parent)
        register_window.title("Register")
        register_window.geometry("500x400")

        container = ttk.Frame(register_window)
        container.pack(expand=True, fill="both")

        container.rowconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)

        form_frame = ttk.Frame(container)
        form_frame.grid(row=1, column=0, sticky=NSEW)
        form_frame.columnconfigure(1, weight=1)

        form = FormBuilder(form_frame)

        user_fields = {
            "Email": StringVar(),
            "First Name": StringVar(),
            "Last Name": StringVar(),
            "Password": StringVar(),
        }

        agent_fields = {
            "Job Title": StringVar(),
            "Agency": StringVar(),
            "Phone Number": StringVar(),
        }

        renter_fields = {
            "Budget": DoubleVar(),
            "Preferred Location": StringVar()
        }

        is_agent = BooleanVar()
        form.add_checkbutton("Register as an Agent", is_agent)

        form.add_fields(user_fields)
        form.add_fields(agent_fields, hide=True)
        form.add_fields(renter_fields)

        def toggle_agent_fields():
            if is_agent.get():
                form.show_field(agent_fields)
                form.hide_field(renter_fields)
            else:
                form.hide_field(agent_fields)
                form.show_field(renter_fields)

        is_agent.trace_add("write", lambda *_, __=None: toggle_agent_fields())

        def on_submit():
            result = process_registration_form(
                fields=user_fields,
                is_agent=is_agent,
                agent_fields=agent_fields,
                renter_fields=renter_fields
            )

            if result == "User registered successfully.":
                messagebox.showinfo("Success", result)
                register_window.destroy()
            else:
                messagebox.showerror("Error", result)

        form.add_submit_buttons(on_submit, register_window.destroy)

        register_window.bind('<Return>', lambda event: on_submit())
        register_window.bind(
            '<Escape>', lambda event: register_window.destroy())

    def forgot_password(self):
        email = askstring("Reset Password", "Enter your email address:")
        if email:
            reset_password(email)

    def show_about(self):
        messagebox.showinfo(
            "About", "Real Estate Application\nVersion 1.0\nDeveloped by Dylan Figueredo, Kyle Grant, and Martin Harmon")

    def show_contact(self):
        messagebox.showinfo("Contact us at:", "Don't contact us.")

    def prompt_pid(self):
        property_id = askstring("Property ID", "Enter the Property ID:")
        if property_id is None:
            return None
        return property_id

    def prompt_card_number(self):
        card_number = askstring("Card Number", "Enter your Card Number")
        if card_number is None:
            return None
        return card_number

    def prompt_booking_id(self):
        booking_id = askstring("Booking ID", "Enter the Booking ID:")
        if booking_id is None:
            return None
        return booking_id

    def property(self):
        property_window = Toplevel(self.parent)
        property_window.title("Property")
        property_window.geometry("400x300")

        is_agent = self.current_user.get("role") == "agent"

        if is_agent:
            ttk.Button(property_window, text="Add Property", command=lambda: add_property(
                self.parent)).grid(row=0, column=0, padx=10, pady=10, sticky=W)
            ttk.Button(property_window, text="Update Property", command=lambda: update_property(
                self.parent, self.prompt_pid())).grid(row=1, column=0, padx=10, pady=10, sticky=W)
            ttk.Button(property_window, text="Delete Property", command=lambda: delete_property(
                self.prompt_pid())).grid(row=2, column=0, padx=10, pady=10, sticky=W)
            ttk.Button(property_window, text="Search Property", command=lambda: search_property(
                self.parent, self.current_user)).grid(row=0, column=1, padx=10, pady=10, sticky=W)
        else:
            ttk.Button(property_window, text="Search Property", command=lambda: search_property(
                self.parent, self.current_user)).grid(row=0, column=0, padx=10, pady=10, sticky=W)

        ttk.Button(property_window, text="Exit", command=property_window.destroy).grid(
            row=3, column=0, padx=10, pady=10, sticky=W)

    def booking(self):
        booking_window = Toplevel(self.parent)
        booking_window.title("Booking")
        booking_window.geometry("400x300")

        if self.current_user['role'] == 'agent':
            ttk.Button(booking_window, text="View Bookings", command=lambda: view_agent_bookings(
                booking_window, self.current_user)).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        else:
            self.renter_dashboard()


if __name__ == "__main__":
    rea = App(Tk())

    rea.parent.title("Real Estate Application")
    rea.parent.geometry("400x300")

    rea.mainloop()
