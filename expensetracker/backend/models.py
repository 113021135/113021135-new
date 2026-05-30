class User:
    def __init__(self, user_id, full_name, email):
        self.id = user_id
        self.full_name = full_name
        self.email = email

class Wallet:
    def __init__(self, wallet_id, user_id, name, currency, balance=0.0, created_at=None):
        self.id = wallet_id
        self.user_id = user_id
        self.name = name
        self.currency = currency
        self.balance = balance
        self.created_at = created_at

class Income:
    def __init__(self, source, amount, category, date, description):
        self.source = source
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

class Expense:
    def __init__(self, category, amount, date, description, payment_method):
        self.category = category
        self.amount = amount
        self.date = date
        self.description = description
        self.payment_method = payment_method

class Budget:
    def __init__(self, budget_id, user_id, wallet_id, category, amount, period, created_at=None):
        self.id = budget_id
        self.user_id = user_id
        self.wallet_id = wallet_id
        self.category = category
        self.amount = amount
        self.period = period  # 'monthly', 'weekly', 'yearly'
        self.created_at = created_at