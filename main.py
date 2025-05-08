from tkinter import *
from tkinter import ttk

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
        Label(self, text="Email:").grid(row=3, column=10, padx=10, pady=10)
        Label(self, text="Password:").grid(row=4, column=10, padx=10, pady=10)

        self.email_entry = Entry(self, width=35)
        self.password_entry = Entry(self, width=35, show='*')

        self.email_entry.grid(row=3, column=11, padx=10, pady=10)
        self.password_entry.grid(row=4, column=11, padx=10, pady=10)

        ttk.Button(self, text='Login', command=self.login).grid(row=5, column=10, columnspan=2, pady=10)
        ttk.Button(self, text='Register', command=self.register).grid(row=6, column=10, columnspan=2, pady=10)
        ttk.Button(self, text='Forgot Password', command=self.forgot_password).grid(row=4, column=12, padx=10, pady=10)

    def login(self):
        pass

    def register(self):
        pass

    def forgot_password(self):
        pass

    def show_about(self):
        print("About clicked")

    def show_contact(self):
        print("Contact clicked")



if __name__ == "__main__":
    rea = App(Tk())

    rea.parent.title("Real Estate Application")
    rea.parent.geometry("800x600")

    rea.mainloop()