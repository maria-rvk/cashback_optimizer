from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Категории трат — один общий список для всего приложения
CATEGORIES = [
    'Продукты',
    'Кафе и рестораны',
    'Топливо',
    'Такси',
    'Одежда',
    'Электроника',
    'Здоровье',
    'Развлечения',
    'Прочее',
]


class Card(db.Model):
    """Банковская карта с кэшбэком."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    default_percent = db.Column(db.Float, nullable=False, default=1.0)

    # Связь: у одной карты много правил кэшбэка
    rules = db.relationship('CashbackRule', backref='card',
                            cascade='all, delete-orphan',
                            lazy=True)

    def __repr__(self):
        return f'<Card {self.name}>'


class CashbackRule(db.Model):
    """Правило кэшбэка: сколько процентов карта даёт в одной категории."""

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    percent = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Rule {self.category}: {self.percent}%>'


class Transaction(db.Model):
    """Одна трата пользователя."""

    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    spent_on = db.Column(db.Date, nullable=False, default=date.today)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)

    # Связь: трата знает, какой картой оплачена
    card = db.relationship('Card', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.store_name}: {self.amount} руб.>'
