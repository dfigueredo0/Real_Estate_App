from tkinter import *
from tkinter import ttk, messagebox
from auth import register_user, login_user
from property import *

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack()
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
        ttk.Label(self, text="Email:").grid(row=3, column=10, padx=10, pady=10)
        ttk.Label(self, text="Password:").grid(row=4, column=10, padx=10, pady=10)

        self.email_entry = ttk.Entry(self, width=35)
        self.password_entry = ttk.Entry(self, width=35, show='*')

        self.email_entry.grid(row=3, column=11, padx=10, pady=10)
        self.password_entry.grid(row=4, column=11, padx=10, pady=10)

        ttk.Button(self, text='Login', command=self.login).grid(row=5, column=10, columnspan=2, pady=10)
        ttk.Button(self, text='Register', command=self.register).grid(row=6, column=10, columnspan=2, pady=10)
        ttk.Button(self, text='Forgot Password', command=self.forgot_password).grid(row=4, column=12, padx=10, pady=10)

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
        register_window.geometry("800x600")

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
            ttk.Label(register_window, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=W)
            entry = ttk.Entry(register_window, textvariable=var, width=35, show='*' if label == "Password" else None)
            entry.grid(row=i, column=1, padx=10, pady=10)
            fields[label] = entry

        budget_var = StringVar()
        budget_label = ttk.Label(register_window, text="Budget:")
        budget_label.grid(row=len(fields)+2+len(admin_fields), column=0, padx=10, pady=10, sticky=W)
        budget_entry = ttk.Entry(register_window, textvariable=budget_var, width=35)
        budget_entry.grid(row=len(fields)+2+len(admin_fields), column=1, padx=10, pady=10)

        location_var = StringVar()
        location_label = ttk.Label(register_window, text="Preferred Location:")
        location_label.grid(row=len(fields)+3+len(admin_fields), column=0, padx=10, pady=10, sticky=W)
        location_entry = ttk.Entry(register_window, textvariable=location_var, width=35)
        location_entry.grid(row=len(fields)+3+len(admin_fields), column=1, padx=10, pady=10)

        def on_admin():
            if is_admin.get():
                for field, (label, entry) in admin_widgets.items():
                    label.grid()
                    entry.grid()
                budget_label.grid_remove()
                budget_entry.grid_remove()
                location_label.grid_remove()
                location_entry.grid_remove()
            else:
                for field, (label, entry) in admin_widgets.items():
                    label.grid_remove()
                    entry.grid_remove()
                budget_label.grid()
                budget_entry.grid()
                location_label.grid()
                location_entry.grid()

        is_admin = BooleanVar()
        ttk.Checkbutton(register_window, text="Register as Admin", variable=is_admin, command=on_admin).grid(row=len(fields), column=0, columnspan=2, pady=10)

        for i, (label, var) in enumerate(admin_fields.items()):
            field = ttk.Label(register_window, text=label)
            field.grid(row=len(fields)+2+i, column=0, padx=10, pady=10, sticky=W)
            entry = ttk.Entry(register_window, textvariable=var, width=35)
            entry.grid(row=len(fields)+2+i, column=1, padx=10, pady=10)
            field.grid_remove()
            entry.grid_remove()
            admin_widgets[label] = (field, entry)

        

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
        
        ttk.Button(register_window, text="Submit", command=submit).grid(row=len(fields), column=3, columnspan=2, pady=10)
        
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
    rea.parent.geometry("800x600")

    rea.mainloop()