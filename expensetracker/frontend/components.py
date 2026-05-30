import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
import json

# Import backend
from backend.database import Database


class Styles:
    def __init__(self, theme='light'):
        self.theme = theme
        self.update_colors()
        # Enhanced font sizes for better readability
        self.fonts = {
            "h1": ("Segoe UI", 30, "bold"),
            "h2": ("Segoe UI", 24, "bold"),
            "h3": ("Segoe UI", 20, "bold"),
            "h4": ("Segoe UI", 17, "bold"),
            "body": ("Segoe UI", 13),
            "small": ("Segoe UI", 11),
            "bold": ("Segoe UI", 13, "bold")
        }
    
    def update_colors(self):
        if self.theme == 'dark':
            self.colors = {
                "primary": "#4361ee",
                "primary_light": "#4895ef",
                "secondary": "#3f37c9",
                "success": "#4cc9f0",
                "danger": "#f72585",
                "warning": "#f8961e",
                "info": "#7209b7",
                "light": "#2d3748",
                "dark": "#f8f9fa",
                "gray": "#a0aec0",
                "gray_light": "#718096",
                "white": "#1a202c",
                "sidebar": "#1a202c",
                "card": "#2d3748",
                "bg": "#1a202c",
                "green": "#38a169",
                "yellow": "#d69e2e",
                "red": "#e53e3e",
                "dark_red": "#c53030",
                "text": "#e2e8f0",
                "text_secondary": "#a0aec0",
                "border": "#4a5568",
                "input_bg": "#2d3748",
                "input_fg": "#e2e8f0",
                "placeholder": "#a0aec0"
            }
        else:  # light theme
            self.colors = {
                "primary": "#4361ee",
                "primary_light": "#4895ef",
                "secondary": "#3f37c9",
                "success": "#4cc9f0",
                "danger": "#f72585",
                "warning": "#f8961e",
                "info": "#7209b7",
                "light": "#f8f9fa",
                "dark": "#212529",
                "gray": "#6c757d",
                "gray_light": "#adb5bd",
                "white": "#ffffff",
                "sidebar": "#1e293b",
                "card": "#ffffff",
                "bg": "#f8fafc",
                "green": "#4CAF50",
                "yellow": "#FF9800",
                "red": "#F44336",
                "dark_red": "#B71C1C",
                "text": "#212529",
                "text_secondary": "#6c757d",
                "border": "#e2e8f0",
                "input_bg": "#f8f9fa",
                "input_fg": "#212529",
                "placeholder": "#6c757d"
            }
    
    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.update_colors()
        return self.theme

class ModernButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, width=130, height=45, 
                 bg_color="#4361ee", hover_color="#3a56d4", fg_color="white", 
                 font_size=13, radius=8, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, **kwargs)
        self.parent = parent
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.font_size = font_size
        self.radius = radius
        self.is_hovered = False
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw_button()
        
    def draw_button(self):
        self.delete("all")
        color = self.hover_color if self.is_hovered else self.bg_color
        
        self.create_rounded_rect(2, 2, self.winfo_reqwidth()-2, 
                                self.winfo_reqheight()-2, 
                                radius=self.radius, fill=color, outline="")
        
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2,
                        text=self.text, fill=self.fg_color,
                        font=("Segoe UI", self.font_size, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
    
    def on_leave(self, event):
        self.is_hovered = False
        self.draw_button()
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def on_release(self, event):
        pass

class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=self['bg'])
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self['bg'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.scrollable_frame.bind("<Configure>", self._configure_canvas)
        self.canvas.bind("<Configure>", self._configure_window)
        
        self._bind_mousewheel()
        
    def _configure_canvas(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _configure_window(self, event):
        self.canvas.itemconfig(self.window, width=event.width)
    
    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", self._on_mousewheel)
        self.scrollable_frame.bind("<Button-5>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def scroll_to_top(self):
        self.canvas.yview_moveto(0)
    
    def scroll_to_bottom(self):
        self.canvas.yview_moveto(1)
    
    def update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class DatePicker(DateEntry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
    def get_date_str(self):
        return self.get_date().strftime('%Y-%m-%d')

class BudgetProgressBar(tk.Frame):
    def __init__(self, parent, controller, budget_amount, spent_amount, currency, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.budget_amount = budget_amount
        self.spent_amount = spent_amount
        self.currency = currency
        
        self.configure(bg=self.controller.styles.colors["white"] if controller else "white")
        self.create_widgets()
        
    def create_widgets(self):
        percentage = min((self.spent_amount / self.budget_amount) * 100, 100) if self.budget_amount > 0 else 0
        remaining = max(0, self.budget_amount - self.spent_amount)
        overspent = max(0, self.spent_amount - self.budget_amount)
        
        color = self.get_color_for_percentage(percentage)
        
        # Category label
        category_label = tk.Label(self, text="Overall Budget", 
                                 font=("Segoe UI", 14, "bold"), 
                                 bg=self.controller.styles.colors["white"], 
                                 fg=self.controller.styles.colors["text"])
        category_label.pack(anchor="w", pady=(0, 8))
        
        # Budget amount label
        currency_symbol = self.controller.get_currency_symbol(self.currency)
        budget_label = tk.Label(self, text=f"Budget: {currency_symbol}{self.budget_amount:,.0f}", 
                               font=("Segoe UI", 11), 
                               bg=self.controller.styles.colors["white"], 
                               fg=self.controller.styles.colors["text_secondary"])
        budget_label.pack(anchor="w", pady=(0, 10))
        
        # Progress bar container
        bar_container = tk.Frame(self, bg="#e9ecef", height=25)
        bar_container.pack(fill="x", pady=(0, 10))
        bar_container.pack_propagate(False)
        
        canvas = tk.Canvas(bar_container, bg="#e9ecef", height=25, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        def update_progress_bar(event=None):
            canvas_width = canvas.winfo_width()
            if canvas_width < 10:
                canvas_width = 400
            
            canvas.delete("all")
            canvas.create_rectangle(0, 0, canvas_width, 25, fill="#e9ecef", outline="")
            
            fill_width = min((percentage / 100) * canvas_width, canvas_width)
            fill_width_pixels = max(10, fill_width)
            
            canvas.create_rectangle(0, 0, fill_width_pixels, 25, fill=color, outline="")
            
            if fill_width_pixels > 40:
                text_x = min(fill_width_pixels - 35, canvas_width/2)
                canvas.create_text(text_x, 12.5, text=f"{percentage:.1f}%", 
                                 font=("Segoe UI", 10, "bold"), fill="black")
        
        canvas.bind("<Configure>", update_progress_bar)
        self.after(100, update_progress_bar)
        
        # Stats below bar
        stats_frame = tk.Frame(self, bg=self.controller.styles.colors["white"])
        stats_frame.pack(fill="x", pady=(0, 15))
        
        spent_label = tk.Label(stats_frame, text=f"Spent: {currency_symbol}{self.spent_amount:,.2f}", 
                              font=("Segoe UI", 11), 
                              bg=self.controller.styles.colors["white"], 
                              fg="#F44336")
        spent_label.pack(side="left", padx=(0, 20))
        
        if self.spent_amount <= self.budget_amount:
            remaining_label = tk.Label(stats_frame, text=f"Left: {currency_symbol}{remaining:,.2f}", 
                                      font=("Segoe UI", 11), 
                                      bg=self.controller.styles.colors["white"], 
                                      fg="#4CAF50")
            remaining_label.pack(side="left")
        else:
            overspent_label = tk.Label(stats_frame, text=f"Overspent: {currency_symbol}{overspent:,.2f}", 
                                      font=("Segoe UI", 11), 
                                      bg=self.controller.styles.colors["white"], 
                                      fg="#B71C1C")
            overspent_label.pack(side="left")
    
    def get_color_for_percentage(self, percentage):
        if percentage < 75:
            return "#4CAF50"
        elif percentage < 90:
            return "#FF9800"
        elif percentage <= 100:
            return "#F44336"
        else:
            return "#B71C1C"

class FinancialChart:
    @staticmethod
    def create_pie_chart(data, labels, colors, title=""):
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_bar_chart(x_data, y_data, x_label="", y_label="", title=""):
        fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
        bars = ax.bar(range(len(x_data)), y_data, color='#4361ee', alpha=0.7, width=0.8)
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        show_every = max(1, len(x_data) // 6)
        xticks = list(range(0, len(x_data), show_every))
        xtick_labels = [x_data[i] for i in xticks]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xtick_labels, rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_line_chart(x_data, y_data_list, labels, colors, title=""):
        fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
        for i, y_data in enumerate(y_data_list):
            ax.plot(x_data, y_data, label=labels[i], color=colors[i], linewidth=2, marker='o')
        ax.legend()
        ax.grid(True, alpha=0.3)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return fig

class DataTable:
    def __init__(self, parent, columns, data=None, actual_data=None, action_callbacks=None, controller=None):
        self.parent = parent
        self.columns = columns
        self.data = data or []
        self.actual_data = actual_data or []
        self.action_callbacks = action_callbacks or {}
        self.controller = controller
        
        self.table_frame = tk.Frame(parent, bg=self.controller.styles.colors["white"] if controller else "white")
        self.table_frame.pack(fill="both", expand=True)
        
        self.create_table()
    
    def create_table(self):
        # Header
        header_frame = tk.Frame(self.table_frame, 
                               bg=self.controller.styles.colors["bg"] if self.controller else "#f8fafc", 
                               height=55)
        header_frame.pack(fill="x")
        
        for i, col in enumerate(self.columns):
            header_cell = tk.Frame(header_frame, 
                                  bg=self.controller.styles.colors["bg"] if self.controller else "#f8fafc", 
                                  width=col["width"])
            header_cell.grid(row=0, column=i, sticky="nsew", padx=1)
            header_cell.grid_propagate(False)
            
            tk.Label(header_cell, text=col["name"], font=("Segoe UI", 13, "bold"),
                    bg=self.controller.styles.colors["bg"] if self.controller else "#f8fafc", 
                    fg=self.controller.styles.colors["text"] if self.controller else "#212529", 
                    anchor=col["anchor"],
                    padx=12, pady=15).pack(fill="both", expand=True)
            
            header_frame.grid_columnconfigure(i, weight=0, minsize=col["width"])
        
        # Create scrollable table area
        table_container = tk.Frame(self.table_frame, 
                                  bg=self.controller.styles.colors["white"] if self.controller else "white")
        table_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(table_container, 
                          bg=self.controller.styles.colors["white"] if self.controller else "white", 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_table = tk.Frame(canvas, 
                                   bg=self.controller.styles.colors["white"] if self.controller else "white")
        
        scrollable_table.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_table, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        if not self.data:
            empty_frame = tk.Frame(scrollable_table, 
                                  bg=self.controller.styles.colors["white"] if self.controller else "white", 
                                  height=200)
            empty_frame.pack(fill="both", expand=True)
            
            tk.Label(empty_frame, text="No data available.", 
                    font=("Segoe UI", 14), 
                    bg=self.controller.styles.colors["white"] if self.controller else "white", 
                    fg=self.controller.styles.colors["text_secondary"] if self.controller else "#6c757d").pack(pady=20)
        else:
            for idx, row_data in enumerate(self.data):
                row_color = self.controller.styles.colors["bg"] if self.controller and idx % 2 == 0 else self.controller.styles.colors["white"] if self.controller else "#f8fafc" if idx % 2 == 0 else "white"
                row_frame = tk.Frame(scrollable_table, bg=row_color, height=55)
                row_frame.pack(fill="x", pady=1)
                row_frame.pack_propagate(False)
                
                for i, col in enumerate(self.columns):
                    row_frame.grid_columnconfigure(i, weight=0, minsize=col["width"])
                
                # FIX: Create cell frames to enforce column widths and prevent misalignment
                for col_idx, cell_value in enumerate(row_data[:-1] if self.columns[-1]["name"] == "Actions" else row_data):
                    cell_anchor = self.columns[col_idx]["anchor"]
                    
                    # Create cell frame to match header structure
                    cell_frame = tk.Frame(row_frame, 
                                        bg=row_color, 
                                        width=self.columns[col_idx]["width"])
                    cell_frame.grid(row=0, column=col_idx, sticky="nsew", padx=1)
                    cell_frame.grid_propagate(False)
                    
                    # Special handling for Description column
                    if self.columns[col_idx]["name"] == "Description":
                        # Create an inner frame for better text wrapping control
                        inner_frame = tk.Frame(cell_frame, bg=row_color)
                        inner_frame.pack(fill="both", expand=True, padx=12, pady=8)
                        
                        # Calculate wraplength based on column width (adjust as needed)
                        wraplength_value = max(100, self.columns[col_idx]["width"] - 30)
                        
                        cell_label = tk.Label(inner_frame, text=cell_value, 
                                            font=("Segoe UI", 11),  # Slightly smaller font
                                            bg=row_color,
                                            fg=self.controller.styles.colors["text"] if self.controller else "#212529", 
                                            anchor="w",
                                            justify="left",
                                            wraplength=wraplength_value)
                        cell_label.pack(side="left", anchor="nw")
                    else:
                        # For other columns, use the original approach
                        cell_label = tk.Label(cell_frame, text=cell_value, 
                                            font=("Segoe UI", 12), bg=row_color,
                                            fg=self.controller.styles.colors["text"] if self.controller else "#212529", 
                                            anchor=cell_anchor,
                                            padx=12, pady=12)
                        cell_label.pack(fill="both", expand=True)
                # Actions column        
                if len(row_data) > 0 and self.columns[-1]["name"] == "Actions":
                    action_frame = tk.Frame(row_frame, bg=row_color)
                    action_frame.grid(row=0, column=len(self.columns)-1, sticky="nsew", padx=10)
                    
                    actual_data = None
                    if idx < len(self.actual_data):
                        actual_data = self.actual_data[idx]
                    
                    edit_btn = tk.Button(action_frame, text="✏️ Edit",
                                       font=("Segoe UI", 11), bg="#3b82f6",
                                       fg="white", relief="flat", cursor="hand2",
                                       command=lambda idx=idx, data=actual_data: self._on_edit(idx, data),
                                       padx=12, pady=6)
                    edit_btn.pack(side="left", padx=(0, 5))
                    
                    border_frame = tk.Frame(action_frame, bg="#1a2b56", padx=2, pady=2)
                    border_frame.pack(pady=5) # Adjust placement as needed
                    delete_btn = tk.Button(border_frame, text="🗑️ Delete",
                                        font=("Segoe UI", 11, "bold"), bg="white",
                                        fg="#1a2b56", relief="flat", bd=0,
                                        cursor="hand2",
                                        command=lambda idx=idx, data
                                        =actual_data: self._on_delete(idx, data),
                                        padx=10, pady=5)
                    delete_btn.pack(side="left")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    def _on_edit(self, row_index, actual_data):
        if 'edit' in self.action_callbacks:
            self.action_callbacks['edit'](row_index, actual_data)
    
    def _on_delete(self, row_index, actual_data):
        if 'delete' in self.action_callbacks:
            self.action_callbacks['delete'](row_index, actual_data)
    
    def update_data(self, new_data, new_actual_data=None):
        self.data = new_data
        if new_actual_data is not None:
            self.actual_data = new_actual_data
        
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.create_table()

class Dialog:
    def __init__(self, parent, title, width=550, height=650, controller=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.controller = controller
        if controller:
            self.dialog.configure(bg=controller.styles.colors["white"])
        else:
            self.dialog.configure(bg="white")
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def add_field(self, parent, label, widget_type="entry", **kwargs):
        field_frame = tk.Frame(parent, bg=self.controller.styles.colors["white"] if self.controller else "white")
        field_frame.pack(fill="x", pady=(0, 25))
        
        # Create label with tooltip for description
        label_frame = tk.Frame(field_frame, bg=self.controller.styles.colors["white"])
        label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(label_frame, text=label, font=("Segoe UI", 12, "bold"),
                bg=self.controller.styles.colors["white"] if self.controller else "white",
                fg=self.controller.styles.colors["text"] if self.controller else "#212529").pack(side="left")
        
        if "description" in kwargs:
            tk.Label(label_frame, text="ⓘ", font=("Segoe UI", 10),
                    bg=self.controller.styles.colors["white"] if self.controller else "white",
                    fg=self.controller.styles.colors["info"] if self.controller else "blue",
                    cursor="hand2").pack(side="left", padx=(5, 0))
        
        if widget_type == "entry":
            widget = tk.Entry(field_frame, font=("Segoe UI", 12),
                             bg=self.controller.styles.colors["input_bg"] if self.controller else "#f8f9fa", 
                             fg=self.controller.styles.colors["input_fg"] if self.controller else "#212529",
                             relief="flat", highlightthickness=1,
                             highlightbackground=self.controller.styles.colors["border"] if self.controller else "#adb5bd", 
                             highlightcolor=self.controller.styles.colors["primary"] if self.controller else "#4361ee")
            if "default" in kwargs:
                widget.insert(0, kwargs["default"])
            if "placeholder" in kwargs:
                widget.insert(0, kwargs["placeholder"])
                widget.config(fg=self.controller.styles.colors["placeholder"] if self.controller else "gray")
                def on_focus_in(event):
                    if widget.get() == kwargs["placeholder"]:
                        widget.delete(0, tk.END)
                        widget.config(fg=self.controller.styles.colors["input_fg"] if self.controller else "#212529")
                def on_focus_out(event):
                    if not widget.get():
                        widget.insert(0, kwargs["placeholder"])
                        widget.config(fg=self.controller.styles.colors["placeholder"] if self.controller else "gray")
                widget.bind("<FocusIn>", on_focus_in)
                widget.bind("<FocusOut>", on_focus_out)
        elif widget_type == "combobox":
            widget = ttk.Combobox(field_frame, font=("Segoe UI", 12),
                                 state="readonly", values=kwargs.get("values", []))
            if "default" in kwargs:
                widget.set(kwargs["default"])
        elif widget_type == "datepicker":
            widget = DatePicker(field_frame, font=("Segoe UI", 12),
                               background=self.controller.styles.colors["input_bg"] if self.controller else 'white', 
                               foreground=self.controller.styles.colors["input_fg"] if self.controller else 'black',
                               borderwidth=1, date_pattern='yyyy-mm-dd')
            widget.set_date(kwargs.get("default", datetime.now()))
        elif widget_type == "text":
            widget = tk.Text(field_frame, font=("Segoe UI", 12),
                            bg=self.controller.styles.colors["input_bg"] if self.controller else "#f8f9fa", 
                            fg=self.controller.styles.colors["input_fg"] if self.controller else "#212529",
                            relief="flat", height=4, wrap="word")
            if "placeholder" in kwargs:
                widget.insert("1.0", kwargs["placeholder"])
                widget.config(fg=self.controller.styles.colors["placeholder"] if self.controller else "gray")
                def on_focus_in(event):
                    if widget.get("1.0", "end-1c") == kwargs["placeholder"]:
                        widget.delete("1.0", tk.END)
                        widget.config(fg=self.controller.styles.colors["input_fg"] if self.controller else "#212529")
                def on_focus_out(event):
                    if not widget.get("1.0", "end-1c").strip():
                        widget.insert("1.0", kwargs["placeholder"])
                        widget.config(fg=self.controller.styles.colors["placeholder"] if self.controller else "gray")
                widget.bind("<FocusIn>", on_focus_in)
                widget.bind("<FocusOut>", on_focus_out)
        
        widget.pack(fill="x")
        return widget
    
    def add_buttons(self, parent, cancel_text="Cancel", save_text="Save", 
                    cancel_command=None, save_command=None):
        button_frame = tk.Frame(parent, bg=self.controller.styles.colors["white"] if self.controller else "white")
        button_frame.pack(fill="x", pady=(25, 0))
        
        if cancel_command:
            cancel_btn = tk.Button(button_frame, text=cancel_text,
                                  font=("Segoe UI", 12), bg=self.controller.styles.colors["gray"] if self.controller else "#adb5bd",
                                  fg="white", relief="flat", cursor="hand2",
                                  command=cancel_command,
                                  padx=35, pady=12)
            cancel_btn.pack(side="left", padx=(0, 15))
        
        if save_command:
            save_btn = tk.Button(button_frame, text=save_text,
                                font=("Segoe UI", 12, "bold"), bg=self.controller.styles.colors["primary"] if self.controller else "#4361ee",
                                fg="white", relief="raised", cursor="hand2",
                                command=save_command,
                                padx=35, pady=12)
            save_btn.pack(side="right")
        
        return save_btn if save_command else None
