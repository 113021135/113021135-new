import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from datetime import datetime
import pandas as pd
import os

# Import frontend modules
from frontend.pages import (DashboardPage, IncomePage, ExpensesPage, 
                           ReportsPage, AllTransactionsPage, WalletsPage, BudgetsPage)
from frontend.dialogs import (AddIncomeDialog, AddExpenseDialog, 
                             AddWalletDialog, AddBudgetDialog)
from frontend.components import Styles
from backend.database import Database

class ExpenseTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Expense Tracker Pro")
        self.root.geometry("1500x950")
        self.root.configure(bg="#f8fafc")
        
        self.db = Database()
        self.styles = Styles(theme='light')
        
        self.current_user = None
        self.current_wallet = None
        self.current_page = None
        
        self.currency_symbols = {
            'USD': '$',
            'NTD': 'NT$',
            'IDR': 'Rp',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CAD': 'C$',
            'AUD': 'A$'
        }
        
        self.show_splash()
    
    def show_splash(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        splash_frame = tk.Frame(self.root, bg=self.styles.colors["primary"])
        splash_frame.pack(fill="both", expand=True)
        
        tk.Label(splash_frame, text="💰", font=("Arial", 120), 
                bg=self.styles.colors["primary"], fg="white").pack(pady=60)
        
        tk.Label(splash_frame, text="Expense Tracker Pro", font=("Segoe UI", 36, "bold"),
                bg=self.styles.colors["primary"], fg="white").pack(pady=25)
        
        tk.Label(splash_frame, text="Professional Multi-Wallet Financial Management", 
                font=("Segoe UI", 16), bg=self.styles.colors["primary"], 
                fg="white", pady=15).pack()
        
        # Enhanced feature list with enhanced spacing
        features_frame = tk.Frame(splash_frame, bg=self.styles.colors["primary"])
        features_frame.pack(pady=30)
        
        features = [
            "✓ Multi-Wallet & Multi-Currency Support",
            "✓ Smart Budget Tracking with Visual Progress",
            "✓ Professional Charts & Reports",
            "✓ One-Click Excel Export",
            "✓ Dark/Light Theme Toggle",
            "✓ Detailed Transaction History"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, font=("Segoe UI", 14),
                    bg=self.styles.colors["primary"], fg="white", 
                    anchor="w").pack(fill="x", pady=8)
        
        progress = ttk.Progressbar(splash_frame, mode='indeterminate', length=350, style='TProgressbar')
        progress.pack(pady=40)
        progress.start(10)
        
        self.root.after(2000, self.show_login)
    
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_container = tk.Frame(self.root, bg=self.styles.colors["white"])
        main_container.pack(fill="both", expand=True)
        
        # Left panel
        left_panel = tk.Frame(main_container, bg=self.styles.colors["primary"])
        left_panel.pack(side="left", fill="both", expand=True)
        
        info_frame = tk.Frame(left_panel, bg=self.styles.colors["primary"])
        info_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(info_frame, text="💰", font=("Arial", 80),
                bg=self.styles.colors["primary"], fg="white").pack()
        
        tk.Label(info_frame, text="Expense Tracker Pro", font=("Segoe UI", 32, "bold"),
                bg=self.styles.colors["primary"], fg="white").pack(pady=25)
        
        tk.Label(info_frame, text="Join thousands managing their finances", 
                font=self.styles.fonts["body"], bg=self.styles.colors["primary"],
                fg="white").pack()
        
        # Enhanced feature list
        features_frame = tk.Frame(info_frame, bg=self.styles.colors["primary"])
        features_frame.pack(pady=20)
        
        features = [
            "✓ Track Income & Expenses Across Multiple Wallets",
            "✓ Visual Budget Progress Bars & Spending Alerts",
            "✓ Professional Financial Reports & Charts",
            "✓ Export Data to Excel with One Click",
            "✓ Beautiful Dark & Light Themes",
            "✓ Secure & Easy-to-Use Interface"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, font=("Segoe UI", 13),
                    bg=self.styles.colors["primary"], fg="white", 
                    anchor="w").pack(fill="x")
        
        # Right panel
        right_panel = tk.Frame(main_container, bg=self.styles.colors["white"])
        right_panel.pack(side="right", fill="both", expand=True, padx=100)
        
        form_frame = tk.Frame(right_panel, bg=self.styles.colors["white"])
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        title_frame.pack(fill="x", pady=(0, 30))
        
        tk.Label(title_frame, text="Welcome Back", font=self.styles.fonts["h2"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(anchor="w")
        
        tk.Label(title_frame, text="Sign in to manage your finances", 
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(8, 0))
        
        # Email field
        email_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        email_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(email_frame, text="Email Address", font=self.styles.fonts["bold"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(anchor="w")
        
        self.login_email = tk.Entry(email_frame, font=self.styles.fonts["body"],
                                   bg=self.styles.colors["light"], relief="flat",
                                   highlightthickness=1, 
                                   highlightbackground=self.styles.colors["gray_light"],
                                   highlightcolor=self.styles.colors["primary"],
                                   width=40)
        self.login_email.pack(fill="x", pady=(8, 0))
        self.login_email.insert(0, "demo@example.com")
        
        # Password field with show/hide toggle
        password_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        password_frame.pack(fill="x", pady=(0, 25))
        
        password_header = tk.Frame(password_frame, bg=self.styles.colors["white"])
        password_header.pack(fill="x", pady=(0, 8))
        
        tk.Label(password_header, text="Password", font=self.styles.fonts["bold"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(side="left")
        
        self.show_password_var = tk.BooleanVar(value=False)
        show_password_check = tk.Checkbutton(password_header, text="Show Password",
                                           variable=self.show_password_var,
                                           font=self.styles.fonts["small"],
                                           bg=self.styles.colors["white"],
                                           fg=self.styles.colors["gray"],
                                           command=self.toggle_password_visibility,
                                           cursor="hand2")
        show_password_check.pack(side="right")
        
        self.login_password = tk.Entry(password_frame, font=self.styles.fonts["body"],
                                      show="•", bg=self.styles.colors["light"], 
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=self.styles.colors["gray_light"],
                                      highlightcolor=self.styles.colors["primary"],
                                      width=40)
        self.login_password.pack(fill="x", pady=(8, 0))
        self.login_password.insert(0, "password123")
        
        # Bind Enter key
        self.login_password.bind('<Return>', lambda event: self.authenticate())
        
        # Login button
        login_btn = tk.Button(form_frame, text="LOGIN", 
                             font=("Segoe UI", 14, "bold"),
                             bg=self.styles.colors["primary"], fg="white",
                             relief="flat", cursor="hand2",
                             command=self.authenticate,
                             width=32, height=2)
        login_btn.pack(pady=30)
        
        # Demo button
        demo_btn = tk.Button(form_frame, text="🚀 Try Demo Account", 
                            font=self.styles.fonts["body"], bg=self.styles.colors["bg"],
                            fg=self.styles.colors["primary"], relief="flat",
                            cursor="hand2", command=self.demo_login,
                            padx=20, pady=10)
        demo_btn.pack(pady=10)
        
        # Signup link
        link_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        link_frame.pack(pady=20)
        
        tk.Label(link_frame, text="Don't have an account? ", 
                font=self.styles.fonts["body"], bg=self.styles.colors["white"], 
                fg=self.styles.colors["gray"]).pack(side="left")
        
        signup_link = tk.Label(link_frame, text="Sign Up", 
                              font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                              fg=self.styles.colors["primary"], cursor="hand2")
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.show_signup())
    
    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.login_password.config(show="")
        else:
            self.login_password.config(show="•")
    
    def show_signup(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_container = tk.Frame(self.root, bg=self.styles.colors["white"])
        main_container.pack(fill="both", expand=True)
        
        left_panel = tk.Frame(main_container, bg=self.styles.colors["primary_light"])
        left_panel.pack(side="left", fill="both", expand=True)
        
        info_frame = tk.Frame(left_panel, bg=self.styles.colors["primary_light"])
        info_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(info_frame, text="📝", font=("Arial", 80),
                bg=self.styles.colors["primary_light"], fg="white").pack()
        
        tk.Label(info_frame, text="Create Account", font=("Segoe UI", 32, "bold"),
                bg=self.styles.colors["primary_light"], fg="white").pack(pady=25)
        
        tk.Label(info_frame, text="Join thousands managing their finances", 
                font=self.styles.fonts["body"], bg=self.styles.colors["primary_light"],
                fg="white").pack()
        
        right_panel = tk.Frame(main_container, bg=self.styles.colors["white"])
        right_panel.pack(side="right", fill="both", expand=True, padx=100)
        
        form_frame = tk.Frame(right_panel, bg=self.styles.colors["white"])
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(form_frame, text="Create an Account", font=self.styles.fonts["h2"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(anchor="w")
        
        tk.Label(form_frame, text="Enter your details to get started", 
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(8, 30))
        
        # Full Name
        name_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        name_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(name_frame, text="Full Name", font=self.styles.fonts["bold"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(anchor="w")
        
        self.signup_name = tk.Entry(name_frame, font=self.styles.fonts["body"],
                                   bg=self.styles.colors["light"], relief="flat",
                                   highlightthickness=1,
                                   highlightbackground=self.styles.colors["gray_light"],
                                   highlightcolor=self.styles.colors["primary"],
                                   width=40)
        self.signup_name.pack(fill="x", pady=(8, 0))
        
        # Email
        email_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        email_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(email_frame, text="Email Address", font=self.styles.fonts["bold"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(anchor="w")
        
        self.signup_email = tk.Entry(email_frame, font=self.styles.fonts["body"],
                                    bg=self.styles.colors["light"], relief="flat",
                                    highlightthickness=1,
                                    highlightbackground=self.styles.colors["gray_light"],
                                    highlightcolor=self.styles.colors["primary"],
                                    width=40)
        self.signup_email.pack(fill="x", pady=(8, 0))
        
        # Password field with show/hide toggle
        password_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        password_frame.pack(fill="x", pady=(0, 25))
        
        password_header = tk.Frame(password_frame, bg=self.styles.colors["white"])
        password_header.pack(fill="x", pady=(0, 8))
        
        tk.Label(password_header, text="Password", font=self.styles.fonts["bold"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(side="left")
        
        self.signup_show_password_var = tk.BooleanVar(value=False)
        signup_show_password_check = tk.Checkbutton(password_header, text="Show Password",
                                                  variable=self.signup_show_password_var,
                                                  font=self.styles.fonts["small"],
                                                  bg=self.styles.colors["white"],
                                                  fg=self.styles.colors["gray"],
                                                  command=self.toggle_signup_password_visibility,
                                                  cursor="hand2")
        signup_show_password_check.pack(side="right")
        
        self.signup_password = tk.Entry(password_frame, font=self.styles.fonts["body"],
                                       show="•", bg=self.styles.colors["light"],
                                       relief="flat", highlightthickness=1,
                                       highlightbackground=self.styles.colors["gray_light"],
                                       highlightcolor=self.styles.colors["primary"],
                                       width=40)
        self.signup_password.pack(fill="x", pady=(8, 0))
        
        # Confirm Password
        confirm_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        confirm_frame.pack(fill="x", pady=(0, 25))
        
        confirm_header = tk.Frame(confirm_frame, bg=self.styles.colors["white"])
        confirm_header.pack(fill="x", pady=(0, 8))
        
        tk.Label(confirm_header, text="Confirm Password", font=self.styles.fonts["bold"],
                bg=self.styles.colors["white"], fg=self.styles.colors["dark"]).pack(side="left")
        
        self.signup_show_confirm_var = tk.BooleanVar(value=False)
        signup_show_confirm_check = tk.Checkbutton(confirm_header, text="Show Password",
                                                 variable=self.signup_show_confirm_var,
                                                 font=self.styles.fonts["small"],
                                                 bg=self.styles.colors["white"],
                                                 fg=self.styles.colors["gray"],
                                                 command=self.toggle_signup_confirm_visibility,
                                                 cursor="hand2")
        signup_show_confirm_check.pack(side="right")
        
        self.signup_confirm = tk.Entry(confirm_frame, font=self.styles.fonts["body"],
                                      show="•", bg=self.styles.colors["light"],
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=self.styles.colors["gray_light"],
                                      highlightcolor=self.styles.colors["primary"],
                                      width=40)
        self.signup_confirm.pack(fill="x", pady=(8, 0))
        
        self.signup_confirm.bind('<Return>', lambda event: self.register_user())
        
        signup_btn = tk.Button(form_frame, text="CREATE ACCOUNT",
                              font=("Segoe UI", 14, "bold"),
                              bg=self.styles.colors["primary"], fg="white",
                              relief="flat", cursor="hand2",
                              command=self.register_user,
                              width=32, height=2)
        signup_btn.pack(pady=30)
        
        link_frame = tk.Frame(form_frame, bg=self.styles.colors["white"])
        link_frame.pack()
        
        tk.Label(link_frame, text="Already have an account? ",
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["gray"]).pack(side="left")
        
        login_link = tk.Label(link_frame, text="Login",
                             font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                             fg=self.styles.colors["primary"], cursor="hand2")
        login_link.pack(side="left")
        login_link.bind("<Button-1>", lambda e: self.show_login())
    
    def toggle_signup_password_visibility(self):
        if self.signup_show_password_var.get():
            self.signup_password.config(show="")
        else:
            self.signup_password.config(show="•")
    
    def toggle_signup_confirm_visibility(self):
        if self.signup_show_confirm_var.get():
            self.signup_confirm.config(show="")
        else:
            self.signup_confirm.config(show="•")
    
    def authenticate(self):
        email = self.login_email.get()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password")
            return
        
        user = self.db.authenticate_user(email, password)
        if user:
            self.current_user = user
            self.styles = Styles(theme=user.get("theme", "light"))
            
            wallets = self.db.get_wallets(user["id"])
            if wallets:
                for wallet in wallets:
                    if wallet["is_default"]:
                        self.current_wallet = wallet
                        break
                if not self.current_wallet:
                    self.current_wallet = wallets[0]
            
            messagebox.showinfo("Success", f"Welcome back, {user['full_name']}!")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid email or password")
    
    def demo_login(self):
        user = self.db.get_demo_user()
        if user:
            self.current_user = user
            self.styles = Styles(theme=user.get("theme", "light"))
            
            wallets = self.db.get_wallets(user["id"])
            if wallets:
                self.current_wallet = wallets[0]
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Demo account not found")
    
    def register_user(self):
        name = self.signup_name.get()
        email = self.signup_email.get()
        password = self.signup_password.get()
        confirm = self.signup_confirm.get()
        
        if not all([name, email, password, confirm]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        
        success, message = self.db.register_user(name, email, password)
        if success:
            user = self.db.authenticate_user(email, password)
            self.current_user = user
            self.styles = Styles(theme=user.get("theme", "light"))
            
            wallets = self.db.get_wallets(user["id"])
            if wallets:
                self.current_wallet = wallets[0]
            
            messagebox.showinfo("Success", message)
            self.show_dashboard()
        else:
            messagebox.showerror("Error", message)
    
    def show_dashboard(self):
        self.current_page = DashboardPage(self.root, self)
        self.current_page.show()
    
    def show_income(self):
        self.current_page = IncomePage(self.root, self)
        self.current_page.show()
    
    def show_expenses(self):
        self.current_page = ExpensesPage(self.root, self)
        self.current_page.show()
    
    def show_reports(self):
        self.current_page = ReportsPage(self.root, self)
        # Initialize the available years
        if self.current_wallet:
            self.current_page.available_years = self.db.get_available_years(
                self.current_user["id"],
                self.current_wallet["id"]
            )
            if not self.current_page.available_years:
                self.current_page.available_years = [str(datetime.now().year)]
            self.current_page.current_year = int(self.current_page.available_years[0])
        self.current_page.show()
    
    def show_wallets(self):
        self.current_page = WalletsPage(self.root, self)
        self.current_page.show()
    
    def show_budgets(self):
        self.current_page = BudgetsPage(self.root, self)
        self.current_page.show()
    
    def show_all_transactions(self):
        self.current_page = AllTransactionsPage(self.root, self)
        self.current_page.show()
    
    def show_add_income_dialog(self):
        if not self.current_wallet:
            messagebox.showerror("Error", "Please select a wallet first")
            return
        dialog = AddIncomeDialog(self.root, self)
    
    def show_add_expense_dialog(self):
        if not self.current_wallet:
            messagebox.showerror("Error", "Please select a wallet first")
            return
        dialog = AddExpenseDialog(self.root, self)
    
    def show_add_wallet_dialog(self):
        dialog = AddWalletDialog(self.root, self)
    
    def show_add_budget_dialog(self):
        if not self.current_wallet:
            messagebox.showerror("Error", "Please select a wallet first")
            return
        dialog = AddBudgetDialog(self.root, self)
    
    def create_wallet(self, name, currency):
        if not name:
            messagebox.showerror("Error", "Wallet name cannot be empty")
            return
        
        wallet_id = self.db.create_wallet(self.current_user["id"], name, currency)
        if wallet_id:
            wallet = self.db.get_wallet(wallet_id)
            self.current_wallet = wallet
            
            messagebox.showinfo("Success", f"Wallet '{name}' created successfully!")
            
            if self.current_page:
                if hasattr(self.current_page, 'show'):
                    self.current_page.show()
        else:
            messagebox.showerror("Error", "Failed to create wallet")
    
    def create_budget(self, amount, category='Overall', period='monthly'):
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        budget_id = self.db.create_budget(self.current_user["id"], self.current_wallet["id"], amount_float, category, period)
        if budget_id:
            messagebox.showinfo("Success", f"Overall monthly budget created successfully!")
            
            if isinstance(self.current_page, BudgetsPage):
                self.current_page.show()
            else:
                self.show_budgets()
        else:
            messagebox.showerror("Error", "Failed to create budget")
    
    def switch_wallet(self, wallet_id):
        wallet = self.db.get_wallet(wallet_id)
        if wallet and wallet["user_id"] == self.current_user["id"]:
            self.current_wallet = wallet
            if self.current_page:
                if hasattr(self.current_page, 'show'):
                    self.current_page.show()
        else:
            messagebox.showerror("Error", "Wallet not found")
    
    def set_default_wallet(self, wallet_id):
        success = self.db.set_default_wallet(self.current_user["id"], wallet_id)
        if success:
            if self.current_wallet and self.current_wallet["id"] == wallet_id:
                self.current_wallet["is_default"] = True
            
            if isinstance(self.current_page, WalletsPage):
                self.current_page.show()
            messagebox.showinfo("Success", "Default wallet updated!")
        else:
            messagebox.showerror("Error", "Failed to set default wallet")
    
    def toggle_theme(self):
        new_theme = self.styles.toggle_theme()
        
        if self.current_user:
            self.db.update_user_theme(self.current_user["id"], new_theme)
        
        if self.current_page:
            if hasattr(self.current_page, 'show'):
                self.current_page.show()
    
    def save_income(self, source, amount, category, date, description):
        source = str(source).strip()
        category = str(category).strip() if category else "Uncategorized"
        description = str(description).strip()
        
        if not source:
            messagebox.showerror("Error", "Income source cannot be empty")
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        if not self.current_wallet:
            messagebox.showerror("Error", "No wallet selected")
            return
        
        try:
            income_id, new_balance = self.db.save_income(
                self.current_user["id"],
                self.current_wallet["id"],
                source,
                amount_float,
                category,
                date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
                description
            )
            
            self.current_wallet["balance"] = new_balance
            
            messagebox.showinfo("Success", "Income added successfully!")
            self.show_income()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save income: {str(e)}")
    
    def save_expense(self, category, amount, date, payment_method, description):
        category = str(category).strip() if category else "Other"
        payment_method = str(payment_method).strip() if payment_method else "Unknown"
        description = str(description).strip()
        
        if not category:
            messagebox.showerror("Error", "Category cannot be empty")
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        if not self.current_wallet:
            messagebox.showerror("Error", "No wallet selected")
            return
        
        try:
            expense_id, new_balance = self.db.save_expense(
                self.current_user["id"],
                self.current_wallet["id"],
                category,
                amount_float,
                date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
                description,
                payment_method
            )
            
            self.current_wallet["balance"] = new_balance
            
            messagebox.showinfo("Success", "Expense added successfully!")
            self.show_expenses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {str(e)}")
    
    def delete_income(self, income_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this income?"):
            success = self.db.delete_income(income_id, self.current_user["id"])
            if success:
                new_balance = self.db.update_wallet_balance(self.current_wallet["id"])
                self.current_wallet["balance"] = new_balance
                
                messagebox.showinfo("Success", "Income deleted successfully!")
                self.show_income()
            else:
                messagebox.showerror("Error", "Failed to delete income")
    
    def delete_expense(self, expense_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            success = self.db.delete_expense(expense_id, self.current_user["id"])
            if success:
                new_balance = self.db.update_wallet_balance(self.current_wallet["id"])
                self.current_wallet["balance"] = new_balance
                
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.show_expenses()
            else:
                messagebox.showerror("Error", "Failed to delete expense")
    
    def format_date_for_display(self, date_str):
        if not date_str:
            return "N/A"
        
        try:
            date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(str(date_str), fmt)
                    return date_obj.strftime('%d %b %Y')
                except:
                    continue
            return str(date_str)[:10]
        except:
            return str(date_str)[:10] if date_str else "N/A"
    
    def get_currency_symbol(self, currency=None):
        if currency is None:
            if self.current_wallet:
                currency = self.current_wallet["currency"]
            else:
                return "$"
        return self.currency_symbols.get(currency, currency)
    
    def format_currency(self, amount, currency=None):
        if currency is None:
            if self.current_wallet:
                currency = self.current_wallet["currency"]
            else:
                currency = "USD"
        currency_symbol = self.get_currency_symbol(currency)
        return f"{currency_symbol}{amount:,.2f}"
    
    def get_yearly_income(self):
        if not self.current_wallet:
            return 0.0
        
        cursor = self.db.conn.cursor()
        current_year = datetime.now().strftime('%Y')
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM income 
            WHERE user_id = ? AND wallet_id = ? AND strftime('%Y', date) = ?
        ''', (self.current_user["id"], self.current_wallet["id"], current_year))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def get_average_income(self):
        if not self.current_wallet:
            return 0.0
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(AVG(monthly_total), 0) FROM (
                SELECT strftime('%Y-%m', date) as month, SUM(amount) as monthly_total
                FROM income 
                WHERE user_id = ? AND wallet_id = ?
                GROUP BY strftime('%Y-%m', date)
            )
        ''', (self.current_user["id"], self.current_wallet["id"]))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def get_yearly_expense(self):
        if not self.current_wallet:
            return 0.0
        
        cursor = self.db.conn.cursor()
        current_year = datetime.now().strftime('%Y')
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM expenses 
            WHERE user_id = ? AND wallet_id = ? AND strftime('%Y', date) = ?
        ''', (self.current_user["id"], self.current_wallet["id"], current_year))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def get_average_expense(self):
        if not self.current_wallet:
            return 0.0
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(AVG(monthly_total), 0) FROM (
                SELECT strftime('%Y-%m', date) as month, SUM(amount) as monthly_total
                FROM expenses 
                WHERE user_id = ? AND wallet_id = ?
                GROUP BY strftime('%Y-%m', date)
            )
        ''', (self.current_user["id"], self.current_wallet["id"]))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def export_income_to_excel(self):
        if not self.current_wallet:
            messagebox.showerror("Error", "No wallet selected")
            return
        
        incomes = self.db.get_all_income(
            self.current_user["id"],
            self.current_wallet["id"]
        )
        
        if not incomes:
            messagebox.showwarning("Warning", "No income data to export")
            return
        
        df = pd.DataFrame(incomes)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"income_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Income data exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_expenses_to_excel(self):
        if not self.current_wallet:
            messagebox.showerror("Error", "No wallet selected")
            return
        
        expenses = self.db.get_all_expenses(
            self.current_user["id"],
            self.current_wallet["id"]
        )
        
        if not expenses:
            messagebox.showwarning("Warning", "No expense data to export")
            return
        
        df = pd.DataFrame(expenses)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Expense data exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def generate_full_report(self):
        if not self.current_wallet:
            messagebox.showerror("Error", "No wallet selected")
            return
        
        try:
            income_data = self.db.get_all_income(
                self.current_user["id"],
                self.current_wallet["id"]
            )
            expense_data = self.db.get_all_expenses(
                self.current_user["id"],
                self.current_wallet["id"]
            )
            
            if not income_data and not expense_data:
                messagebox.showwarning("Warning", "No financial data to generate report")
                return
            
            wallet_name = self.current_wallet["name"]
            currency_symbol = self.get_currency_symbol(self.current_wallet["currency"])
            
            summary_data = {
                'Metric': ['Total Income', 'Total Expenses', 'Net Savings', 'Wallet Balance'],
                'Amount': [
                    f"{currency_symbol}{self.db.get_total_income(self.current_user['id'], self.current_wallet['id']):,.2f}",
                    f"{currency_symbol}{self.db.get_total_expenses(self.current_user['id'], self.current_wallet['id']):,.2f}",
                    f"{currency_symbol}{self.db.get_total_income(self.current_user['id'], self.current_wallet['id']) - self.db.get_total_expenses(self.current_user['id'], self.current_wallet['id']):,.2f}",
                    f"{currency_symbol}{self.db.get_wallet_balance(self.current_wallet['id']):,.2f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            income_df = pd.DataFrame(income_data) if income_data else pd.DataFrame()
            expense_df = pd.DataFrame(expense_data) if expense_data else pd.DataFrame()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"{wallet_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    if not income_df.empty:
                        income_df.to_excel(writer, sheet_name='Income', index=False)
                    if not expense_df.empty:
                        expense_df.to_excel(writer, sheet_name='Expenses', index=False)
                
                messagebox.showinfo("Success", f"Financial report generated:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def logout(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.current_user = None
            self.current_wallet = None
            self.current_page = None
            self.show_login()
    
    def run(self):
        self.root.mainloop()

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        import matplotlib
        import pandas
        from tkcalendar import DateEntry
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install matplotlib pandas tkcalendar openpyxl")
        exit(1)
    
    app = ExpenseTracker()
    app.run()