import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import components and backend
from .components import (Styles, ModernButton, ScrollableFrame, DatePicker, 
                        BudgetProgressBar, FinancialChart, DataTable, Dialog)
from backend.database import Database

class BasePage:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.styles = controller.styles
        
    def create_sidebar(self):
        sidebar = tk.Frame(self.parent, bg=self.styles.colors["sidebar"], width=300)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # User info
        user_frame = tk.Frame(sidebar, bg=self.styles.colors["sidebar"])
        user_frame.pack(fill="x", pady=(30, 25), padx=20)
        
        profile_circle = tk.Canvas(user_frame, width=65, height=65, 
                                  bg=self.styles.colors["sidebar"], highlightthickness=0)
        profile_circle.create_oval(5, 5, 60, 60, fill=self.styles.colors["primary"], outline="")
        initials = "".join([name[0] for name in self.controller.current_user["full_name"].split()[:2]]).upper()
        profile_circle.create_text(32.5, 32.5, text=initials, fill="white", 
                                  font=("Segoe UI", 18, "bold"))
        profile_circle.pack()
        
        tk.Label(user_frame, text=self.controller.current_user["full_name"],
                font=self.styles.fonts["h3"], bg=self.styles.colors["sidebar"],
                fg="white").pack(pady=(12, 5))
        
        tk.Label(user_frame, text=self.controller.current_user["email"],
                font=self.styles.fonts["small"], bg=self.styles.colors["sidebar"],
                fg=self.styles.colors["gray_light"]).pack()
        
        # Current wallet info
        wallet_frame = tk.Frame(user_frame, bg=self.styles.colors["sidebar"])
        wallet_frame.pack(pady=(15, 0))
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_text = f"{self.controller.current_wallet['name']} ({currency_symbol})"
            tk.Label(wallet_frame, text="Current Wallet:",
                    font=self.styles.fonts["small"], bg=self.styles.colors["sidebar"],
                    fg=self.styles.colors["gray_light"]).pack(anchor="w")
            tk.Label(wallet_frame, text=wallet_text,
                    font=self.styles.fonts["bold"], bg=self.styles.colors["sidebar"],
                    fg="white").pack(anchor="w")
        
        # Navigation
        nav_frame = tk.Frame(sidebar, bg=self.styles.colors["sidebar"])
        nav_frame.pack(fill="x", padx=20, pady=25)
        
        nav_items = [
            ("Dashboard", self.controller.show_dashboard),
            ("Income", self.controller.show_income),
            ("Expenses", self.controller.show_expenses),
            ("Reports", self.controller.show_reports),
            ("Wallets", self.controller.show_wallets),
            ("Budgets", self.controller.show_budgets),
            ("Logout", self.controller.logout)
        ]
        
        for item_text, command in nav_items:
            item_frame = tk.Frame(nav_frame, bg=self.styles.colors["sidebar"])
            item_frame.pack(fill="x", pady=6)
            
            item_btn = tk.Button(item_frame, text=f"  {item_text}",
                                font=self.styles.fonts["body"], anchor="w",
                                bg=self.styles.colors["sidebar"], fg="white",
                                relief="flat", cursor="hand2",
                                command=command,
                                padx=20, pady=14)
            item_btn.pack(fill="x")
            
            item_btn.bind("<Enter>", 
                         lambda e, b=item_btn: b.config(bg="#334155"))
            item_btn.bind("<Leave>", 
                         lambda e, b=item_btn: b.config(bg=self.styles.colors["sidebar"]))
        
        # Theme toggle button at the bottom of sidebar
        theme_frame = tk.Frame(sidebar, bg=self.styles.colors["sidebar"], pady=20)
        theme_frame.pack(side="bottom", fill="x", padx=20)
        
        theme_icon = "🌙" if self.styles.theme == 'light' else "☀️"
        theme_text = "Dark Mode" if self.styles.theme == 'light' else "Light Mode"
        
        theme_btn = tk.Button(theme_frame, text=f"  {theme_icon} {theme_text}",
                             font=self.styles.fonts["body"], anchor="w",
                             bg=self.styles.colors["sidebar"], fg="white",
                             relief="flat", cursor="hand2",
                             command=self.controller.toggle_theme,
                             padx=20, pady=12)
        theme_btn.pack(fill="x")
        
        theme_btn.bind("<Enter>", 
                      lambda e, b=theme_btn: b.config(bg="#334155"))
        theme_btn.bind("<Leave>", 
                      lambda e, b=theme_btn: b.config(bg=self.styles.colors["sidebar"]))
        
        return sidebar

