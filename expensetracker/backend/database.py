import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from .models import User, Wallet, Income, Expense, Budget


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('expense_tracker.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
        self.cleanup_database_data()
    
    def init_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Wallets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                balance REAL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_default INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Income table (now includes wallet_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                wallet_id TEXT,
                source TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0.00,
                category TEXT DEFAULT 'Uncategorized',
                date DATE NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (wallet_id) REFERENCES wallets (id)
            )
        ''')
        
        # Expenses table (now includes wallet_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                wallet_id TEXT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (wallet_id) REFERENCES wallets (id)
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon TEXT,
                color TEXT
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                wallet_id TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Overall',
                amount REAL NOT NULL,
                period TEXT DEFAULT 'monthly',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (wallet_id) REFERENCES wallets (id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT DEFAULT 'light',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('Shopping', '🛍️', '#4361ee'),
            ('Travel', '✈️', '#f72585'),
            ('Food', '🍕', '#4cc9f0'),
            ('Bills', '💡', '#f8961e'),
            ('Transport', '🚗', '#7209b7'),
            ('Healthcare', '🏥', '#06d6a0'),
            ('Entertainment', '🎬', '#ffd166'),
            ('Education', '📚', '#118ab2'),
            ('Loan', '🏦', '#ef476f'),
            ('Salary', '💰', '#06d6a0'),
            ('Investment', '📈', '#7209b7'),
            ('Freelance', '💼', '#ffd166'),
            ('Gift', '🎁', '#ff6b6b'),
            ('Rent', '🏠', '#4ecdc4'),
            ('Utilities', '⚡', '#45b7d1'),
            ('Insurance', '🛡️', '#96ceb4'),
            ('Tax', '💰', '#ffeaa7')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO categories (name, icon, color) 
            VALUES (?, ?, ?)
        ''', default_categories)
        
        # Create demo user if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO users (full_name, email, password_hash)
            VALUES ('Mike William', 'demo@example.com', ?)
        ''', (hashlib.sha256('password123'.encode()).hexdigest(),))
        
        # Create default wallet for demo user
        cursor.execute('SELECT id FROM users WHERE email = ?', ("demo@example.com",))
        user = cursor.fetchone()
        if user:
            user_id = user[0]
            cursor.execute('SELECT COUNT(*) FROM wallets WHERE user_id = ?', (user_id,))
            if cursor.fetchone()[0] == 0:
                wallet_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO wallets (id, user_id, name, currency, is_default)
                    VALUES (?, ?, 'Main Wallet', 'USD', 1)
                ''', (wallet_id, user_id))
        
        self.conn.commit()

    # Add this method to Database class
    def get_available_years(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT strftime('%Y', date) as year 
            FROM (
                SELECT date FROM income WHERE user_id = ? AND wallet_id = ?
                UNION 
                SELECT date FROM expenses WHERE user_id = ? AND wallet_id = ?
            )
            ORDER BY year DESC
        ''', (user_id, wallet_id, user_id, wallet_id))
        
        years = [row[0] for row in cursor.fetchall()]
        
        if not years:
            years = [str(datetime.now().year)]
        
        return years
    
    def cleanup_database_data(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE income SET 
                source = TRIM(COALESCE(source, 'Unknown')),
                category = CASE 
                    WHEN TRIM(COALESCE(category, '')) = '' THEN 'Uncategorized'
                    ELSE TRIM(category)
                END,
                description = TRIM(COALESCE(description, ''))
            WHERE source IS NOT NULL OR category IS NOT NULL OR description IS NOT NULL
        ''')
        
        cursor.execute('''
            UPDATE expenses SET 
                category = TRIM(COALESCE(category, 'Other')),
                description = TRIM(COALESCE(description, '')),
                payment_method = TRIM(COALESCE(payment_method, 'Unknown'))
        ''')
        
        cursor.execute('''
            DELETE FROM income 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM income 
                GROUP BY user_id, source, amount, date, category, description
            )
        ''')
        
        self.conn.commit()  # Fixed: Changed self.commit() to self.conn.commit()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user and self.hash_password(password) == user[3]:
            cursor.execute("SELECT theme FROM user_preferences WHERE user_id = ?", (user[0],))
            pref = cursor.fetchone()
            theme = pref[0] if pref else 'light'
            
            return {
                "id": user[0],
                "full_name": user[1],
                "email": user[2],
                "theme": theme
            }
        return None
    
    def get_user_theme(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT theme FROM user_preferences WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'light'
    
    def update_user_theme(self, user_id, theme):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, theme)
            VALUES (?, ?)
        ''', (user_id, theme))
        self.conn.commit()
    
    def get_demo_user(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", ("demo@example.com",))
        user = cursor.fetchone()
        if user:
            cursor.execute("SELECT theme FROM user_preferences WHERE user_id = ?", (user[0],))
            pref = cursor.fetchone()
            theme = pref[0] if pref else 'light'
            
            return {
                "id": user[0],
                "full_name": user[1],
                "email": user[2],
                "theme": theme
            }
        return None
    
    def register_user(self, name, email, password):
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Email already registered"
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
        ''', (name, email, password_hash))
        
        user_id = cursor.lastrowid
        wallet_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO wallets (id, user_id, name, currency, is_default)
            VALUES (?, ?, 'Main Wallet', 'USD', 1)
        ''', (wallet_id, user_id))
        
        cursor.execute('''
            INSERT INTO user_preferences (user_id, theme)
            VALUES (?, ?)
        ''', (user_id, 'light'))
        
        self.conn.commit()
        return True, "Account created successfully"
    
    # Wallet methods
    def create_wallet(self, user_id, name, currency):
        cursor = self.conn.cursor()
        wallet_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO wallets (id, user_id, name, currency, balance)
            VALUES (?, ?, ?, ?, 0.00)
        ''', (wallet_id, user_id, name, currency))
        
        self.conn.commit()
        return wallet_id
    
    def update_wallet(self, wallet_id, name, currency):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE wallets SET name = ?, currency = ?
            WHERE id = ?
        ''', (name, currency, wallet_id))
        
        self.conn.commit()
        return True
    
    def get_wallets(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, currency, balance, created_at, is_default
            FROM wallets 
            WHERE user_id = ?
            ORDER BY is_default DESC, created_at DESC
        ''', (user_id,))
        
        wallets = []
        for row in cursor.fetchall():
            wallets.append({
                "id": row[0],
                "name": row[1],
                "currency": row[2],
                "balance": float(row[3]),
                "created_at": row[4],
                "is_default": bool(row[5])
            })
        return wallets
    
    def get_wallet(self, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, currency, balance, user_id, is_default
            FROM wallets 
            WHERE id = ?
        ''', (wallet_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "currency": row[2],
                "balance": float(row[3]),
                "user_id": row[4],
                "is_default": bool(row[5])
            }
        return None
    
    def update_wallet_balance(self, wallet_id):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM income WHERE wallet_id = ?', (wallet_id,))
        total_income = float(cursor.fetchone()[0])
        
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE wallet_id = ?', (wallet_id,))
        total_expenses = float(cursor.fetchone()[0])
        
        new_balance = total_income - total_expenses
        cursor.execute('UPDATE wallets SET balance = ? WHERE id = ?', (new_balance, wallet_id))
        
        self.conn.commit()
        return new_balance
    
    def set_default_wallet(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        
        cursor.execute('UPDATE wallets SET is_default = 0 WHERE user_id = ?', (user_id,))
        cursor.execute('UPDATE wallets SET is_default = 1 WHERE id = ? AND user_id = ?', (wallet_id, user_id))
        
        self.conn.commit()
        return True
    
    def delete_wallet(self, wallet_id, user_id):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM wallets WHERE user_id = ?', (user_id,))
        wallet_count = cursor.fetchone()[0]
        
        if wallet_count <= 1:
            return False, "Cannot delete the only wallet. Create another wallet first."
        
        cursor.execute('SELECT is_default FROM wallets WHERE id = ?', (wallet_id,))
        is_default = cursor.fetchone()[0]
        
        cursor.execute('DELETE FROM income WHERE wallet_id = ?', (wallet_id,))
        cursor.execute('DELETE FROM expenses WHERE wallet_id = ?', (wallet_id,))
        cursor.execute('DELETE FROM budgets WHERE wallet_id = ?', (wallet_id,))
        
        cursor.execute('DELETE FROM wallets WHERE id = ? AND user_id = ?', (wallet_id, user_id))
        
        if is_default:
            cursor.execute('SELECT id FROM wallets WHERE user_id = ? LIMIT 1', (user_id,))
            new_default = cursor.fetchone()
            if new_default:
                cursor.execute('UPDATE wallets SET is_default = 1 WHERE id = ?', (new_default[0],))
        
        self.conn.commit()
        return True, "Wallet deleted successfully"
    
    # Budget methods
    def create_budget(self, user_id, wallet_id, amount, category='Overall', period='monthly'):
        cursor = self.conn.cursor()
        budget_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO budgets (id, user_id, wallet_id, category, amount, period)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (budget_id, user_id, wallet_id, category, amount, period))
        
        self.conn.commit()
        return budget_id
    
    def update_budget(self, budget_id, amount, category='Overall', period='monthly'):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE budgets SET category = ?, amount = ?, period = ?
            WHERE id = ?
        ''', (category, amount, period, budget_id))
        
        self.conn.commit()
        return True
    
    def get_budgets(self, user_id, wallet_id=None):
        cursor = self.conn.cursor()
        
        if wallet_id:
            cursor.execute('''
                SELECT id, wallet_id, category, amount, period, created_at
                FROM budgets 
                WHERE user_id = ? AND wallet_id = ?
                ORDER BY created_at DESC
            ''', (user_id, wallet_id))
        else:
            cursor.execute('''
                SELECT id, wallet_id, category, amount, period, created_at
                FROM budgets 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        budgets = []
        for row in cursor.fetchall():
            budgets.append({
                "id": row[0],
                "wallet_id": row[1],
                "category": row[2],
                "amount": float(row[3]),
                "period": row[4],
                "created_at": row[5]
            })
        return budgets
    
    def get_budget(self, budget_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, user_id, wallet_id, category, amount, period
            FROM budgets 
            WHERE id = ?
        ''', (budget_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "wallet_id": row[2],
                "category": row[3],
                "amount": float(row[4]),
                "period": row[5]
            }
        return None
    
    def delete_budget(self, budget_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM budgets WHERE id = ? AND user_id = ?', (budget_id, user_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_current_month_expenses_by_category(self, user_id, wallet_id, category='Overall'):
        cursor = self.conn.cursor()
        current_month = datetime.now().strftime('%Y-%m')
        
        if category == 'Overall':
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM expenses 
                WHERE user_id = ? AND wallet_id = ? AND strftime('%Y-%m', date) = ?
            ''', (user_id, wallet_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM expenses 
                WHERE user_id = ? AND wallet_id = ? AND category = ? AND strftime('%Y-%m', date) = ?
            ''', (user_id, wallet_id, category, current_month))
        
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def get_current_month_total_expenses(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        current_month = datetime.now().strftime('%Y-%m')
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM expenses 
            WHERE user_id = ? AND wallet_id = ? AND strftime('%Y-%m', date) = ?
        ''', (user_id, wallet_id, current_month))
        
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    # Updated methods with wallet_id parameter
    def save_income(self, user_id, wallet_id, source, amount, category, date, description):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO income (user_id, wallet_id, source, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, source, amount, category, date, description))
        
        new_balance = self.update_wallet_balance(wallet_id)
        self.conn.commit()
        return cursor.lastrowid, new_balance
    
    def save_expense(self, user_id, wallet_id, category, amount, date, payment_method, description):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, wallet_id, category, amount, date, description, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, category, amount, date, description, payment_method))
        
        new_balance = self.update_wallet_balance(wallet_id)
        self.conn.commit()
        return cursor.lastrowid, new_balance
    
    def delete_income(self, income_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT wallet_id FROM income WHERE id = ? AND user_id = ?", (income_id, user_id))
        wallet_info = cursor.fetchone()
        
        if not wallet_info:
            return False
        
        wallet_id = wallet_info[0]
        cursor.execute("DELETE FROM income WHERE id = ? AND user_id = ?", (income_id, user_id))
        
        self.update_wallet_balance(wallet_id)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_expense(self, expense_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT wallet_id FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        wallet_info = cursor.fetchone()
        
        if not wallet_info:
            return False
        
        wallet_id = wallet_info[0]
        cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        
        self.update_wallet_balance(wallet_id)
        self.conn.commit()
        return cursor.rowcount > 0
    
    # All methods now require wallet_id parameter
    def get_total_income(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM income 
            WHERE user_id = ? AND wallet_id = ?
        ''', (user_id, wallet_id))
        return float(cursor.fetchone()[0])
    
    def get_total_expenses(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM expenses 
            WHERE user_id = ? AND wallet_id = ?
        ''', (user_id, wallet_id))
        return float(cursor.fetchone()[0])
    
    def get_wallet_balance(self, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT balance FROM wallets WHERE id = ?', (wallet_id,))
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0
    
    def get_all_income(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, source, amount, date, category, description
            FROM income 
            WHERE user_id = ? AND wallet_id = ?
            ORDER BY date DESC, id DESC
        ''', (user_id, wallet_id))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_expenses(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, category, amount, date, description, payment_method
            FROM expenses 
            WHERE user_id = ? AND wallet_id = ?
            ORDER BY date DESC, id DESC
        ''', (user_id, wallet_id))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_transactions(self, user_id, wallet_id, limit=5):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT source as description, amount, date, 'income' as type
            FROM income 
            WHERE user_id = ? AND wallet_id = ?
            ORDER BY date DESC, id DESC
            LIMIT ?
        ''', (user_id, wallet_id, limit))
        income = cursor.fetchall()
        
        cursor.execute('''
            SELECT category as description, amount, date, 'expense' as type
            FROM expenses 
            WHERE user_id = ? AND wallet_id = ?
            ORDER BY date DESC, id DESC
            LIMIT ?
        ''', (user_id, wallet_id, limit))
        expenses = cursor.fetchall()
        
        all_transactions = []
        for inc in income:
            all_transactions.append(dict(inc))
        for exp in expenses:
            all_transactions.append(dict(exp))
        
        all_transactions.sort(key=lambda x: x['date'], reverse=True)
        return all_transactions[:limit]
    
    def get_monthly_income(self, user_id, wallet_id):
        current_month = datetime.now().strftime('%Y-%m')
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM income 
            WHERE user_id = ? AND wallet_id = ? AND strftime('%Y-%m', date) = ?
        ''', (user_id, wallet_id, current_month))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def get_monthly_expense(self, user_id, wallet_id):
        current_month = datetime.now().strftime('%Y-%m')
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM expenses 
            WHERE user_id = ? AND wallet_id = ? AND strftime('%Y-%m', date) = ?
        ''', (user_id, wallet_id, current_month))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    def get_last_30_days_expenses(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        thirty_days_ago = (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT date, COALESCE(SUM(amount), 0) as daily_total
            FROM expenses 
            WHERE user_id = ? AND wallet_id = ? AND date >= ?
            GROUP BY date
        ''', (user_id, wallet_id, thirty_days_ago))
        
        rows = cursor.fetchall()
        expenses_data = {}
        
        for i in range(30):
            day = (datetime.now() - timedelta(days=29 - i)).strftime('%Y-%m-%d')
            expenses_data[day] = 0
        
        for row in rows:
            date_str = row[0]
            amount = float(row[1])
            if date_str in expenses_data:
                expenses_data[date_str] = amount
        
        return expenses_data
    
    def get_expense_by_category(self, user_id, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT category, COALESCE(SUM(amount), 0) as total
            FROM expenses 
            WHERE user_id = ? AND wallet_id = ?
            GROUP BY category
            ORDER BY total DESC
            LIMIT 6
        ''', (user_id, wallet_id))
        
        rows = cursor.fetchall()
        category_data = {}
        for row in rows:
            category_data[row[0]] = float(row[1])
        
        return category_data
    
    # Replace the existing get_monthly_summary method
    def get_monthly_summary(self, user_id, wallet_id, year=None):
        cursor = self.conn.cursor()
        
        if year is None:
            year = datetime.now().year
        
        months = []
        for month_num in range(1, 13):
            months.append(f"{year}-{month_num:02d}")
        
        monthly_data = []
        for month in months:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM income 
                WHERE user_id = ? AND wallet_id = ? AND strftime('%Y-%m', date) = ?
            ''', (user_id, wallet_id, month))
            income = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM expenses 
                WHERE user_id = ? AND wallet_id = ? AND strftime('%Y-%m', date) = ?
            ''', (user_id, wallet_id, month))
            expenses = cursor.fetchone()[0] or 0
            
            monthly_data.append({
                'month': month,
                'income': float(income),
                'expenses': float(expenses)
            })
        
        return monthly_data
    
    def close(self):
        if self.conn:
            self.conn.close()
