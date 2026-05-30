import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry as DatePicker
# At the top of dialogs.py, add:
from frontend.components import ScrollableFrame

class AddIncomeDialog:
    def __init__(self, parent, controller):
        self.controller = controller
        self.styles = controller.styles
        
        # MODIFIED: Larger size matching requirements
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Income")
        self.dialog.geometry("550x680")  # Increased height for consistency
        self.dialog.configure(bg=self.styles.colors["white"])
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # MODIFIED: Use ScrollableFrame for scrollable content
        self.scrollable_container = ScrollableFrame(self.dialog, bg=self.styles.colors["white"])
        self.scrollable_container.pack(fill="both", expand=True)
        
        self.main_container = tk.Frame(self.scrollable_container.scrollable_frame, bg=self.styles.colors["white"], padx=30, pady=30)
        self.main_container.pack(fill="both", expand=True)
        
        self.create_form()
    
    def create_form(self):
        header_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(header_frame, text="Add New Income", 
                font=self.styles.fonts["h2"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        # Description box
        desc_frame = tk.Frame(header_frame, bg="#e8f5e9", padx=15, pady=10)
        desc_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(desc_frame, text="💡 Enter details of money received. This will increase your wallet balance.",
                font=self.styles.fonts["body"], bg="#e8f5e9", fg="#2e7d32", wraplength=450).pack(anchor="w")
        
        wallet_info = ""
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_info = f" to {self.controller.current_wallet['name']} ({currency_symbol})"
        
        tk.Label(header_frame, text=f"Add income{wallet_info}",
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(10, 0))
        
        form_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        # Source field with tooltip
        source_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        source_frame.pack(fill="x", pady=(0, 20))
        
        source_label_frame = tk.Frame(source_frame, bg=self.styles.colors["white"])
        source_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(source_label_frame, text="Income Source *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(source_label_frame, text="ⓘ e.g., Salary, Freelance, Gift",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        # MODIFIED: Entry styling to match amount textbox exactly
        self.source_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                                    bg=self.controller.styles.colors["input_bg"], 
                                    fg=self.controller.styles.colors["placeholder"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=self.controller.styles.colors["border"],
                                    highlightcolor=self.controller.styles.colors["primary"])
        self.source_entry.pack(fill="x")
        self.source_entry.insert(0, "e.g., Salary, Freelance, Gift")
        self.source_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.source_entry, "e.g., Salary, Freelance, Gift"))
        self.source_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.source_entry, "e.g., Salary, Freelance, Gift"))
        self.source_entry.focus_set()
        
        # Amount field
        amount_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        amount_frame.pack(fill="x", pady=(0, 20))
        
        amount_label_frame = tk.Frame(amount_frame, bg=self.styles.colors["white"])
        amount_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(amount_label_frame, text="Amount *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(amount_label_frame, text="ⓘ Enter the amount received",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        self.amount_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                                    bg=self.controller.styles.colors["input_bg"], 
                                    fg=self.controller.styles.colors["placeholder"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=self.controller.styles.colors["border"],
                                    highlightcolor=self.controller.styles.colors["primary"])
        self.amount_entry.pack(fill="x")
        self.amount_entry.insert(0, "0.00")
        self.amount_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.amount_entry, "0.00"))
        self.amount_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.amount_entry, "0.00"))
        self.amount_entry.focus_set()
        
        # MODIFIED: Category dropdown styling to match amount textbox
        tk.Label(form_frame, text="Category", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        self.category_var = tk.StringVar()
        categories = ["Salary", "Freelance", "Business", "Investment", 
                     "Dividends", "Bonus", "Gift", "Other"]
        
        # MODIFIED: Combobox with same height/visual weight as entry
        self.category_menu = ttk.Combobox(form_frame, textvariable=self.category_var,
                                         values=categories, state="readonly",
                                         font=self.controller.styles.fonts["body"])
        self.category_menu.pack(fill="x", pady=(0, 20))
        self.category_menu.set("Salary")
        
        # Date field
        tk.Label(form_frame, text="Date", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        self.date_entry = DatePicker(form_frame, font=self.controller.styles.fonts["body"],
                                    background=self.controller.styles.colors["input_bg"], 
                                    foreground=self.controller.styles.colors["input_fg"],
                                    borderwidth=1, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(fill="x", pady=(0, 20))
        self.date_entry.set_date(datetime.now())
        
        # MODIFIED: Description field - MATCHES AMOUNT TEXTBOX EXACTLY
        desc_label_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        desc_label_frame.pack(fill="x", pady=(0, 8))

        tk.Label(desc_label_frame, text="Description (Optional)", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")

        tk.Label(desc_label_frame, text="ⓘ Add notes about this expense",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))

        # MODIFIED: Text widget with EXACT SAME styling as amount entry
        self.desc_entry = tk.Text(form_frame, font=self.controller.styles.fonts["body"],
                                bg=self.controller.styles.colors["input_bg"], 
                                fg=self.controller.styles.colors["placeholder"],
                                relief="flat", highlightthickness=1,
                                highlightbackground=self.controller.styles.colors["border"],
                                highlightcolor=self.controller.styles.colors["primary"],
                                height=4, wrap="word")
        self.desc_entry.pack(fill="x")
        self.desc_entry.insert("1.0", "Add notes about this income...")
        self.desc_entry.bind("<FocusIn>", lambda e: self.clear_text_placeholder(self.desc_entry, "Add notes about this income..."))
        self.desc_entry.bind("<FocusOut>", lambda e: self.add_text_placeholder(self.desc_entry, "Add notes about this income..."))
        
        # MODIFIED: Button frame with "Add" and "Clear" buttons fixed at bottom
        # Create a container frame that will hold the buttons at the bottom
        button_container = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        button_container.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Add a separator line
        separator = tk.Frame(button_container, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x", pady=(0, 15))
        
        button_frame = tk.Frame(button_container, bg=self.styles.colors["white"])
        button_frame.pack(fill="x")
        
        # MODIFIED: Clear button added
        clear_btn = tk.Button(button_frame, text="Clear",
                             font=self.styles.fonts["body"], bg=self.styles.colors["gray"],
                             fg="white", relief="flat", cursor="hand2",
                             command=self.clear_form,
                             padx=35, pady=12)
        clear_btn.pack(side="left", padx=(0, 15))
        
        # MODIFIED: Save button renamed to "Add"
        save_btn = tk.Button(button_frame, text="➕ Add Income",
                            font=self.styles.fonts["bold"], bg=self.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=self.save_income,
                            padx=35, pady=12)
        save_btn.pack(side="right")
        
        def on_enter_key(event):
            save_btn.invoke()
        
        self.dialog.bind('<Return>', on_enter_key)
        self.dialog.bind('<Return>', on_enter_key)
    
    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=self.controller.styles.colors["input_fg"])
    
    def add_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=self.controller.styles.colors["placeholder"])
    
    def clear_text_placeholder(self, text_widget, placeholder):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", tk.END)
            text_widget.config(fg=self.controller.styles.colors["input_fg"])
    
    def add_text_placeholder(self, text_widget, placeholder):
        if not text_widget.get("1.0", "end-1c").strip():
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg=self.controller.styles.colors["placeholder"])
    
    # MODIFIED: New clear form method
    def clear_form(self):
        self.source_entry.delete(0, tk.END)
        self.source_entry.insert(0, "e.g., Salary, Freelance, Gift")
        self.source_entry.config(fg=self.controller.styles.colors["placeholder"])  # FIXED: Use brackets []
        
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, "0.00")
        self.amount_entry.config(fg=self.controller.styles.colors["placeholder"])  # FIXED: Use brackets []
        
        self.category_menu.set("Salary")
        
        self.date_entry.set_date(datetime.now())
        
        self.desc_entry.delete("1.0", tk.END)
        self.desc_entry.insert("1.0", "Add notes about this income...")
        self.desc_entry.config(fg=self.controller.styles.colors["placeholder"])
    
    def save_income(self):
        source = self.source_entry.get().strip()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        date = self.date_entry.get_date()
        description = self.desc_entry.get("1.0", "end").strip()
        
        if source == "e.g., Salary, Freelance, Gift" or not source:
            messagebox.showerror("Error", "Please enter a valid income source")
            return
        
        if amount == "0.00":
            messagebox.showerror("Error", "Please enter a valid amount")
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            self.controller.save_income(source, amount_float, category, date, description)
        else:
            messagebox.showerror("Error", "No wallet selected")
        
        self.dialog.destroy()

