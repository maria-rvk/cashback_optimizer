import time
from collections import defaultdict

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_wtf import CSRFProtect
from charts import build_charts
from forms import CardForm, CashbackRuleForm, TransactionForm
from models import Card, CashbackRule, Transaction, db
from optimizer import CashbackOptimizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashback.db'

csrf = CSRFProtect(app)

db.init_app(app)


# ---------- Красивые суммы ----------

@app.template_filter('money')
def money(value):
    """12345.6 -> '12 345,60' — суммы с пробелами и копейками."""
    return f'{value:,.2f}'.replace(',', ' ').replace('.', ',')


# ---------- Главная страница ----------

@app.route('/')
def index():
    cards = Card.query.all()
    transactions = Transaction.query.all()
    total_spent = sum(t.amount for t in transactions)
    return render_template(
        'index.html',
        cards=cards,
        transactions_count=len(transactions),
        total_spent=total_spent,
    )


# ---------- Карты ----------

@app.route('/cards')
def cards_list():
    cards = Card.query.order_by(Card.name).all()
    return render_template('cards.html', cards=cards)


@app.route('/cards/add', methods=['GET', 'POST'])
def add_card():
    form = CardForm()
    if form.validate_on_submit():
        card = Card(
            name=form.name.data,
            default_percent=form.default_percent.data,
        )
        db.session.add(card)
        db.session.commit()
        flash(f'Карта «{card.name}» добавлена!')
        return redirect(url_for('card_detail', card_id=card.id))
    return render_template('card_form.html', form=form, title='Новая карта')


@app.route('/cards/<int:card_id>', methods=['GET', 'POST'])
def card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    rule_form = CashbackRuleForm()
    if rule_form.validate_on_submit():
        existing = CashbackRule.query.filter_by(
            card_id=card.id,
            category=rule_form.category.data,
        ).first()
        if existing:
            existing.percent = rule_form.percent.data
            flash(f'Правило для «{existing.category}» обновлено.')
        else:
            rule = CashbackRule(
                card_id=card.id,
                category=rule_form.category.data,
                percent=rule_form.percent.data,
            )
            db.session.add(rule)
            flash(f'Правило для «{rule.category}» добавлено.')
        db.session.commit()
        return redirect(url_for('card_detail', card_id=card.id))
    return render_template(
        'card_detail.html',
        card=card,
        rule_form=rule_form,
    )


@app.route('/rules/<int:rule_id>/delete', methods=['POST'])
def delete_rule(rule_id):
    rule = CashbackRule.query.get_or_404(rule_id)
    card_id = rule.card_id
    db.session.delete(rule)
    db.session.commit()
    flash('Правило удалено.')
    return redirect(url_for('card_detail', card_id=card_id))


# ---------- Траты ----------

@app.route('/transactions')
def transactions_list():
    transactions = (
        Transaction.query
        .order_by(Transaction.spent_on.desc(), Transaction.id.desc())
        .all()
    )
    return render_template('transactions.html', transactions=transactions)


@app.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    cards = Card.query.all()
    if not cards:
        flash('Сначала добавьте хотя бы одну карту!')
        return redirect(url_for('add_card'))

    form = TransactionForm()
    form.card_id.choices = [(c.id, c.name) for c in cards]
    if form.validate_on_submit():
        transaction = Transaction(
            store_name=form.store_name.data,
            category=form.category.data,
            amount=form.amount.data,
            spent_on=form.spent_on.data,
            card_id=form.card_id.data,
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Трата добавлена!')
        return redirect(url_for('transactions_list'))
    return render_template(
        'transaction_form.html',
        form=form,
        title='Новая трата',
    )


@app.route('/transactions/<int:tr_id>/edit', methods=['GET', 'POST'])
def edit_transaction(tr_id):
    transaction = Transaction.query.get_or_404(tr_id)
    form = TransactionForm(obj=transaction)
    cards = Card.query.all()
    form.card_id.choices = [(c.id, c.name) for c in cards]

    if form.validate_on_submit():
        transaction.store_name = form.store_name.data
        transaction.category = form.category.data
        transaction.amount = form.amount.data
        transaction.spent_on = form.spent_on.data
        transaction.card_id = form.card_id.data
        db.session.commit()
        flash('Трата обновлена!')
        return redirect(url_for('transactions_list'))
    return render_template(
        'transaction_form.html',
        form=form,
        title='Редактировать трату',
    )


@app.route('/transactions/<int:tr_id>/delete', methods=['POST'])
def delete_transaction(tr_id):
    transaction = Transaction.query.get_or_404(tr_id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Трата удалена.')
    return redirect(url_for('transactions_list'))


# ---------- Статистика ----------

@app.route('/stats')
def stats():
    transactions = Transaction.query.all()
    total_spent = sum(t.amount for t in transactions)

    has_charts = build_charts()   # PNG-картинки (Matplotlib)

    # Разбивка по категориям для таблицы
    by_category = defaultdict(float)
    for t in transactions:
        by_category[t.category] += t.amount
    category_rows = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        'stats.html',
        total_spent=total_spent,
        transactions_count=len(transactions),
        has_charts=has_charts,
        category_rows=category_rows,
        chart_version=int(time.time()),   # сбрасываем кэш картинок
    )


# ---------- Рекомендация: какой картой платить ----------

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    cards = Card.query.all()
    if not cards:
        flash('Сначала добавьте хотя бы одну карту!')
        return redirect(url_for('add_card'))

    form = TransactionForm()
    form.card_id.choices = [(c.id, c.name) for c in cards]
    # поле «карта» в этой форме не нужно — карта выбирается автоматически
    del form.card_id

    recommendation = None
    rating = None

    if form.validate_on_submit():
        optimizer = CashbackOptimizer(cards)
        best_card, best_cashback, rating = optimizer.best_card(
            category=form.category.data,
            amount=form.amount.data,
        )
        recommendation = (best_card, best_cashback)

    return render_template(
        'recommend.html',
        form=form,
        recommendation=recommendation,
        rating=rating,
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