class DashboardPage(BasePage):
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # Header
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="Dashboard", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            wallet_text = f"{self.controller.current_wallet['name']} ({self.controller.get_currency_symbol(self.controller.current_wallet['currency'])})"
            wallet_label = tk.Label(left_header, text=f" | {wallet_text}",
                                  font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                                  fg=self.styles.colors["primary"])
            wallet_label.pack(side="left", padx=(20, 0))
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        date_label = tk.Label(right_header, 
                             text=datetime.now().strftime("%d %B, %Y"),
                             font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                             fg=self.styles.colors["text_secondary"])
        date_label.pack(side="right")
        
        # Info banner
        info_banner = tk.Frame(content_frame, bg="#e3f2fd", padx=20, pady=15)
        info_banner.pack(fill="x", padx=30, pady=(0, 20))
        
        tk.Label(info_banner, text="💡 Tip: This dashboard shows your current wallet's financial overview. Switch wallets to see different data.",
                font=self.styles.fonts["body"], bg="#e3f2fd", fg="#1976d2").pack(anchor="w")
        
        # Current Wallet card section
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            wallets_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
            wallets_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            tk.Label(wallets_frame, text="Current Wallet", 
                    font=self.styles.fonts["h3"], bg=self.styles.colors["bg"],
                    fg=self.styles.colors["text"]).pack(anchor="w", pady=(0, 15))
            
            wallet_card = self.create_wallet_card(wallets_frame, self.controller.current_wallet)
            wallet_card.pack(fill="x", pady=(0, 10))
        
        # Summary Cards for current wallet
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            summary_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
            summary_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            wallet_id = self.controller.current_wallet["id"]
            total_income = self.controller.db.get_total_income(self.controller.current_user["id"], wallet_id)
            total_expenses = self.controller.db.get_total_expenses(self.controller.current_user["id"], wallet_id)
            total_balance = self.controller.db.get_wallet_balance(wallet_id)
            
            # Add tooltip explanation
            summary_data = [
                ("Wallet Balance", self.controller.format_currency(total_balance, self.controller.current_wallet["currency"]), 
                 self.styles.colors["primary"], "💰", "Current available funds in this wallet"),
                ("Total Income", self.controller.format_currency(total_income, self.controller.current_wallet["currency"]), 
                 "#10b981", "📈", "Sum of all income recorded in this wallet"),
                ("Total Expenses", self.controller.format_currency(total_expenses, self.controller.current_wallet["currency"]), 
                 "#ef4444", "📉", "Sum of all expenses recorded in this wallet")
            ]
            
            for title, value, color, icon, tooltip in summary_data:
                card = self.create_summary_card(summary_frame, title, value, color, icon, tooltip)
                card.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Two Column Layout
        columns_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
        columns_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        left_column = tk.Frame(columns_frame, bg=self.styles.colors["bg"])
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        right_column = tk.Frame(columns_frame, bg=self.styles.colors["bg"])
        right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            self.create_recent_transactions(left_column)
            self.create_financial_chart(left_column)
            self.create_expense_chart(right_column)
            self.create_income_section(right_column)
    
    def create_wallet_card(self, parent, wallet):
        card = tk.Frame(parent, bg=self.styles.colors["card"], relief="flat",
                       highlightbackground=self.styles.colors["border"], highlightthickness=1)
        
        content_frame = tk.Frame(card, bg=self.styles.colors["card"], padx=25, pady=25)
        content_frame.pack(fill="both", expand=True)
        
        header_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        header_frame.pack(fill="x", pady=(0, 15))
        
        wallet_icon = tk.Label(header_frame, text="💳", font=("Arial", 24),
                              bg=self.styles.colors["card"], fg=self.styles.colors["primary"])
        wallet_icon.pack(side="left")
        
        wallet_name_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        wallet_name_frame.pack(side="left", fill="both", expand=True, padx=(12, 0))
        
        tk.Label(wallet_name_frame, text=wallet["name"],
                font=self.styles.fonts["bold"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        currency_symbol = self.controller.get_currency_symbol(wallet["currency"])
        tk.Label(wallet_name_frame, text=f"{currency_symbol} • Default" if wallet.get("is_default") else currency_symbol,
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w")
        
        current_balance = self.controller.db.get_wallet_balance(wallet["id"])
        balance_text = self.controller.format_currency(current_balance, wallet["currency"])
        tk.Label(content_frame, text=balance_text,
                font=("Segoe UI", 26, "bold"), bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        indicator = tk.Frame(content_frame, bg=self.styles.colors["primary"], height=3)
        indicator.pack(fill="x", pady=(12, 0))
        
        return card
    
    def create_summary_card(self, parent, title, value, color, icon, tooltip=""):
        card = tk.Frame(parent, bg=self.styles.colors["card"], relief="flat",
                       highlightbackground=self.styles.colors["border"], highlightthickness=1)
        
        content_frame = tk.Frame(card, bg=self.styles.colors["card"], padx=25, pady=25)
        content_frame.pack(fill="both", expand=True)
        
        icon_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        icon_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(icon_frame, text=icon, font=("Arial", 24),
                bg=self.styles.colors["card"], fg=color).pack(side="left")
        
        # Add tooltip label
        if tooltip:
            tk.Label(icon_frame, text="ⓘ", font=("Segoe UI", 10),
                    bg=self.styles.colors["card"], fg=color,
                    cursor="hand2").pack(side="right")
        
        tk.Label(icon_frame, text=title, font=self.styles.fonts["small"],
                bg=self.styles.colors["card"], fg=self.styles.colors["text_secondary"]).pack(side="right")
        
        tk.Label(content_frame, text=value, font=("Segoe UI", 28, "bold"),
                bg=self.styles.colors["card"], fg=self.styles.colors["text"]).pack(anchor="w")
        
        return card
    
    def create_recent_transactions(self, parent):
        trans_frame = tk.Frame(parent, bg=self.styles.colors["card"])
        trans_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        header_frame = tk.Frame(trans_frame, bg=self.styles.colors["card"], padx=25, pady=25)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Recent Transactions", 
                font=self.styles.fonts["h3"], bg=self.styles.colors["card"], 
                fg=self.styles.colors["text"]).pack(side="left")
        
        # Add info label
        tk.Label(header_frame, text="ⓘ", font=("Segoe UI", 12),
                bg=self.styles.colors["card"], fg=self.styles.colors["info"],
                cursor="hand2").pack(side="left", padx=(5, 0))
        
        see_all_btn = tk.Button(header_frame, text="See All →",
                               font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                               fg=self.styles.colors["primary"], relief="flat",
                               cursor="hand2", command=self.controller.show_all_transactions)
        see_all_btn.pack(side="right")
        
        transactions = self.controller.db.get_recent_transactions(
            self.controller.current_user["id"],
            self.controller.current_wallet["id"]
        )
        
        list_frame = tk.Frame(trans_frame, bg=self.styles.colors["card"])
        list_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        if not transactions:
            tk.Label(list_frame, text="No transactions yet",
                    font=self.styles.fonts["body"], bg=self.styles.colors["card"],
                    fg=self.styles.colors["text_secondary"]).pack(pady=20)
        else:
            for trans in transactions:
                self.create_transaction_item(list_frame, trans)
    
    def create_transaction_item(self, parent, transaction):
        item_frame = tk.Frame(parent, bg=self.styles.colors["card"], height=65)
        item_frame.pack(fill="x", pady=5)
        item_frame.pack_propagate(False)
        
        content_frame = tk.Frame(item_frame, bg=self.styles.colors["card"])
        content_frame.pack(fill="both", expand=True, padx=15)
        
        left_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        left_frame.pack(side="left", fill="y")
        
        icon_text = "💰" if transaction['type'] == 'income' else "💸"
        type_text = "INCOME" if transaction['type'] == 'income' else "EXPENSE"
        type_color = "#10b981" if transaction['type'] == 'income' else "#ef4444"
        
        tk.Label(left_frame, text=icon_text, font=("Arial", 24),
                bg=self.styles.colors["card"], fg=type_color).pack(side="left", padx=(0, 15))
        
        center_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        center_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(center_frame, text=transaction['description'][:50] + ("..." if len(transaction['description']) > 50 else ""),
                font=self.styles.fonts["bold"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"], anchor="w").pack(anchor="w", pady=(2, 0))
        
        formatted_date = self.controller.format_date_for_display(transaction['date'])
        tk.Label(center_frame, text=f"📅 {formatted_date}",
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 2))
        
        right_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        right_frame.pack(side="right", fill="y")
        
        amount_prefix = "+" if transaction['type'] == 'income' else "-"
        amount_color = "#10b981" if transaction['type'] == 'income' else "#ef4444"
        
        currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
        
        tk.Label(right_frame, text=f"{amount_prefix}{currency_symbol}{transaction['amount']:,.2f}",
                font=self.styles.fonts["h4"], bg=self.styles.colors["card"],
                fg=amount_color).pack(pady=5)
        
        separator = tk.Frame(item_frame, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x", padx=15)

    def create_financial_chart(self, parent):
        chart_frame = tk.Frame(parent, bg=self.styles.colors["card"])
        chart_frame.pack(fill="both", expand=True)
        
        header_frame = tk.Frame(chart_frame, bg=self.styles.colors["card"], padx=25, pady=25)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Financial Overview",
                font=self.styles.fonts["h3"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        # Add info label
        tk.Label(header_frame, text="ⓘ Shows income vs expenses breakdown",
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        
        total_income = self.controller.db.get_total_income(self.controller.current_user["id"],
                                                        self.controller.current_wallet["id"])
        total_expenses = self.controller.db.get_total_expenses(self.controller.current_user["id"],
                                                            self.controller.current_wallet["id"])
        
        # Calculate percentages
        total = total_income + total_expenses
        expense_pct = (total_expenses / total * 100) if total > 0 else 0
        income_pct = (total_income / total * 100) if total > 0 else 0
        
        if total_income > 0 or total_expenses > 0:
            # Labels with 3 lines: Category, Percentage, Simple Description
            labels = [
                f'EXPENSES\n{expense_pct:.1f}%\nMoney Out', 
                f'INCOME\n{income_pct:.1f}%\nMoney In'
            ]
            sizes = [total_expenses, total_income]
            
            # Colors: Red for expenses, Green for income
            colors = ['#ef4444', '#10b981']
            
            # Create pie chart with multi-line labels
            ax.pie(sizes, 
                labels=labels, 
                colors=colors,
                labeldistance=0.65,  # Pull labels closer to center for better fit
                startangle=90, 
                textprops={
                    'color': 'white', 
                    'fontweight': 'bold', 
                    'fontsize': 9,
                    'ha': 'center',  # Center align text
                    'va': 'center'   # Vertical center align
                })
            
        else:
            ax.text(0.5, 0.5, 'No data\navailable', 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=12)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
    def create_expense_chart(self, parent):
        chart_frame = tk.Frame(parent, bg=self.styles.colors["card"])
        chart_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # MODIFIED: Header matching Recent Transactions style
        header_frame = tk.Frame(chart_frame, bg=self.styles.colors["card"])
        header_frame.pack(fill="x", padx=25, pady=25)
        
        # Left side: Title and info
        left_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(left_frame, text="Last 30 Days Expenses",
                font=self.styles.fonts["h3"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        tk.Label(left_frame, text="ⓘ Daily spending trend for the past month",
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(5, 0))
        
        # Right side: See All button
        right_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        right_frame.pack(side="right")
        
        # MODIFIED: Matching Recent Transactions button style
        see_all_btn = tk.Button(right_frame, text="See All →",
                            font=self.styles.fonts["small"],
                            bg=self.styles.colors["card"],  # Same background
                            fg=self.styles.colors["primary"],  # Primary color text
                            relief="flat", cursor="hand2",
                            command=self.controller.show_expenses,
                            padx=12, pady=8)  # Consistent padding
        see_all_btn.pack()
        
        # MODIFIED: Separator line
        separator = tk.Frame(chart_frame, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x")
        
        # Rest of your chart code...
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        
        expenses_data = self.controller.db.get_last_30_days_expenses(
            self.controller.current_user["id"],
            self.controller.current_wallet["id"]
        )
        
        if expenses_data and any(amount > 0 for amount in expenses_data.values()):
            dates = []
            amounts = []
            
            today = datetime.now()
            for i in range(30):
                date = today - timedelta(days=29 - i)
                date_str = date.strftime('%Y-%m-%d')
                dates.append(date.strftime('%d/%m'))
                amounts.append(expenses_data.get(date_str, 0))
            
            ax.plot(range(len(dates)), amounts, color=self.styles.colors["primary"], 
                linewidth=2.5, marker='o', markersize=6, markerfacecolor=self.styles.colors["primary"], 
                markeredgecolor=self.styles.colors["primary"], alpha=0.8)
            
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel(f'Amount ({self.controller.get_currency_symbol(self.controller.current_wallet["currency"])})', fontsize=12)
            
            show_every = max(1, len(dates) // 6)
            xticks = list(range(0, len(dates), show_every))
            xtick_labels = [dates[i] for i in xticks]
            ax.set_xticks(xticks)
            ax.set_xticklabels(xtick_labels, rotation=45, ha='right')
            
            ax.grid(True, alpha=0.3, axis='both', linestyle='--', linewidth=0.5)
            
            max_amount = max(amounts)
            ax.set_ylim(0, max_amount * 1.15)
            
        else:
            ax.text(0.5, 0.5, 'No expense data\nfor last 30 days\n\nAdd expenses to see trends', 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=11,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=1', facecolor='#f8f9fa', alpha=0.8))
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(20, 25))
                    
    def create_income_section(self, parent):
        income_frame = tk.Frame(parent, bg=self.styles.colors["card"])
        income_frame.pack(fill="both", expand=True)
        
        # MODIFIED: Header matching Recent Transactions style
        header_frame = tk.Frame(income_frame, bg=self.styles.colors["card"])
        header_frame.pack(fill="x", padx=25, pady=25)
        
        # Left side: Title and info
        left_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(left_frame, text="Recent Income",
                font=self.styles.fonts["h3"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        tk.Label(left_frame, text="ⓘ Latest income entries",
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(5, 0))
        
        # Right side: See All button
        right_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        right_frame.pack(side="right")
        
        # MODIFIED: Matching Recent Transactions button style
        see_all_btn = tk.Button(right_frame, text="See All →",
                            font=self.styles.fonts["small"],
                            bg=self.styles.colors["card"],  # Same background as container
                            fg=self.styles.colors["primary"],  # Primary color text
                            relief="flat", cursor="hand2",
                            command=self.controller.show_income,
                            padx=12, pady=8)  # Balanced padding
        see_all_btn.pack()
        
        # MODIFIED: Separator line for visual separation
        separator = tk.Frame(income_frame, height=1, bg=self.styles.colors["border"])
        separator.pack(fill="x")
        
        # List content
        list_frame = tk.Frame(income_frame, bg=self.styles.colors["card"])
        list_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        incomes = self.controller.db.get_all_income(
            self.controller.current_user["id"],
            self.controller.current_wallet["id"]
        )[:3]
        
        if not incomes:
            tk.Label(list_frame, text="No income recorded",
                    font=self.styles.fonts["body"], bg=self.styles.colors["card"],
                    fg=self.styles.colors["text_secondary"]).pack(pady=20)
        else:
            for income in incomes:
                self.create_income_item(list_frame, income)
                            
    def create_income_item(self, parent, income):
        item_frame = tk.Frame(parent, bg=self.styles.colors["card"])
        item_frame.pack(fill="x", pady=8)
        
        icon_label = tk.Label(item_frame, text="💰", font=("Arial", 20),
                             bg=self.styles.colors["card"], fg="#10b981")
        icon_label.pack(side="left", padx=(0, 15))
        
        details_frame = tk.Frame(item_frame, bg=self.styles.colors["card"])
        details_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(details_frame, text=income['source'],
                font=self.styles.fonts["bold"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"], anchor="w").pack(anchor="w")
        
        formatted_date = self.controller.format_date_for_display(income['date'])
        tk.Label(details_frame, text=formatted_date,
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"], anchor="w").pack(anchor="w")
        
        currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
        tk.Label(item_frame, text=f"+{currency_symbol}{income['amount']:,.2f}",
                font=self.styles.fonts["bold"], bg=self.styles.colors["card"],
                fg="#10b981").pack(side="right")

class IncomePage(BasePage):
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # MODIFIED HEADER - MATCHING DASHBOARD STYLE
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="Income Management", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_text = f"{self.controller.current_wallet['name']} ({currency_symbol})"
            wallet_label = tk.Label(left_header, text=f" | {wallet_text}",
                                  font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                                  fg=self.styles.colors["primary"])
            wallet_label.pack(side="left", padx=(20, 0))
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        add_btn = tk.Button(right_header, text="➕ Add Income",
                           font=self.styles.fonts["bold"],
                           bg=self.styles.colors["primary"], fg="white",
                           relief="raised", cursor="hand2",
                           command=self.controller.show_add_income_dialog,
                           padx=25, pady=12)
        add_btn.pack(side="right", padx=(10, 0))
        
        self.parent.bind('<Control-i>', lambda event: self.controller.show_add_income_dialog())
        
        # Info banner
        info_banner = tk.Frame(content_frame, bg="#e8f5e9", padx=20, pady=12)
        info_banner.pack(fill="x", padx=30, pady=(0, 20))
        
        tk.Label(info_banner, text="💡 Tip: Press Ctrl+I to quickly add income. Income increases your wallet balance.",
                font=self.styles.fonts["body"], bg="#e8f5e9", fg="#2e7d32").pack(anchor="w")
        
        # Income overview cards
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            cards_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
            cards_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            monthly_income = self.controller.db.get_monthly_income(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            yearly_income = self.controller.get_yearly_income()
            avg_income = self.controller.get_average_income()
            
            income_stats = [
                ("This Month", self.controller.format_currency(monthly_income, self.controller.current_wallet["currency"]), "#10b981", "📅", "Income received in current month"),
                ("This Year", self.controller.format_currency(yearly_income, self.controller.current_wallet["currency"]), "#3b82f6", "📊", "Total income in current year"),
                ("Average Monthly", self.controller.format_currency(avg_income, self.controller.current_wallet["currency"]), "#8b5cf6", "📈", "Average income per month")
            ]
            
            for title, value, color, icon, tooltip in income_stats:
                card = self.create_summary_card(cards_frame, title, value, color, icon, tooltip)
                card.pack(side="left", fill="both", expand=True, padx=(0, 20))
            
            table_frame = tk.Frame(content_frame, bg=self.styles.colors["white"])
            table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
            
            columns = [
                {"name": "Source", "width": 180, "anchor": "w"},
                {"name": "Amount", "width": 140, "anchor": "center"},
                {"name": "Date", "width": 140, "anchor": "center"},
                {"name": "Category", "width": 140, "anchor": "w"},
                {"name": "Description", "width": 250, "anchor": "w"},
                {"name": "Actions", "width": 120, "anchor": "center"}
            ]
            
            incomes = self.controller.db.get_all_income(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            table_data = []
            actual_data = []
            
            for income in incomes:
                formatted_date = self.controller.format_date_for_display(income['date'])
                currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
                table_data.append([
                    income['source'],
                    f"{currency_symbol}{income['amount']:,.2f}",
                    formatted_date,
                    income['category'],
                    income['description'][:35] + "..." if len(income['description']) > 35 else income['description'],
                    ""
                ])
                actual_data.append(income)
            
            self.income_table = DataTable(table_frame, columns, 
                                         data=table_data, 
                                         actual_data=actual_data,
                                         action_callbacks={
                                             'edit': self.edit_income,
                                             'delete': self.delete_income
                                         },
                                         controller=self.controller)
            
            # Export button
            export_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
            export_frame.pack(fill="x", padx=30, pady=20)
            
            export_btn = tk.Button(export_frame, text="📥 Export to Excel",
                                  font=self.styles.fonts["bold"],
                                  bg="#10b981", fg="white",
                                  relief="flat", cursor="hand2",
                                  command=self.controller.export_income_to_excel,
                                  padx=20, pady=10)
            export_btn.pack(side="right")
    
    def create_summary_card(self, parent, title, value, color, icon, tooltip=""):
        card = tk.Frame(parent, bg=self.styles.colors["card"], relief="flat",
                       highlightbackground=self.styles.colors["border"], highlightthickness=1)
        
        content_frame = tk.Frame(card, bg=self.styles.colors["card"], padx=25, pady=25)
        content_frame.pack(fill="both", expand=True)
        
        icon_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        icon_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(icon_frame, text=icon, font=("Arial", 24),
                bg=self.styles.colors["card"], fg=color).pack(side="left")
        
        if tooltip:
            tk.Label(icon_frame, text="ⓘ", font=("Segoe UI", 10),
                    bg=self.styles.colors["card"], fg=color).pack(side="right")
        
        tk.Label(icon_frame, text=title, font=self.styles.fonts["small"],
                bg=self.styles.colors["card"], fg=self.styles.colors["text_secondary"]).pack(side="right")
        
        tk.Label(content_frame, text=value, font=("Segoe UI", 28, "bold"),
                bg=self.styles.colors["card"], fg=self.styles.colors["text"]).pack(anchor="w")
        
        return card
    
    def edit_income(self, row_index, income_data):
        if not income_data:
            messagebox.showerror("Error", "Income data not found")
            return
        
        self.show_edit_income_dialog(income_data)
    
    def delete_income(self, row_index, income_data):
        if not income_data:
            messagebox.showerror("Error", "Income data not found")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete income from '{income_data['source']}'?"):
            success = self.controller.db.delete_income(income_data['id'], self.controller.current_user["id"])
            if success:
                messagebox.showinfo("Success", "Income deleted successfully!")
                self.show()
            else:
                messagebox.showerror("Error", "Failed to delete income")
    
    def show_edit_income_dialog(self, income):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Income")
        dialog.geometry("550x650")
        dialog.configure(bg=self.controller.styles.colors["white"])
        dialog.resizable(False, False)
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        main_container = tk.Frame(dialog, bg=self.controller.styles.colors["white"], padx=30, pady=30)
        main_container.pack(fill="both", expand=True)
        
        tk.Label(main_container, text="Edit Income", 
                font=self.controller.styles.fonts["h2"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 30))
        
        form_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="Income Source *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        source_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                               bg=self.controller.styles.colors["input_bg"], 
                               fg=self.controller.styles.colors["input_fg"],
                               relief="flat", highlightthickness=1)
        source_entry.pack(fill="x", pady=(0, 20))
        source_entry.insert(0, income['source'])
        
        tk.Label(form_frame, text="Amount *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        amount_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                               bg=self.controller.styles.colors["input_bg"], 
                               fg=self.controller.styles.colors["input_fg"],
                               relief="flat", highlightthickness=1)
        amount_entry.insert(0, str(income['amount']))
        
        tk.Label(form_frame, text="Category", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        category_var = tk.StringVar()
        categories = ["Salary", "Freelance", "Business", "Investment", 
                    "Dividends", "Bonus", "Gift", "Other"]
        category_menu = ttk.Combobox(form_frame, textvariable=category_var,
                                    values=categories, state="readonly")
        category_menu.pack(fill="x", pady=(0, 20))
        category_menu.set(income['category'] if income['category'] else "Salary")
        
        tk.Label(form_frame, text="Date", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        try:
            date_obj = datetime.strptime(income['date'], '%Y-%m-%d')
        except:
            date_obj = datetime.now()
        
        date_entry = DatePicker(form_frame, font=self.controller.styles.fonts["body"],
                            background=self.controller.styles.colors["input_bg"], 
                            foreground=self.controller.styles.colors["input_fg"],
                            borderwidth=1, date_pattern='yyyy-mm-dd')
        date_entry.pack(fill="x", pady=(0, 20))
        date_entry.set_date(date_obj)
        
        tk.Label(form_frame, text="Description", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        desc_entry = tk.Text(form_frame, font=self.controller.styles.fonts["body"],
                            bg=self.controller.styles.colors["input_bg"], 
                            fg=self.controller.styles.colors["input_fg"],
                            relief="flat", highlightthickness=1,
                            highlightbackground=self.controller.styles.colors["border"],
                            highlightcolor=self.controller.styles.colors["primary"],
                            height=4, wrap="word")
        desc_entry.pack(fill="x", pady=(0, 30))
        desc_entry.insert("1.0", income['description'])
        
        def save_changes():
            source = source_entry.get().strip()
            amount = amount_entry.get()
            category = category_var.get()
            date = date_entry.get_date()
            description = desc_entry.get("1.0", "end").strip()
            
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
            
            cursor = self.controller.db.conn.cursor()
            try:
                cursor.execute('''
                    UPDATE income SET 
                        source = ?, 
                        amount = ?, 
                        category = ?, 
                        date = ?, 
                        description = ?
                    WHERE id = ? AND user_id = ?
                ''', (source, amount_float, category, 
                    date.strftime('%Y-%m-%d'), description, 
                    income['id'], self.controller.current_user["id"]))
                self.controller.db.conn.commit()
                
                messagebox.showinfo("Success", "Income updated successfully!")
                dialog.destroy()
                self.show()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update income: {str(e)}")
        
        button_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                            font=self.controller.styles.fonts["body"], bg=self.controller.styles.colors["gray_light"],
                            fg="white", relief="flat", cursor="hand2",
                            command=dialog.destroy,
                            padx=30, pady=10)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(button_frame, text="💾 Save Changes",
                            font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=save_changes,
                            padx=30, pady=10)
        save_btn.pack(side="right")
        
        def on_enter_key(event):
            save_btn.invoke()
        
        dialog.bind('<Return>', on_enter_key)

class ExpensesPage(BasePage):
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # MODIFIED HEADER - MATCHING DASHBOARD STYLE
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="Expense Management", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_text = f"{self.controller.current_wallet['name']} ({currency_symbol})"
            wallet_label = tk.Label(left_header, text=f" | {wallet_text}",
                                  font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                                  fg=self.styles.colors["primary"])
            wallet_label.pack(side="left", padx=(20, 0))
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        add_btn = tk.Button(right_header, text="➕ Add Expense",
                           font=self.styles.fonts["bold"],
                           bg=self.styles.colors["primary"], fg="white",
                           relief="raised", cursor="hand2",
                           command=self.controller.show_add_expense_dialog,
                           padx=25, pady=12)
        add_btn.pack(side="right", padx=(10, 0))
        
        self.parent.bind('<Control-e>', lambda event: self.controller.show_add_expense_dialog())
        
        # Info banner
        info_banner = tk.Frame(content_frame, bg="#ffebee", padx=20, pady=12)
        info_banner.pack(fill="x", padx=30, pady=(0, 20))
        
        tk.Label(info_banner, text="💡 Tip: Press Ctrl+E to quickly add expenses. Expenses reduce your wallet balance.",
                font=self.styles.fonts["body"], bg="#ffebee", fg="#c62828").pack(anchor="w")
        
        # Expense overview cards
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            cards_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
            cards_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            monthly_expense = self.controller.db.get_monthly_expense(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            yearly_expense = self.controller.get_yearly_expense()
            avg_expense = self.controller.get_average_expense()
            
            expense_stats = [
                ("This Month", self.controller.format_currency(monthly_expense, self.controller.current_wallet["currency"]), "#ef4444", "📅", "Expenses in current month"),
                ("This Year", self.controller.format_currency(yearly_expense, self.controller.current_wallet["currency"]), "#f97316", "📊", "Total expenses in current year"),
                ("Average Monthly", self.controller.format_currency(avg_expense, self.controller.current_wallet["currency"]), "#ec4899", "📉", "Average expenses per month")
            ]
            
            for title, value, color, icon, tooltip in expense_stats:
                card = self.create_summary_card(cards_frame, title, value, color, icon, tooltip)
                card.pack(side="left", fill="both", expand=True, padx=(0, 20))
            
            # Category breakdown chart - FIXED: No Total bar, pure categories
            category_frame = tk.Frame(content_frame, bg=self.styles.colors["white"])
            category_frame.pack(fill="x", padx=30, pady=(0, 20))

            tk.Label(category_frame, text="Expense by Category",
                    font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                    fg=self.styles.colors["text"]).pack(anchor="w", padx=25, pady=25)

            # Add info label
            tk.Label(category_frame, text="ⓘ Shows top spending categories",
                    font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                    fg=self.styles.colors["text_secondary"]).pack(anchor="w", padx=25, pady=(0, 15))

            fig, ax = plt.subplots(figsize=(9, 5), dpi=100)

            category_data = self.controller.db.get_expense_by_category(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )

            if category_data:
                categories = list(category_data.keys())
                amounts = list(category_data.values())
                
                # Sort categories by amount (descending)
                sorted_indices = sorted(range(len(amounts)), key=lambda i: amounts[i], reverse=True)
                categories = [categories[i] for i in sorted_indices]
                amounts = [amounts[i] for i in sorted_indices]
                
                # Calculate total for context (not shown as a bar)
                total_expenses = sum(amounts)
                
                # Limit to top categories for readability
                max_categories = min(8, len(categories))
                categories = categories[:max_categories]
                amounts = amounts[:max_categories]
                
                # Create bar chart - NO TOTAL BAR INCLUDED
                x_pos = range(len(categories))
                bars = ax.bar(x_pos, amounts, color=self.styles.colors["primary"], 
                            alpha=0.8, width=0.6, edgecolor='white', linewidth=1.5)
                
                # Add value labels on top of each bar
                currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
                for bar, amount in zip(bars, amounts):
                    # Calculate percentage of total
                    percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                    
                    # Format the value
                    if amount >= 1000:
                        value_text = f"{currency_symbol}{amount/1000:.1f}K\n({percentage:.1f}%)"
                    else:
                        value_text = f"{currency_symbol}{amount:.0f}\n({percentage:.1f}%)"
                    
                    # Position text above the bar
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + (max(amounts) * 0.02),
                        value_text,
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold', linespacing=1.2,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                    alpha=0.9, edgecolor='lightgray', linewidth=0.5))
                
                # Set x-axis labels (categories) with rotation
                ax.set_xticks(x_pos)
                ax.set_xticklabels(categories, fontsize=10, fontweight='bold', rotation=45, ha='right')
                
                # Set y-axis label
                ax.set_ylabel(f'Amount ({currency_symbol})', fontsize=11, fontweight='bold')
                
                # Add grid for better readability
                ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.5)
                
                # Remove top and right spines for cleaner look
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_linewidth(0.5)
                ax.spines['bottom'].set_linewidth(0.5)
                
                # Set light background color
                ax.set_facecolor('#f8f9fa')
                
                # Auto-adjust y-axis limit to accommodate labels
                max_amount = max(amounts)
                ax.set_ylim(0, max_amount * 1.2)  # Extra space for labels
                
            else:
                # No data message
                ax.text(0.5, 0.5, 'No expense data yet\n\nAdd expenses to see category breakdown', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=1', facecolor='#f8f9fa', alpha=0.8))
                ax.set_facecolor('#f8f9fa')
                
                # Remove spines
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.set_xticks([])
                ax.set_yticks([])

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, category_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=25, pady=(0, 25))
            
            # Expense table
                        # Expense table section
            table_frame = tk.Frame(content_frame, bg=self.styles.colors["white"])
            table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

            columns = [
                {"name": "Category", "width": 140, "anchor": "w"},
                {"name": "Amount", "width": 140, "anchor": "center"},
                {"name": "Date", "width": 140, "anchor": "center"},
                {"name": "Payment Method", "width": 160, "anchor": "w"},
                {"name": "Description", "width": 250, "anchor": "w"},
                {"name": "Actions", "width": 120, "anchor": "center"}
            ]

            expenses = self.controller.db.get_all_expenses(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            table_data = []
            actual_data = []

                    # In ExpensesPage.show() method, in the table data creation section:
            for expense in expenses:
                formatted_date = self.controller.format_date_for_display(expense['date'])
                currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
                table_data.append([
                    expense['category'],
                    f"-{currency_symbol}{expense['amount']:,.2f}",
                    formatted_date,
                    expense['description'][:35] + "..." if len(expense['description']) > 35 else expense['description'],
                    expense['payment_method'],

                    ""
                ])
                actual_data.append(expense)

            self.expense_table = DataTable(table_frame, columns, 
                                        data=table_data, 
                                        actual_data=actual_data,
                                        action_callbacks={
                                            'edit': self.edit_expense,
                                            'delete': self.delete_expense
                                        },
                                        controller=self.controller)
            # Export button
            export_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
            export_frame.pack(fill="x", padx=30, pady=20)
            
            export_btn = tk.Button(export_frame, text="📥 Export to Excel",
                                font=self.styles.fonts["bold"],
                                bg="#10b981", fg="white",
                                relief="flat", cursor="hand2",
                                command=self.controller.export_expenses_to_excel,
                                padx=20, pady=10)
            export_btn.pack(side="right")

    def create_summary_card(self, parent, title, value, color, icon, tooltip=""):
        card = tk.Frame(parent, bg=self.styles.colors["card"], relief="flat",
                    highlightbackground=self.styles.colors["border"], highlightthickness=1)
        
        content_frame = tk.Frame(card, bg=self.styles.colors["card"], padx=25, pady=25)
        content_frame.pack(fill="both", expand=True)
        
        icon_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        icon_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(icon_frame, text=icon, font=("Arial", 24),
                bg=self.styles.colors["card"], fg=color).pack(side="left")
        
        if tooltip:
            tk.Label(icon_frame, text="ⓘ", font=("Segoe UI", 10),
                    bg=self.styles.colors["card"], fg=color).pack(side="right")
        
        tk.Label(icon_frame, text=title, font=self.styles.fonts["small"],
                bg=self.styles.colors["card"], fg=self.styles.colors["text_secondary"]).pack(side="right")
        
        tk.Label(content_frame, text=value, font=("Segoe UI", 28, "bold"),
                bg=self.styles.colors["card"], fg=self.styles.colors["text"]).pack(anchor="w")
        
        return card
    
    def edit_expense(self, row_index, expense_data):
        if not expense_data:
            messagebox.showerror("Error", "Expense data not found")
            return
            
        print("Editing expense data:")
        print(f"  ID: {expense_data['id']}")
        print(f"  Category: {expense_data['category']}")
        print(f"  Amount: {expense_data['amount']}")
        print(f"  Payment Method: {expense_data.get('payment_method', 'N/A')}")
        print(f"  Description: {expense_data.get('description', 'N/A')}")
        
        self.show_edit_expense_dialog(expense_data)
    
    def delete_expense(self, row_index, expense_data):
        if not expense_data:
            messagebox.showerror("Error", "Expense data not found")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete expense for '{expense_data['category']}'?"):
            success = self.controller.db.delete_expense(expense_data['id'], self.controller.current_user["id"])
            if success:
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.show()
            else:
                messagebox.showerror("Error", "Failed to delete expense")
    
    def show_edit_expense_dialog(self, expense):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Expense")
        dialog.geometry("550x650")
        dialog.configure(bg=self.controller.styles.colors["white"])
        dialog.resizable(False, False)
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        main_container = tk.Frame(dialog, bg=self.controller.styles.colors["white"], padx=30, pady=30)
        main_container.pack(fill="both", expand=True)
        
        tk.Label(main_container, text="Edit Expense", 
                font=self.controller.styles.fonts["h2"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 30))
        
        form_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="Category *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        category_var = tk.StringVar()
        categories = ["Shopping", "Food", "Transport", "Bills", 
                    "Entertainment", "Healthcare", "Education", "Travel", 
                    "Rent", "Utilities", "Insurance", "Tax", "Other"]
        category_menu = ttk.Combobox(form_frame, textvariable=category_var,
                                    values=categories, state="readonly")
        category_menu.pack(fill="x", pady=(0, 20))
        category_menu.set(expense['category'] if expense['category'] else "Shopping")
        
        tk.Label(form_frame, text="Amount *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        amount_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                            bg=self.controller.styles.colors["input_bg"], 
                            fg=self.controller.styles.colors["input_fg"],
                            relief="flat", highlightthickness=1)
        amount_entry.pack(fill="x", pady=(0, 20))
        amount_entry.insert(0, str(expense['amount']))
        
        tk.Label(form_frame, text="Date", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        try:
            date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        except:
            date_obj = datetime.now()
        
        date_entry = DatePicker(form_frame, font=self.controller.styles.fonts["body"],
                            background=self.controller.styles.colors["input_bg"], 
                            foreground=self.controller.styles.colors["input_fg"],
                            borderwidth=1, date_pattern='yyyy-mm-dd')
        date_entry.pack(fill="x", pady=(0, 20))
        date_entry.set_date(date_obj)
        
        # Payment Method field (but load with Description data)
        tk.Label(form_frame, text="Payment Method", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        payment_var = tk.StringVar()
        payment_menu = ttk.Combobox(form_frame, textvariable=payment_var,
                                values=["Credit Card", "Debit Card", "Cash", 
                                        "Bank Transfer", "Digital Wallet", "Other"],
                                state="readonly")
        payment_menu.pack(fill="x", pady=(0, 20))
        payment_menu.set(expense['description'] if expense['description'] else "Credit Card")
        
        # Description field (but load with Payment Method data)
        tk.Label(form_frame, text="Description", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        desc_entry = tk.Text(form_frame, font=self.controller.styles.fonts["body"],
                            bg=self.controller.styles.colors["input_bg"], 
                            fg=self.controller.styles.colors["input_fg"],
                            relief="flat", highlightthickness=1,
                            highlightbackground=self.controller.styles.colors["border"],
                            highlightcolor=self.controller.styles.colors["primary"],
                            height=4, wrap="word")
        desc_entry.pack(fill="x", pady=(0, 30))
        
        desc_entry.insert("1.0", expense['payment_method'] if expense.get('payment_method') else "")
        
        def save_changes():
            category = category_var.get()
            amount = amount_entry.get()
            date = date_entry.get_date()
            
            # SWAPPED: Get values from swapped fields
            description = payment_var.get()  # From Payment Method field (but actually contains description)
            payment_method = desc_entry.get("1.0", "end").strip()  # From Description field (but actually contains payment method)
            
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
            
            cursor = self.controller.db.conn.cursor()
            try:
                # SWAPPED: Save swapped values back to correct database fields
                cursor.execute('''
                    UPDATE expenses SET 
                        category = ?, 
                        amount = ?, 
                        date = ?, 
                        description = ?, 
                        payment_method = ?  
                    WHERE id = ? AND user_id = ?
                ''', (category, amount_float,
                    date.strftime('%Y-%m-%d'), description, 
                    payment_method, expense['id'], self.controller.current_user["id"]))
                self.controller.db.conn.commit()
                
                messagebox.showinfo("Success", "Expense updated successfully!")
                dialog.destroy()
                self.show()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update expense: {str(e)}")
        
        button_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                            font=self.controller.styles.fonts["body"], bg=self.controller.styles.colors["gray_light"],
                            fg="white", relief="flat", cursor="hand2",
                            command=dialog.destroy,
                            padx=30, pady=10)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(button_frame, text="💾 Save Changes",
                            font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=save_changes,
                            padx=30, pady=10)
        save_btn.pack(side="right")
        
        def on_enter_key(event):
            save_btn.invoke()
        
        dialog.bind('<Return>', on_enter_key)

class ReportsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.current_year = datetime.now().year
        self.available_years = []
        self.summary_table_frame = None
        
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # Header
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="Financial Reports", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_text = f"{self.controller.current_wallet['name']} ({currency_symbol})"
            wallet_label = tk.Label(left_header, text=f" | {wallet_text}",
                                font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                                fg=self.styles.colors["primary"])
            wallet_label.pack(side="left", padx=(20, 0))
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        # Info banner
        info_banner = tk.Frame(content_frame, bg="#fff3e0", padx=20, pady=12)
        info_banner.pack(fill="x", padx=30, pady=(0, 20))
        
        tk.Label(info_banner, text="💡 These reports show trends and breakdowns of your financial data for analysis.",
                font=self.styles.fonts["body"], bg="#fff3e0", fg="#e65100").pack(anchor="w")
        
        # Get available years
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            self.available_years = self.controller.db.get_available_years(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            if not self.available_years:
                self.available_years = [str(datetime.now().year)]
        
        # Reports grid
        reports_grid = tk.Frame(content_frame, bg=self.styles.colors["bg"])
        reports_grid.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Income vs Expense chart
        chart1_frame = tk.Frame(reports_grid, bg=self.styles.colors["white"])
        chart1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=(0, 15))
        
        chart1_header = tk.Frame(chart1_frame, bg=self.styles.colors["white"], padx=25, pady=25)
        chart1_header.pack(fill="x")
        
        tk.Label(chart1_header, text="Income vs Expense Trend",
                font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(chart1_header, text="ⓘ 12-month comparison",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            monthly_data = self.controller.db.get_monthly_summary(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            
            fig1, ax1 = plt.subplots(figsize=(7, 5), dpi=100)
            
            if monthly_data:
                months = [d['month'] for d in monthly_data]
                income = [d['income'] for d in monthly_data]
                expenses = [d['expenses'] for d in monthly_data]
                
                short_months = []
                for month in months:
                    try:
                        year, month_num = month.split('-')
                        month_name = datetime.strptime(month_num, "%m").strftime("%b")
                        short_months.append(f"{month_name} '{year[2:]}")
                    except:
                        short_months.append(month[:7])
                
                ax1.plot(short_months, income, label='Income', color='#10b981', linewidth=2, marker='o')
                ax1.plot(short_months, expenses, label='Expenses', color='#ef4444', linewidth=2, marker='o')
                ax1.fill_between(short_months, income, expenses, alpha=0.2, color='#3b82f6')
                ax1.legend(loc='upper left', fontsize=11)
                ax1.grid(True, alpha=0.3)
                ax1.set_ylabel(f'Amount ({self.controller.get_currency_symbol(self.controller.current_wallet["currency"])})', fontsize=12)
                
                plt.xticks(rotation=45)
            else:
                ax1.text(0.5, 0.5, 'No data available', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax1.transAxes,
                    fontsize=12)
            
            plt.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, chart1_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Expense Distribution - Enhanced pie chart
        chart2_frame = tk.Frame(reports_grid, bg=self.styles.colors["white"])
        chart2_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=(0, 15))
        
        chart2_header = tk.Frame(chart2_frame, bg=self.styles.colors["white"], padx=25, pady=25)
        chart2_header.pack(fill="x")
        
        tk.Label(chart2_header, text="Expense Distribution",
                font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        tk.Label(chart2_header, text="ⓘ Category breakdown",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        fig2, ax2 = plt.subplots(figsize=(7, 5), dpi=100)
        
        category_data = self.controller.db.get_expense_by_category(
            self.controller.current_user["id"],
            self.controller.current_wallet["id"]
        )
        
        if category_data:
            categories = list(category_data.keys())
            amounts = list(category_data.values())
            
            sorted_data = sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)
            categories = [item[0] for item in sorted_data]
            amounts = [item[1] for item in sorted_data]
            
            total_expenses = sum(amounts)
            percentages = [(amount / total_expenses * 100) if total_expenses > 0 else 0 for amount in amounts]
            
            # Show only significant categories
            show_labels = []
            show_amounts = []
            other_categories = []
            other_amount = 0
            
            for i, (category, amount, percentage) in enumerate(zip(categories, amounts, percentages)):
                if percentage >= 5.0 and len(show_labels) < 5:
                    show_labels.append(category)
                    show_amounts.append(amount)
                else:
                    other_categories.append(category)
                    other_amount += amount
            
            if other_amount > 0:
                show_labels.append("Other")
                show_amounts.append(other_amount)
            
            colors = ['#4361ee', '#4cc9f0', '#7209b7', '#f8961e', '#ffd166', 
                    '#06d6a0', '#ef476f', '#118ab2', '#ff9a76', '#a663cc']
            
            def autopct_format(pct, allvals):
                absolute = pct / 100. * sum(allvals)
                return f'{pct:.1f}%\n({self.controller.get_currency_symbol(self.controller.current_wallet["currency"])}{absolute:,.0f})'
            
            wedges, texts, autotexts = ax2.pie(
                show_amounts, 
                labels=show_labels, 
                colors=colors[:len(show_labels)],
                autopct=lambda pct: autopct_format(pct, show_amounts),
                startangle=90,
                textprops={'fontsize': 10, 'color': 'white', 'fontweight': 'bold'},
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
            )
            
            for autotext in autotexts:
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            ax2.set_title(f'Total: {self.controller.get_currency_symbol(self.controller.current_wallet["currency"])}{total_expenses:,.0f}', 
                        fontsize=11, fontweight='bold', pad=10)
            
            if other_categories and "Other" in show_labels:
                legend_text = f"Other includes: {', '.join(other_categories[:3])}"
                if len(other_categories) > 3:
                    legend_text += f" and {len(other_categories) - 3} more"
                ax2.text(0.5, -0.15, legend_text,
                    transform=ax2.transAxes,
                    fontsize=8,
                    ha='center',
                    va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.3))
            
        else:
            ax2.text(0.5, 0.5, 'No expense data yet\n\nAdd expenses to see\ncategory breakdown', 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax2.transAxes,
                fontsize=11,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=1', facecolor='#f8f9fa', alpha=0.8))
        
        ax2.axis('equal')
        plt.tight_layout()
        
        canvas2 = FigureCanvasTkAgg(fig2, chart2_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # === YEARLY SUMMARY SECTION WITH DROPDOWN ===
        summary_section = tk.Frame(reports_grid, bg=self.styles.colors["bg"])
        summary_section.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))
        
        # Header with year selector
        summary_header = tk.Frame(summary_section, bg=self.styles.colors["white"])
        summary_header.pack(fill="x", padx=0, pady=(0, 15))
        
        # Left side: Title
        title_frame = tk.Frame(summary_header, bg=self.styles.colors["white"])
        title_frame.pack(side="left", fill="x", expand=True, padx=25, pady=25)
        
        tk.Label(title_frame, text="Yearly Summary",
                font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        tk.Label(title_frame, text="ⓘ Income and expenses by month",
                font=self.styles.fonts["small"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w")
        
        # Right side: Year selector
        year_selector_frame = tk.Frame(summary_header, bg=self.styles.colors["white"])
        year_selector_frame.pack(side="right", padx=25, pady=25)
        
        tk.Label(year_selector_frame, text="Year:",
                font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left", padx=(0, 10))
        
        # Year dropdown
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_dropdown = ttk.Combobox(year_selector_frame, textvariable=self.year_var,
                                    values=self.available_years, state="readonly",
                                    font=self.styles.fonts["body"], width=8)
        year_dropdown.pack(side="left")
        
        # Update button
        update_btn = tk.Button(year_selector_frame, text="Update",
                            font=self.styles.fonts["body"], bg=self.styles.colors["primary"],
                            fg="white", relief="flat", cursor="hand2",
                            command=self.update_year_summary,
                            padx=15, pady=6)
        update_btn.pack(side="left", padx=(10, 0))
        
        # Table frame
        self.summary_table_frame = tk.Frame(summary_section, bg=self.styles.colors["white"])
        self.summary_table_frame.pack(fill="both", expand=True)
        
        # Initial load of summary table
        self.update_year_summary()
        
        # Download report button
        download_frame = tk.Frame(summary_section, bg=self.styles.colors["white"])
        download_frame.pack(fill="x", padx=25, pady=25)
        
        download_btn = tk.Button(download_frame, text="📊 Download Full Report",
                                font=self.styles.fonts["bold"],
                                bg=self.styles.colors["primary"], fg="white",
                                relief="flat", cursor="hand2",
                                command=self.controller.generate_full_report,
                                padx=20, pady=10)
        download_btn.pack(side="right")
        
        reports_grid.grid_columnconfigure(0, weight=1)
        reports_grid.grid_columnconfigure(1, weight=1)
        reports_grid.grid_rowconfigure(0, weight=1)
        reports_grid.grid_rowconfigure(1, weight=0)

    def update_year_summary(self):
        # Clear existing table
        for widget in self.summary_table_frame.winfo_children():
            widget.destroy()
        
        # Get selected year
        try:
            selected_year = int(self.year_var.get())
        except ValueError:
            selected_year = datetime.now().year
        
        # Get summary data for selected year
        monthly_summary = self.get_yearly_summary_table(selected_year)
        
        if monthly_summary:
            columns = [
                {"name": "Month", "width": 240, "anchor": "w"},
                {"name": "Income", "width": 180, "anchor": "w"},
                {"name": "Expenses", "width": 180, "anchor": "w"}
            ]
            
            self.summary_table = DataTable(self.summary_table_frame, columns, monthly_summary, controller=self.controller)
        else:
            tk.Label(self.summary_table_frame, text=f"No data available for {selected_year}",
                    font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                    fg=self.styles.colors["text_secondary"], pady=50).pack()

    def get_yearly_summary_table(self, year):
        monthly_data = self.controller.db.get_monthly_summary(
            self.controller.current_user["id"],
            self.controller.current_wallet["id"],
            year
        )
        table_data = []
        
        for data in monthly_data:
            income = data['income']
            expenses = data['expenses']
            
            try:
                year, month = data['month'].split('-')
                month_name = datetime.strptime(month, "%m").strftime("%b")
                month_display = f"{month_name} {year}"
            except:
                month_display = data['month']
            
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            table_data.append([
                month_display,
                f"{currency_symbol}{income:,.2f}",
                f"{currency_symbol}{expenses:,.2f}"
            ])
        
        return table_data
# In the AllTransactionsPage class, replace the show() method with this:

class AllTransactionsPage(BasePage):
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # Header
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="All Transactions", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_text = f"{self.controller.current_wallet['name']} ({currency_symbol})"
            wallet_label = tk.Label(left_header, text=f" | {wallet_text}",
                                  font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                                  fg=self.styles.colors["primary"])
            wallet_label.pack(side="left", padx=(20, 0))
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        # Get all transactions for current wallet
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            all_transactions = []
            
            # Fetch income transactions
            incomes = self.controller.db.get_all_income(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            for income in incomes:
                all_transactions.append({
                    'id': income['id'],
                    'description': income['source'],
                    'amount': income['amount'],
                    'date': income['date'],
                    'type': 'income',
                    'category': income['category'],
                    'details': income['description']
                })
            
            # Fetch expense transactions
            expenses = self.controller.db.get_all_expenses(
                self.controller.current_user["id"],
                self.controller.current_wallet["id"]
            )
            for expense in expenses:
                all_transactions.append({
                    'id': expense['id'],
                    'description': expense['category'],
                    'amount': expense['amount'],
                    'date': expense['date'],
                    'type': 'expense',
                    'payment_method': expense['payment_method'],
                    'details': expense['description']
                })
            
            # Sort by date (newest first)
            all_transactions.sort(key=lambda x: x['date'], reverse=True)
            
            # Create main container
            trans_frame = tk.Frame(content_frame, bg=self.styles.colors["white"])
            trans_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            if not all_transactions:
                # Show empty state
                empty_frame = tk.Frame(trans_frame, bg=self.styles.colors["white"], height=400)
                empty_frame.pack(fill="both", expand=True)
                
                tk.Label(empty_frame, text="No transactions found",
                        font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                        fg=self.styles.colors["text_secondary"], pady=50).pack()
                
                tk.Label(empty_frame, text="Start by adding income or expenses to see them here",
                        font=self.styles.fonts["body"], bg=self.styles.colors["white"],
                        fg=self.styles.colors["text_secondary"]).pack()
                
                create_btn = tk.Button(empty_frame, text="Add First Transaction",
                                      font=self.styles.fonts["bold"],
                                      bg=self.styles.colors["primary"], fg="white",
                                      relief="flat", cursor="hand2",
                                      command=self.controller.show_add_income_dialog,
                                      padx=30, pady=15)
                create_btn.pack(pady=20)
            else:
                # Create transaction items
                for trans in all_transactions:
                    self.create_transaction_item(trans_frame, trans)
    
    def create_transaction_item(self, parent, transaction):
        # BALANCED SIZE - not too small, not too big
        item_frame = tk.Frame(parent, bg=self.styles.colors["white"])
        item_frame.pack(fill="x", padx=15, pady=5)  # Comfortable spacing
        
        # Use grid for tight layout
        item_frame.grid_columnconfigure(0, weight=0)  # Icon
        item_frame.grid_columnconfigure(1, weight=1)  # Details
        item_frame.grid_columnconfigure(2, weight=0)  # Amount
        
        # Icon - BIGGER (24px)
        icon_text = "💰" if transaction['type'] == 'income' else "💸"
        type_color = "#10b981" if transaction['type'] == 'income' else "#ef4444"
        tk.Label(item_frame, text=icon_text, font=("Arial", 24),  # Increased size
                bg=self.styles.colors["white"], fg=type_color).grid(row=0, column=0, rowspan=2, padx=(10, 15), pady=5)
        
        # First line: Description and Type
        top_line = tk.Frame(item_frame, bg=self.styles.colors["white"])
        top_line.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        tk.Label(top_line, text=transaction['description'],
                font=self.styles.fonts["bold"],  # 13px bold
                bg=self.styles.colors["white"],
                fg=self.styles.colors["text"]).pack(side="left")
        
        type_text = "INCOME" if transaction['type'] == 'income' else "EXPENSE"
        tk.Label(top_line, text=f" • {type_text}",
                font=self.styles.fonts["small"],  # 11px
                bg=self.styles.colors["white"],
                fg=type_color).pack(side="left", padx=(8, 0))
        
        # Second line: Date and Category/Payment
        bottom_line = tk.Frame(item_frame, bg=self.styles.colors["white"])
        bottom_line.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        formatted_date = self.controller.format_date_for_display(transaction['date'])
        tk.Label(bottom_line, text=f"📅 {formatted_date}",
                font=self.styles.fonts["body"],  # 13px
                bg=self.styles.colors["white"],
                fg=self.styles.colors["text_secondary"]).pack(side="left")
        
        if transaction['type'] == 'income' and transaction.get('category'):
            tk.Label(bottom_line, text=f" • {transaction['category']}",
                    font=self.styles.fonts["body"],
                    bg=self.styles.colors["white"],
                    fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        elif transaction['type'] == 'expense' and transaction.get('payment_method'):
            tk.Label(bottom_line, text=f" • {transaction['payment_method']}",
                    font=self.styles.fonts["body"],
                    bg=self.styles.colors["white"],
                    fg=self.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        # Amount - BIGGER (h4 = 17px bold)
        amount_prefix = "+" if transaction['type'] == 'income' else "-"
        amount_color = "#10b981" if transaction['type'] == 'income' else "#ef4444"
        currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
        
        tk.Label(item_frame, text=f"{amount_prefix}{currency_symbol}{transaction['amount']:,.2f}",
                font=self.styles.fonts["h4"],  # 17px bold - more readable
                bg=self.styles.colors["white"],
                fg=amount_color).grid(row=0, column=2, rowspan=2, padx=(15, 20), pady=5)
        
        # Visible separator
        separator = tk.Frame(parent, height=1, bg="#e0e0e0")
        separator.pack(fill="x", padx=15)

class WalletsPage(BasePage):
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # MODIFIED HEADER - MATCHING DASHBOARD STYLE
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="My Wallets", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        add_btn = tk.Button(right_header, text="➕ Add Wallet",
                           font=self.styles.fonts["bold"],
                           bg=self.styles.colors["primary"], fg="white",
                           relief="raised", cursor="hand2",
                           command=self.controller.show_add_wallet_dialog,
                           padx=25, pady=12)
        add_btn.pack(side="right", padx=(10, 0))
        
        # Info banner
        info_banner = tk.Frame(content_frame, bg="#e1f5fe", padx=20, pady=12)
        info_banner.pack(fill="x", padx=30, pady=(0, 20))
        
        tk.Label(info_banner, text="💡 Each wallet tracks finances separately. Set a default wallet for quick access.",
                font=self.styles.fonts["body"], bg="#e1f5fe", fg="#01579b").pack(anchor="w")
        
        wallets = self.controller.db.get_wallets(self.controller.current_user["id"])
        
        wallets_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
        wallets_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        if not wallets:
            empty_frame = tk.Frame(wallets_frame, bg=self.styles.colors["bg"], height=400)
            empty_frame.pack(fill="both", expand=True)
            
            tk.Label(empty_frame, text="No wallets yet",
                    font=self.styles.fonts["h3"], bg=self.styles.colors["bg"],
                    fg=self.styles.colors["text_secondary"], pady=50).pack()
            
            tk.Label(empty_frame, text="Create your first wallet to start tracking finances",
                    font=self.styles.fonts["body"], bg=self.styles.colors["bg"],
                    fg=self.styles.colors["text_secondary"]).pack()
            
            create_btn = tk.Button(empty_frame, text="Create First Wallet",
                                  font=self.styles.fonts["bold"],
                                  bg=self.styles.colors["primary"], fg="white",
                                  relief="flat", cursor="hand2",
                                  command=self.controller.show_add_wallet_dialog,
                                  padx=30, pady=15)
            create_btn.pack(pady=20)
        else:
            rows_needed = (len(wallets) + 1) // 2
            
            for row in range(rows_needed):
                row_frame = tk.Frame(wallets_frame, bg=self.styles.colors["bg"])
                row_frame.pack(fill="x", pady=(0, 20))
                
                for col in range(2):
                    wallet_index = row * 2 + col
                    if wallet_index < len(wallets):
                        wallet = wallets[wallet_index]
                        card = self.create_wallet_card(row_frame, wallet)
                        card.grid(row=0, column=col, padx=(0, 20), sticky="nsew")
                        row_frame.grid_columnconfigure(col, weight=1)
    
    def create_wallet_card(self, parent, wallet):
        card = tk.Frame(parent, bg=self.styles.colors["card"], relief="flat",
                       highlightbackground=self.styles.colors["border"], highlightthickness=1,
                       width=520)
        
        content_frame = tk.Frame(card, bg=self.styles.colors["card"], padx=25, pady=25)
        content_frame.pack(fill="both", expand=True)
        
        header_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        header_frame.pack(fill="x", pady=(0, 15))
        
        wallet_info_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        wallet_info_frame.pack(side="left", fill="y")
        
        wallet_icon = tk.Label(wallet_info_frame, text="💳", font=("Arial", 24),
                              bg=self.styles.colors["card"], fg=self.styles.colors["primary"])
        wallet_icon.pack(side="left", padx=(0, 15))
        
        wallet_name_frame = tk.Frame(wallet_info_frame, bg=self.styles.colors["card"])
        wallet_name_frame.pack(side="left", fill="y")
        
        tk.Label(wallet_name_frame, text=wallet["name"],
                font=self.styles.fonts["bold"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        currency_symbol = self.controller.get_currency_symbol(wallet["currency"])
        tk.Label(wallet_name_frame, text=currency_symbol,
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w")
        
        action_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        action_frame.pack(side="right")
        
        edit_btn = tk.Button(action_frame, text="Edit",
                           font=self.styles.fonts["small"], bg="#3b82f6",
                           fg="white", relief="flat", cursor="hand2",
                           command=lambda w=wallet: self.edit_wallet(w),
                           padx=10, pady=6)
        edit_btn.pack(side="left", padx=(0, 5))
        
        if not (self.controller.current_wallet and self.controller.current_wallet["id"] == wallet["id"]):
            switch_btn = tk.Button(action_frame, text="Switch",
                                  font=self.styles.fonts["small"], bg="#10b981",
                                  fg="white", relief="flat", cursor="hand2",
                                  command=lambda w=wallet: self.controller.switch_wallet(w["id"]),
                                  padx=10, pady=6)
            switch_btn.pack(side="left", padx=(0, 5))
        
        if not wallet["is_default"]:
            default_btn = tk.Button(action_frame, text="Set Default",
                                  font=self.styles.fonts["small"], bg="#8b5cf6",
                                  fg="white", relief="flat", cursor="hand2",
                                  command=lambda w=wallet: self.controller.set_default_wallet(w["id"]),
                                  padx=10, pady=6)
            default_btn.pack(side="left", padx=(0, 5))
        
        if len(self.controller.db.get_wallets(self.controller.current_user["id"])) > 1:
            delete_btn = tk.Button(action_frame, text="Delete",
                                 font=self.styles.fonts["small"], bg="#ef4444",
                                 fg="white", relief="flat", cursor="hand2",
                                 command=lambda w=wallet: self.delete_wallet(w),
                                 padx=10, pady=6)
            delete_btn.pack(side="left")
        
        current_balance = self.controller.db.get_wallet_balance(wallet["id"])
        balance_text = self.controller.format_currency(current_balance, wallet["currency"])
        tk.Label(content_frame, text=balance_text,
                font=("Segoe UI", 28, "bold"), bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w", pady=(10, 0))
        
        stats_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        stats_frame.pack(fill="x", pady=(20, 0))
        
        total_income = self.controller.db.get_total_income(self.controller.current_user["id"], wallet["id"])
        total_expenses = self.controller.db.get_total_expenses(self.controller.current_user["id"], wallet["id"])
        
        tk.Label(stats_frame, text=f"Income: {self.controller.format_currency(total_income, wallet['currency'])}",
                font=self.styles.fonts["body"], bg=self.styles.colors["card"],
                fg="#10b981").pack(anchor="w")
        
        tk.Label(stats_frame, text=f"Expenses: {self.controller.format_currency(total_expenses, wallet['currency'])}",
                font=self.styles.fonts["body"], bg=self.styles.colors["card"],
                fg="#ef4444").pack(anchor="w")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet and self.controller.current_wallet["id"] == wallet["id"]:
            indicator = tk.Frame(content_frame, bg=self.styles.colors["primary"], height=3)
            indicator.pack(fill="x", pady=(15, 0))
        
        if wallet["is_default"]:
            default_indicator = tk.Frame(content_frame, bg="#10b981", height=3)
            default_indicator.pack(fill="x", pady=(8, 0))
            
            tk.Label(content_frame, text="Default Wallet",
                    font=self.styles.fonts["body"], bg=self.styles.colors["card"],
                    fg="#10b981").pack(anchor="w", pady=(5, 0))
        
        return card
    
    def edit_wallet(self, wallet):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Wallet")
        dialog.geometry("450x350")
        dialog.configure(bg=self.controller.styles.colors["white"])
        dialog.resizable(False, False)
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        main_container = tk.Frame(dialog, bg=self.controller.styles.colors["white"], padx=30, pady=30)
        main_container.pack(fill="both", expand=True)
        
        tk.Label(main_container, text="Edit Wallet", 
                font=self.controller.styles.fonts["h2"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 30))
        
        form_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="Wallet Name *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        name_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                             bg=self.controller.styles.colors["input_bg"], 
                             fg=self.controller.styles.colors["input_fg"],
                             relief="flat", highlightthickness=1,
                             highlightbackground=self.controller.styles.colors["border"],
                             highlightcolor=self.controller.styles.colors["primary"])
        name_entry.pack(fill="x", pady=(0, 20))
        name_entry.insert(0, wallet['name'])
        name_entry.focus_set()
        
        tk.Label(form_frame, text="Currency *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 8))
        
        currency_var = tk.StringVar(value=wallet['currency'])
        currency_menu = ttk.Combobox(form_frame, textvariable=currency_var,
                                    values=["USD", "NTD", "IDR", "EUR", "GBP", "JPY", "CAD", "AUD"],
                                    state="readonly")
        currency_menu.pack(fill="x", pady=(0, 30))
        
        button_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              font=self.controller.styles.fonts["body"], bg=self.controller.styles.colors["gray_light"],
                              fg="white", relief="flat", cursor="hand2",
                              command=dialog.destroy,
                              padx=30, pady=10)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(button_frame, text="💾 Save Changes",
                            font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=lambda: self.save_wallet_changes(dialog, wallet['id'], name_entry.get().strip(), currency_var.get()),
                            padx=30, pady=10)
        save_btn.pack(side="right")
        
        def on_enter_key(event):
            save_btn.invoke()
        
        dialog.bind('<Return>', on_enter_key)
    
    def save_wallet_changes(self, dialog, wallet_id, name, currency):
        if not name:
            messagebox.showerror("Error", "Wallet name cannot be empty")
            return
        
        success = self.controller.db.update_wallet(wallet_id, name, currency)
        if success:
            if self.controller.current_wallet and self.controller.current_wallet["id"] == wallet_id:
                self.controller.current_wallet["name"] = name
                self.controller.current_wallet["currency"] = currency
            
            messagebox.showinfo("Success", "Wallet updated successfully!")
            dialog.destroy()
            self.show()
        else:
            messagebox.showerror("Error", "Failed to update wallet")
    
    def delete_wallet(self, wallet):
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete wallet '{wallet['name']}'?\n\nAll transactions in this wallet will be deleted permanently."):
            success, message = self.controller.db.delete_wallet(wallet["id"], self.controller.current_user["id"])
            if success:
                messagebox.showinfo("Success", message)
                self.show()
            else:
                messagebox.showerror("Error", message)

class BudgetsPage(BasePage):
    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        
        main_content = tk.Frame(self.parent, bg=self.styles.colors["bg"])
        main_content.pack(side="right", fill="both", expand=True)
        
        scrollable_frame = ScrollableFrame(main_content, bg=self.styles.colors["bg"])
        scrollable_frame.pack(fill="both", expand=True)
        content_frame = scrollable_frame.scrollable_frame
        
        # MODIFIED HEADER - MATCHING DASHBOARD STYLE
        header = tk.Frame(content_frame, bg=self.styles.colors["white"])
        header.pack(fill="x", padx=30, pady=20)
        
        left_header = tk.Frame(header, bg=self.styles.colors["white"])
        left_header.pack(side="left", fill="y")
        
        tk.Label(left_header, text="Budget Management", font=self.styles.fonts["h1"],
                bg=self.styles.colors["white"], fg=self.styles.colors["text"]).pack(side="left")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
            wallet_text = f"{self.controller.current_wallet['name']} ({currency_symbol})"
            wallet_label = tk.Label(left_header, text=f" | {wallet_text}",
                                  font=self.styles.fonts["h3"], bg=self.styles.colors["white"],
                                  fg=self.styles.colors["primary"])
            wallet_label.pack(side="left", padx=(20, 0))
        
        right_header = tk.Frame(header, bg=self.styles.colors["white"])
        right_header.pack(side="right", fill="y")
        
        add_btn = tk.Button(right_header, text="➕ Add Budget",
                           font=self.styles.fonts["bold"],
                           bg=self.styles.colors["primary"], fg="white",
                           relief="raised", cursor="hand2",
                           command=self.controller.show_add_budget_dialog,
                           padx=25, pady=12)
        add_btn.pack(side="right", padx=(10, 0))
        
        # Info banner
        info_banner = tk.Frame(content_frame, bg="#f3e5f5", padx=20, pady=12)
        info_banner.pack(fill="x", padx=30, pady=(0, 20))
        
        tk.Label(info_banner, text="💡 Budgets help you control spending. The progress bar shows how much you've used of your monthly limit.",
                font=self.styles.fonts["body"], bg="#f3e5f5", fg="#4a148c").pack(anchor="w")
        
        if hasattr(self.controller, 'current_wallet') and self.controller.current_wallet:
            budgets = self.controller.db.get_budgets(self.controller.current_user["id"], self.controller.current_wallet["id"])
            
            if not budgets:
                empty_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"], height=400)
                empty_frame.pack(fill="both", expand=True, padx=30, pady=20)
                
                tk.Label(empty_frame, text="No budgets yet",
                        font=self.styles.fonts["h3"], bg=self.styles.colors["bg"],
                        fg=self.styles.colors["text_secondary"], pady=50).pack()
                
                tk.Label(empty_frame, text="Create your first budget to track spending limits",
                        font=self.styles.fonts["body"], bg=self.styles.colors["bg"],
                        fg=self.styles.colors["text_secondary"]).pack()
                
                create_btn = tk.Button(empty_frame, text="Create First Budget",
                                      font=self.styles.fonts["bold"],
                                      bg=self.styles.colors["primary"], fg="white",
                                      relief="flat", cursor="hand2",
                                      command=self.controller.show_add_budget_dialog,
                                      padx=30, pady=15)
                create_btn.pack(pady=20)
            else:
                budgets_frame = tk.Frame(content_frame, bg=self.styles.colors["bg"])
                budgets_frame.pack(fill="both", expand=True, padx=30, pady=20)
                
                rows_needed = (len(budgets) + 1) // 2
                
                for row in range(rows_needed):
                    row_frame = tk.Frame(budgets_frame, bg=self.styles.colors["bg"])
                    row_frame.pack(fill="x", pady=(0, 20))
                    
                    for col in range(2):
                        budget_index = row * 2 + col
                        if budget_index < len(budgets):
                            budget = budgets[budget_index]
                            card = self.create_budget_card(row_frame, budget)
                            card.grid(row=0, column=col, padx=(0, 20), sticky="nsew")
                            row_frame.grid_columnconfigure(col, weight=1)
    
    def create_budget_card(self, parent, budget):
        card = tk.Frame(parent, bg=self.styles.colors["card"], relief="flat",
                       highlightbackground=self.styles.colors["border"], highlightthickness=1,
                       width=520)
        
        content_frame = tk.Frame(card, bg=self.styles.colors["card"], padx=25, pady=25)
        content_frame.pack(fill="both", expand=True)
        
        header_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        header_frame.pack(fill="x", pady=(0, 15))
        
        budget_info_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        budget_info_frame.pack(side="left", fill="y")
        
        budget_icon = tk.Label(budget_info_frame, text="💰", font=("Arial", 24),
                              bg=self.styles.colors["card"], fg=self.styles.colors["primary"])
        budget_icon.pack(side="left", padx=(0, 15))
        
        budget_name_frame = tk.Frame(budget_info_frame, bg=self.styles.colors["card"])
        budget_name_frame.pack(side="left", fill="y")
        
        tk.Label(budget_name_frame, text="Overall Budget",
                font=self.styles.fonts["bold"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text"]).pack(anchor="w")
        
        tk.Label(budget_name_frame, text=f"Monthly Budget",
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w")
        
        action_frame = tk.Frame(header_frame, bg=self.styles.colors["card"])
        action_frame.pack(side="right")
        
        edit_btn = tk.Button(action_frame, text="Edit",
                           font=self.styles.fonts["small"], bg="#3b82f6",
                           fg="white", relief="flat", cursor="hand2",
                           command=lambda b=budget: self.edit_budget(b),
                           padx=10, pady=6)
        edit_btn.pack(side="left", padx=(0, 5))
        
        delete_btn = tk.Button(action_frame, text="Delete",
                              font=self.styles.fonts["small"], bg="#ef4444",
                              fg="white", relief="flat", cursor="hand2",
                              command=lambda b=budget: self.delete_budget(b),
                              padx=10, pady=6)
        delete_btn.pack(side="left")
        
        spent_amount = self.controller.db.get_current_month_total_expenses(
            self.controller.current_user["id"],
            self.controller.current_wallet["id"]
        )
        
        progress_bar = BudgetProgressBar(
            content_frame, 
            self.controller,
            budget_amount=budget["amount"],
            spent_amount=spent_amount,
            currency=self.controller.current_wallet["currency"]
        )
        progress_bar.pack(fill="x", pady=(10, 0))
        
        info_frame = tk.Frame(content_frame, bg=self.styles.colors["card"])
        info_frame.pack(fill="x", pady=(20, 0))
        
        currency_symbol = self.controller.get_currency_symbol(self.controller.current_wallet["currency"])
        tk.Label(info_frame, text=f"Budget: {currency_symbol}{budget['amount']:,.0f}",
                font=self.styles.fonts["body"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w")
        
        tk.Label(info_frame, text=f"Created: {self.controller.format_date_for_display(budget['created_at'])}",
                font=self.styles.fonts["small"], bg=self.styles.colors["card"],
                fg=self.styles.colors["text_secondary"]).pack(anchor="w", pady=(8, 0))
        
        return card
    
    def edit_budget(self, budget):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Budget")
        dialog.geometry("450x300")
        dialog.configure(bg=self.controller.styles.colors["white"])
        dialog.resizable(False, False)
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        main_container = tk.Frame(dialog, bg=self.controller.styles.colors["white"], padx=30, pady=30)
        main_container.pack(fill="both", expand=True)
        
        tk.Label(main_container, text="Edit Budget", 
                font=self.controller.styles.fonts["h2"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(anchor="w", pady=(0, 25))
        
        form_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        form_frame.pack(fill="both", expand=True)
        
        # Amount info
        amount_frame = tk.Frame(form_frame, bg=self.controller.styles.colors["white"])
        amount_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(amount_frame, text="Budget Amount *", 
                font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text"]).pack(side="left")
        
        tk.Label(amount_frame, text="ⓘ Monthly spending limit",
                font=self.controller.styles.fonts["small"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text_secondary"]).pack(side="left", padx=(10, 0))
        
        self.amount_entry = tk.Entry(form_frame, font=self.controller.styles.fonts["body"],
                                    bg=self.controller.styles.colors["input_bg"], 
                                    fg=self.controller.styles.colors["input_fg"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=self.controller.styles.colors["border"],
                                    highlightcolor=self.controller.styles.colors["primary"])
        self.amount_entry.pack(fill="x")
        self.amount_entry.insert(0, str(budget['amount']))
        self.amount_entry.focus_set()
        
        # Fixed category and period info
        tk.Label(form_frame, text="Category: Overall • Period: Monthly",
                font=self.controller.styles.fonts["body"], bg=self.controller.styles.colors["white"],
                fg=self.controller.styles.colors["text_secondary"]).pack(anchor="w", pady=(10, 0))
        
        button_frame = tk.Frame(main_container, bg=self.controller.styles.colors["white"])
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              font=self.controller.styles.fonts["body"], bg=self.controller.styles.colors["gray_light"],
                              fg="white", relief="flat", cursor="hand2",
                              command=dialog.destroy,
                              padx=30, pady=10)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(button_frame, text="💾 Save Changes",
                            font=self.controller.styles.fonts["bold"], bg=self.controller.styles.colors["primary"],
                            fg="white", relief="raised", cursor="hand2",
                            command=lambda: self.save_budget_changes(dialog, budget['id'], self.amount_entry.get()),
                            padx=30, pady=10)
        save_btn.pack(side="right")
        
        def on_enter_key(event):
            save_btn.invoke()
        
        dialog.bind('<Return>', on_enter_key)
    
    def save_budget_changes(self, dialog, budget_id, amount):
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        success = self.controller.db.update_budget(budget_id, amount_float, 'Overall', 'monthly')
        if success:
            messagebox.showinfo("Success", "Budget updated successfully!")
            dialog.destroy()
            self.show()
        else:
            messagebox.showerror("Error", "Failed to update budget")
    
    def delete_budget(self, budget):
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete the overall budget?"):
            success = self.controller.db.delete_budget(budget["id"], self.controller.current_user["id"])
            if success:
                messagebox.showinfo("Success", "Budget deleted successfully!")
                self.show()
            else:
                messagebox.showerror("Error", "Failed to delete budget")
