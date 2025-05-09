from tkinter import *
from tkinter import ttk, messagebox
from auth import register_user, login_user
from property import *

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
        container.rowconfigure(2, weight=1) # for spacing
        container.columnconfigure(0, weight=1)

        login_frame = ttk.Frame(container)
        login_frame.grid(row=1, column=0, sticky=NSEW) # row 1 = center row.

        login_frame.columnconfigure(1, weight=1)

        login_frame.rowconfigure(0, weight=1)

        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, padx=10, pady=10, sticky=E)
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky=E)

        self.email_entry = ttk.Entry(login_frame, width=30)
        self.password_entry = ttk.Entry(login_frame, width=30, show='*')

        self.email_entry.grid(row=0, column=1, padx=10, pady=10, sticky=EW)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=EW)

        ttk.Button(login_frame, text='Login', command=self.login).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(login_frame, text='Register', command=self.register).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(login_frame, text='Forgot Password', command=self.forgot_password).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(login_frame, text='Exit', command=self.quit).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.parent.bind('<Return>', lambda event: self.login()) # Bind Enter key to login

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showinfo("Login Unsuccessful", "Please enter both email and password.")
            return
        
        result = login_user(email, password)
        if result == "Login successful.":
            # Proceed to the next step in the application
            property_menu() #this is still based on property.py btw
            print("finished 😫")
        else:
            messagebox.showinfo(result)

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

        labels = {
            "Email": StringVar(),
            "First Name": StringVar(),
            "Last Name": StringVar(),
            "Password": StringVar(),
        }
        fields = {}

        admin_fields = {
            "Job Title": StringVar(),
            "Agency": StringVar(),
            "Phone Number": StringVar(),
        }
        admin_widgets = {}

        for i, (label, var) in enumerate(labels.items()):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=E)
            entry = ttk.Entry(form_frame, textvariable=var, show='*' if label == "Password" else None)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=EW)
            fields[label] = entry

        is_admin = BooleanVar()
        ttk.Checkbutton(form_frame, text="Register as Admin", variable=is_admin).grid(row=len(fields), column=0, columnspan=2, pady=10)

        for i, (label, var) in enumerate(admin_fields.items()):
            field = ttk.Label(form_frame, text=label)
            entry = ttk.Entry(form_frame, textvariable=var)
            field.grid(row=len(fields)+1+i, column=0, padx=10, pady=5, sticky=E)
            entry.grid(row=len(fields)+1+i, column=1, padx=10, pady=5, sticky=EW)
            field.grid_remove()
            entry.grid_remove()
            admin_widgets[label] = (field, entry)

        budget_var = StringVar()
        location_var = StringVar()

        budget_label = ttk.Label(form_frame, text="Budget:")
        budget_entry = ttk.Entry(form_frame, textvariable=budget_var)
        location_label = ttk.Label(form_frame, text="Preferred Location:")
        location_entry = ttk.Entry(form_frame, textvariable=location_var)

        renter_row = len(fields) + len(admin_fields) + 1
        budget_label.grid(row=renter_row, column=0, padx=10, pady=5, sticky=E)
        budget_entry.grid(row=renter_row, column=1, padx=10, pady=5, sticky=EW)
        location_label.grid(row=renter_row + 1, column=0, padx=10, pady=5, sticky=E)
        location_entry.grid(row=renter_row + 1, column=1, padx=10, pady=5, sticky=EW)

        def on_admin():
            if is_admin.get():
                for label, (l, e) in admin_widgets.items():
                    l.grid()
                    e.grid()
                budget_label.grid_remove()
                budget_entry.grid_remove()
                location_label.grid_remove()
                location_entry.grid_remove()
            else:
                for label, (l, e) in admin_widgets.items():
                    l.grid_remove()
                    e.grid_remove()
                budget_label.grid()
                budget_entry.grid()
                location_label.grid()
                location_entry.grid()

        is_admin.trace_add("write", lambda *args: on_admin())

        def submit():
            email = labels["Email"].get()
            first_name = labels["First Name"].get()
            last_name = labels["Last Name"].get()
            password = labels["Password"].get()
            role = "admin" if is_admin.get() else "user"

            extra_info = {
                "job_title": admin_fields["Job Title"].get() if is_admin.get() else None,
                "agency": admin_fields["Agency"].get() if is_admin.get() else None,
                "phone_number": admin_fields["Phone Number"].get() if is_admin.get() else None,
                "budget": budget_var.get() if not is_admin.get() else None,
                "location": location_var.get() if not is_admin.get() else None
            }

            result = register_user(email, first_name, last_name, password, role, extra_info)
            if result == "User registered successfully.":
                messagebox.showinfo("Success", result)
                register_window.destroy()
            else:
                messagebox.showerror("Error", result)

        ttk.Button(form_frame, text="Submit", command=submit).grid(row=renter_row + 2, column=0, columnspan=2, pady=10)
        ttk.Button(form_frame, text="Cancel", command=register_window.destroy).grid(row=renter_row + 3, column=0, columnspan=2, pady=5)

        register_window.bind('<Return>', lambda event: submit())
        register_window.bind('<Escape>', lambda event: register_window.destroy())
        
    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Not Implemented yet.")

    def show_about(self):
        messagebox.showinfo("About", "Real Estate Application\nVersion 1.0\nDeveloped by Dylan Figueredo, Kyle Grant, and Martin Harmon")

    def show_contact(self):
        messagebox.showinfo("Contact us at:", "Don't contact us.")

    def property_menu(self):
        register_window = Toplevel(self.parent)
        register_window.title("Property")
        register_window.geometry("800x600")

        ttk.Button(register_window, text="Add Property", command=add_property).grid(row=0, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(register_window, text="Update Property", command=update_property).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(register_window, text="Delete Property", command=delete_property).grid(row=2, column=0, padx=10, pady=10, sticky=W)
        ttk.Button(register_window, text="Exit", command=register_window.destroy).grid(row=3, column=0, padx=10, pady=10, sticky=W)

if __name__ == "__main__":
    rea = App(Tk())

    rea.parent.title("Real Estate Application")
    rea.parent.geometry("400x300")

    rea.mainloop()