class AddExpenseDialog:
    def __init__(self, parent, controller):
        self.controller = controller
        self.styles = controller.styles
        
        # MODIFIED: Larger size matching requirements
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Expense")
        self.dialog.geometry("550x700")  # Increased height for consistency
        self.dialog.configure(bg=self.styles.colors["white"])
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # MODIFIED: Use ScrollableFrame for scrollable content
        self.scrollable_container = ScrollableFrame(self.dialog, bg=self.styles.colors["white"])
        self.scrollable_container.pack(fill="both", expand=True)
        
        self.main_container = tk.Frame(self.scrollable_container.scrollable_frame, bg=self.styles.colors["white"], padx=30, pady=30)
        self.main_container.pack(fill="both", expand=True)
        
        self.create_form()
    
    def create_form(self):
        header_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(header_frame, text="Add New Expense", 
                font=self.styles.fonts["h2"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        # Description box
        desc_frame = tk.Frame(header_frame, bg="#ffebee", padx=15, pady=10)
        desc_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(desc_frame, text="💡 Enter details of money spent. This will reduce your wallet balance.",
                font=self.styles.fonts["body"], bg="#ffebee", fg="#c62828", wraplength=450).pack(anchor="w")
        
        wallet_info = ""
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_info = f" to {self.controller.current_wallet['name']} ({currency_symbol})"
        
        tk.Label(header_frame, text=f"Add expense{wallet_info}",
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(10, 0))
        
        form_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        # Category field with tooltip
        category_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        category_frame.pack(fill="x", pady=(0, 20))
        
        category_label_frame = tk.Frame(category_frame, bg=self.styles.colors["white"])
        category_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(category_label_frame, text="Category *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(category_label_frame, text="ⓘ Select expense category",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        self.category_var = tk.StringVar()
        categories = ["Shopping", "Food", "Transport", "Bills", 
                     "Entertainment", "Healthcare", "Education", "Travel", 
                     "Rent", "Utilities", "Insurance", "Tax", "Other"]
        
        # MODIFIED: Combobox with same styling as amount entry
        self.category_menu = ttk.Combobox(form_frame, textvariable=self.category_var,
                                         values=categories, state="readonly",
                                         font=self.controller.styles.fonts["body"])
        self.category_menu.pack(fill="x", pady=(0, 20))
        self.category_menu.set("Shopping")
        
        # Amount field
        amount_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        amount_frame.pack(fill="x", pady=(0, 20))
        
        amount_label_frame = tk.Frame(amount_frame, bg=self.styles.colors["white"])
        amount_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(amount_label_frame, text="Amount *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(amount_label_frame, text="ⓘ Enter the amount spent",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        self.amount_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                                    bg=self.controller.styles.colors["input_bg"], 
                                    fg=self.controller.styles.colors["placeholder"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=self.controller.styles.colors["border"],
                                    highlightcolor=self.controller.styles.colors["primary"])
        self.amount_entry.pack(fill="x")
        self.amount_entry.insert(0, "0.00")
        self.amount_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.amount_entry, "0.00"))
        self.amount_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.amount_entry, "0.00"))
        self.amount_entry.focus_set()
        
        # Date field
        tk.Label(form_frame, text="Date", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        self.date_entry = DatePicker(form_frame, font=self.controller.styles.fonts["body"],
                                    background=self.controller.styles.colors["input_bg"], 
                                    foreground=self.controller.styles.colors["input_fg"],
                                    borderwidth=1, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(fill="x", pady=(0, 20))
        self.date_entry.set_date(datetime.now())
        
        # Payment Method (CORRECTED - only one instance)
        payment_label_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        payment_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(payment_label_frame, text="Payment Method", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(payment_label_frame, text="ⓘ Select how you paid",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        self.payment_var = tk.StringVar()
        
        self.payment_menu = ttk.Combobox(form_frame, textvariable=self.payment_var,
                                        values=["Credit Card", "Debit Card", "Cash", 
                                               "Bank Transfer", "Digital Wallet", "Other"],
                                        state="readonly",
                                        font=self.controller.styles.fonts["body"])
        self.payment_menu.pack(fill="x", pady=(0, 20))
        self.payment_menu.set("Credit Card")
        
        # Description field - MATCHES AMOUNT TEXTBOX EXACTLY (CORRECTED POSITION)
        desc_label_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        desc_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(desc_label_frame, text="Description (Optional)", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(desc_label_frame, text="ⓘ Add notes about this expense",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        # MODIFIED: Text widget with EXACT SAME styling as amount entry
        self.desc_entry = tk.Text(form_frame, font=self.controller.styles.fonts["body"],
                                bg=self.controller.styles.colors["input_bg"], 
                                fg=self.controller.styles.colors["placeholder"],
                                relief="flat", highlightthickness=1,
                                highlightbackground=self.controller.styles.colors["border"],
                                highlightcolor=self.controller.styles.colors["primary"],
                                height=4, wrap="word")
        self.desc_entry.pack(fill="x")
        self.desc_entry.insert("1.0", "Add notes about this expense...")
        self.desc_entry.bind("<FocusIn>", lambda e: self.clear_text_placeholder(self.desc_entry, "Add notes about this expense..."))
        self.desc_entry.bind("<FocusOut>", lambda e: self.add_text_placeholder(self.desc_entry, "Add notes about this expense..."))
        
        # MODIFIED: Button frame with "Add" and "Clear" buttons fixed at bottom
        # Create a container frame that will hold the buttons at the bottom
        button_container = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        button_container.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Add a separator line
        separator = tk.Frame(button_container, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x", pady=(0, 15))
        
        button_frame = tk.Frame(button_container, bg=self.styles.colors["white"])
        button_frame.pack(fill="x")
        
        # MODIFIED: Clear button added
        clear_btn = tk.Button(button_frame, text="Clear",
                             font=self.styles.fonts["body"], bg=self.styles.colors["gray"],
                             fg="white", relief="flat", cursor="hand2",
                             command=self.clear_form,
                             padx=35, pady=12)
        clear_btn.pack(side="left", padx=(0, 15))
        
        # MODIFIED: Save button renamed to "Add"
        save_btn = tk.Button(button_frame, text="➕ Add Expense",
                            font=self.styles.fonts["bold"], bg=self.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=self.save_expense,
                            padx=35, pady=12)
        save_btn.pack(side="right")
        
        def on_enter_key(event):
            save_btn.invoke()
        
        self.dialog.bind('<Return>', on_enter_key)
    
    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=self.controller.styles.colors["input_fg"])
    
    def add_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=self.controller.styles.colors["placeholder"])
    
    def clear_text_placeholder(self, text_widget, placeholder):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", tk.END)
            text_widget.config(fg=self.controller.styles.colors["input_fg"])
    
    def add_text_placeholder(self, text_widget, placeholder):
        if not text_widget.get("1.0", "end-1c").strip():
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg=self.controller.styles.colors["placeholder"])
    
    # MODIFIED: New clear form method
    def clear_form(self):
        self.category_menu.set("Shopping")
        
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, "0.00")
        self.amount_entry.config(fg=self.controller.styles.colors["placeholder"])  # FIXED: Use brackets []
        
        self.date_entry.set_date(datetime.now())
        
        self.payment_menu.set("Credit Card")
        
        self.desc_entry.delete("1.0", tk.END)
        self.desc_entry.insert("1.0", "Add notes about this expense...")
        self.desc_entry.config(fg=self.controller.styles.colors["placeholder"])
    
    def save_expense(self):
        category = self.category_var.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get_date()
        payment_method = self.payment_var.get()
        description = self.desc_entry.get("1.0", "end").strip()
        
        if amount == "0.00":
            messagebox.showerror("Error", "Please enter a valid amount")
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            self.controller.save_expense(category, amount_float, date, payment_method, description)
        else:
            messagebox.showerror("Error", "No wallet selected")
        
        self.dialog.destroy()

class AddWalletDialog:
    def __init__(self, parent, controller):
        self.controller = controller
        self.styles = controller.styles
        
        # MODIFIED: Larger size matching requirements (same as income/expense)
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Wallet")
        self.dialog.geometry("550x680")  # Increased from 500x400
        self.dialog.configure(bg=self.styles.colors["white"])
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # MODIFIED: Use ScrollableFrame for scrollable content
        self.scrollable_container = ScrollableFrame(self.dialog, bg=self.styles.colors["white"])
        self.scrollable_container.pack(fill="both", expand=True)
        
        self.main_container = tk.Frame(self.scrollable_container.scrollable_frame, bg=self.styles.colors["white"], padx=40, pady=40)
        self.main_container.pack(fill="both", expand=True)
        
        self.create_form()
    
    def create_form(self):
        header_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(header_frame, text="Create New Wallet", 
                font=self.styles.fonts["h2"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        # Description box
        desc_frame = tk.Frame(header_frame, bg="#e1f5fe", padx=15, pady=10)
        desc_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(desc_frame, text="💡 Create separate wallets for different purposes (e.g., Personal, Business, Savings).",
                font=self.styles.fonts["body"], bg="#e1f5fe", fg="#01579b", wraplength=450).pack(anchor="w")
        
        wallet_info = ""
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_info = f" for {self.controller.current_wallet['name']} ({currency_symbol})"
        
        tk.Label(header_frame, text="Add a new wallet to track finances separately",
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(10, 0))
        
        form_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        # Wallet Name
        name_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        name_frame.pack(fill="x", pady=(0, 20))
        
        name_label_frame = tk.Frame(name_frame, bg=self.styles.colors["white"])
        name_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(name_label_frame, text="Wallet Name *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(name_label_frame, text="ⓘ e.g., Personal, Business, Savings",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        # MODIFIED: Entry styling to match amount textbox
        self.name_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                                  bg=self.controller.styles.colors["input_bg"], 
                                  fg=self.controller.styles.colors["placeholder"],
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=self.controller.styles.colors["border"],
                                  highlightcolor=self.controller.styles.colors["primary"])
        self.name_entry.pack(fill="x")
        self.name_entry.insert(0, "e.g., Personal, Business, Savings")
        self.name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.name_entry, "e.g., Personal, Business, Savings"))
        self.name_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.name_entry, "e.g., Personal, Business, Savings"))
        self.name_entry.focus_set()
        
        # Currency
        currency_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        currency_frame.pack(fill="x", pady=(0, 30))
        
        currency_label_frame = tk.Frame(currency_frame, bg=self.styles.colors["white"])
        currency_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(currency_label_frame, text="Currency *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(currency_label_frame, text="ⓘ Select currency for this wallet",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        self.currency_var = tk.StringVar(value="USD")
        
        # MODIFIED: Currency combobox with same styling
        self.currency_menu = ttk.Combobox(form_frame, textvariable=self.currency_var,
                                         values=["USD", "NTD", "IDR", "EUR", "GBP", "JPY", "CAD", "AUD"],
                                         state="readonly",
                                         font=self.controller.styles.fonts["body"])
        self.currency_menu.pack(fill="x")
        
        # MODIFIED: Button frame with "Add" and "Clear" buttons fixed at bottom
        # Create a container frame that will hold the buttons at the bottom
        button_container = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        button_container.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Add a separator line
        separator = tk.Frame(button_container, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x", pady=(0, 15))
        
        button_frame = tk.Frame(button_container, bg=self.styles.colors["white"])
        button_frame.pack(fill="x")
        
        # MODIFIED: Clear button added
        clear_btn = tk.Button(button_frame, text="Clear",
                             font=self.styles.fonts["body"], bg=self.styles.colors["gray"],
                             fg="white", relief="flat", cursor="hand2",
                             command=self.clear_form,
                             padx=35, pady=12)
        clear_btn.pack(side="left", padx=(0, 15))
        
        # MODIFIED: Save button renamed to "Add"
        create_btn = tk.Button(button_frame, text="➕ Create Wallet",
                            font=self.styles.fonts["bold"], bg=self.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=self.create_wallet,
                            padx=35, pady=12)
        create_btn.pack(side="right")
        
        def on_enter_key(event):
            create_btn.invoke()
        
        self.dialog.bind('<Return>', on_enter_key)
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=self.controller.styles.colors["input_fg"])
    
    def add_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=self.controller.styles.colors["placeholder"])
    
    # MODIFIED: New clear form method
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, "e.g., Personal, Business, Savings")
        self.name_entry.config(fg=self.controller.styles.colors["placeholder"])  # FIXED: Use brackets []
        
        self.currency_menu.set("USD")
    
    def create_wallet(self):
        name = self.name_entry.get().strip()
        currency = self.currency_var.get()
        
        if name == "e.g., Personal, Business, Savings" or not name:
            messagebox.showerror("Error", "Please enter a wallet name")
            return
        
        self.controller.create_wallet(name, currency)
        self.dialog.destroy()

