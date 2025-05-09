from tkinter import *
from tkinter import ttk

class FormBuilder:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(expand=True, fill='both')
        self.fields = {}
        self.row = 0

    def add_fields(self, fields_dict, hide=False):
        for label, var in fields_dict.items():
            l = ttk.Label(self.frame, text=label)
            entry = ttk.Entry(self.frame, textvariable=var, show='*' if 'Password' in label else None)
            l.grid(row=self.row, column=0, padx=10, pady=5, sticky=E)
            entry.grid(row=self.row, column=1, padx=10, pady=5, sticky=EW)
            self.fields[label] = (l, entry)

            if hide:
                l.grid_remove()
                entry.grid_remove() 
            
            self.row += 1

    def get_values(self):
        return {label: var.get() for label, var in self.fields.items()}
    
    def get_field(self, label):
        return self.fields[label]
    
    def set_field(self, label, value):
        self.fields[label].set(value)
    
    def hide_field(self, fields_dict):
        for label in fields_dict:
            l, e = self.widgets[label]
            l.grid_remove()
            e.grid_remove()

    def show_field(self, fields_dict):
        for label in fields_dict:
            l, e = self.widgets[label]
            l.grid()
            e.grid()

    def add_checkbutton(self, text, var):
        check_button = ttk.Checkbutton(self.frame, text=text, variable=var)
        check_button.grid(row=self.row, column=0, columnspan=2, pady=10)
        self.row += 1

    def add_submit_buttons(self, submit_command, cancel_command, cancel_text="Cancel"):
        ttk.Button(self.frame, text="Submit", command=submit_command).grid(row=self.row, column=0, pady=10)
        ttk.Button(self.frame, text=cancel_text, command=cancel_command).grid(row=self.row, column=1, pady=10)