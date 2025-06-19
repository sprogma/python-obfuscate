class Bank:
    def __init__(self, money, percent):
        self.percent = percent
        self.start_money = money
        self.money = money
        self.multiplier = 1.0 + percent / 100.0

    def add_year(self):
        self.money *= self.multiplier

    def add_years(self, n):
        for year in range(n):
            self.add_year()

    def get_profit(self):
        return self.money - self.start_money

    def __repr__(self):
        return f"Bank(${self.money:,}, {self.percent}%)"


bank = Bank(100_000, 7)
bank.add_years(17)
print(bank, bank.get_profit())