class AddBudgetDialog:
    def __init__(self, parent, controller):
        self.controller = controller
        self.styles = controller.styles
        
        # MODIFIED: Larger size matching requirements
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Budget")
        self.dialog.geometry("550x680")  # Increased from 450x320
        self.dialog.configure(bg=self.styles.colors["white"])
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # MODIFIED: Use ScrollableFrame for scrollable content
        self.scrollable_container = ScrollableFrame(self.dialog, bg=self.styles.colors["white"])
        self.scrollable_container.pack(fill="both", expand=True)
        
        self.main_container = tk.Frame(self.scrollable_container.scrollable_frame, bg=self.styles.colors["white"], padx=40, pady=30)
        self.main_container.pack(fill="both", expand=True)
        
        self.create_form()
    
    def create_form(self):
        header_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(header_frame, text="Create New Budget", 
                font=self.styles.fonts["h2"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        # Description box
        desc_frame = tk.Frame(header_frame, bg="#fff3e0", padx=15, pady=10)
        desc_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(desc_frame, text="💡 Set a monthly spending limit to track your expenses automatically.",
                font=self.styles.fonts["body"], bg="#fff3e0", fg="#e65100", wraplength=450).pack(anchor="w")
        
        wallet_info = ""
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_info = f" for {self.controller.current_wallet['name']} ({currency_symbol})"
        
        tk.Label(header_frame, text=f"Set overall budget{wallet_info}",
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(10, 0))
        
        form_frame = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        # Amount info
        amount_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        amount_frame.pack(fill="x", pady=(0, 25))
        
        amount_label_frame = tk.Frame(amount_frame, bg=self.styles.colors["white"])
        amount_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(amount_label_frame, text="Budget Amount *", 
                font=self.styles.fonts["bold"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(amount_label_frame, text="ⓘ Monthly spending limit",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.controller.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        # MODIFIED: Entry styling to match amount textbox
        self.amount_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                                    bg=self.controller.styles.colors["input_bg"], 
                                    fg=self.controller.styles.colors["placeholder"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=self.controller.styles.colors["border"],
                                    highlightcolor=self.controller.styles.colors["primary"])
        self.amount_entry.pack(fill="x")
        self.amount_entry.insert(0, "1000.00")
        self.amount_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.amount_entry, "1000.00"))
        self.amount_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.amount_entry, "1000.00"))
        self.amount_entry.focus_set()
        
        # Fixed category and period info
        info_label = tk.Label(form_frame, text="Category: Overall • Period: Monthly",
                font=self.controller.styles.fonts["body"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text_secondary"])
        info_label.pack(anchor="w", pady=(10, 0))
        
        # Explanation label
        tk.Label(form_frame, text="This budget tracks all expenses in your wallet.",
                font=self.controller.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.controller.styles.colors["text_secondary"]).pack(anchor="w", pady=(5, 0))
        
        # MODIFIED: Button frame with "Add" and "Clear" buttons fixed at bottom
        # Create a container frame that will hold the buttons at the bottom
        button_container = tk.Frame(self.main_container, bg=self.styles.colors["white"])
        button_container.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Add a separator line
        separator = tk.Frame(button_container, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x", pady=(0, 15))
        
        button_frame = tk.Frame(button_container, bg=self.styles.colors["white"])
        button_frame.pack(fill="x")
        
        # MODIFIED: Clear button added
        clear_btn = tk.Button(button_frame, text="Clear",
                             font=self.styles.fonts["body"], bg=self.styles.colors["gray"],
                             fg="white", relief="flat", cursor="hand2",
                             command=self.clear_form,
                             padx=35, pady=12)
        clear_btn.pack(side="left", padx=(0, 15))
        
        # MODIFIED: Save button renamed to "Add"
        create_btn = tk.Button(button_frame, text="➕ Create Budget",
                            font=self.styles.fonts["bold"], bg=self.controller.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=self.create_budget,
                            padx=35, pady=12)
        create_btn.pack(side="right")
        
        def on_enter_key(event):
            create_btn.invoke()
        
        self.dialog.bind('<Return>', on_enter_key)
    
    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=self.controller.styles.colors["input_fg"])
    
    def add_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=self.controller.styles.colors["placeholder"])
    
    # MODIFIED: New clear form method
    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, "1000.00")
        self.amount_entry.config(fg=self.controller.styles.colors["placeholder"])  # FIXED: Use brackets []
    
    def create_budget(self):
        amount = self.amount_entry.get()
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            self.controller.create_budget(amount_float, 'Overall', 'monthly')
        else:
            messagebox.showerror("Error", "No wallet selected")
        
        self.dialog.destroy()