import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')  # рисуем без окна: сервер не имеет экрана
import matplotlib.pyplot as plt

from models import Transaction


def build_charts():
    """Рисует графики статистики и сохраняет их в static/img.

    Возвращает True, если графики построены, и False,
    если трат пока нет (тогда страница покажет заглушку).
    """
    transactions = Transaction.query.all()
    if not transactions:
        return False

    by_category = defaultdict(float)
    by_card = defaultdict(float)
    for t in transactions:
        by_category[t.category] += t.amount
        by_card[t.card.name] += t.amount

    img_dir = os.path.join(os.path.dirname(__file__), 'static', 'img')
    os.makedirs(img_dir, exist_ok=True)

    # --- График 1: траты по категориям (столбцы) ---
    categories = list(by_category.keys())
    amounts = list(by_category.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(categories, amounts)
    ax.set_title('Траты по категориям')
    ax.set_ylabel('Руб.')
    ax.bar_label(bars, fmt='%.0f')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    fig.savefig(os.path.join(img_dir, 'categories.png'), dpi=120)
    plt.close(fig)

    # --- График 2: траты по картам (круговая диаграмма) ---
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        list(by_card.values()),
        labels=list(by_card.keys()),
        autopct='%1.1f%%',
        startangle=90,
    )
    ax.set_title('Доля карт в общих тратах')
    plt.tight_layout()
    fig.savefig(os.path.join(img_dir, 'cards.png'), dpi=120)
    plt.close(fig)

    return True
