import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')  # рисуем без окна: сервер не имеет экрана
import matplotlib.pyplot as plt

from models import Transaction

# ===== Единый стиль графиков (в тон сайту) =====

ACCENT = '#4f6df5'        # основной синий — как кнопки на сайте
GREEN = '#2fb673'
ORANGE = '#f5a623'
DANGER = '#e04f5f'
PALETTE = ['#4f6df5', '#2fb673', '#f5a623', '#e04f5f', '#8b5cf6', '#14b8a6', '#f472b6']

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#d1d5db',
    'axes.grid': True,
    'grid.color': '#eef0f4',
    'grid.linewidth': 1,
    'axes.spines.top': False,       # без верхней и правой рамок
    'axes.spines.right': False,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelcolor': '#2c3244',
    'xtick.color': '#6b7280',
    'ytick.color': '#6b7280',
    'font.size': 10,
    'savefig.dpi': 150,             # резкость картинок
    'savefig.bbox': 'tight',
})


def _format_money(value):
    """1234567 -> '1 234 567' — суммы с пробелами читаются легче."""
    return f'{value:,.0f}'.replace(',', ' ')


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

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(categories, amounts, color=ACCENT, width=0.6, zorder=3)

    # подписи сумм над столбцами
    for bar, amount in zip(bars, amounts):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(amounts) * 0.01,
                _format_money(amount),
                ha='center', va='bottom',
                fontsize=8, color='#2c3244')

    ax.set_title('Траты по категориям')
    ax.set_ylabel('Сумма, ₽')
    ax.set_ylim(0, max(amounts) * 1.12)   # запас сверху, чтобы подписи не обрезались
    ax.tick_params(axis='x', rotation=30, labelsize=8)
    for label in ax.get_xticklabels():
        label.set_ha('right')

    fig.savefig(os.path.join(img_dir, 'categories.png'))
    plt.close(fig)

    # --- График 2: траты по картам (круговая диаграмма) ---
    card_names = list(by_card.keys())
    card_amounts = list(by_card.values())
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(card_names))]

    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        card_amounts,
        labels=card_names,
        colors=colors,
        autopct='%1.1f%%',
        pctdistance=0.75,
        startangle=90,
        counterclock=False,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},  # белые разделители
        textprops={'fontsize': 9, 'color': '#2c3244'},
    )
    for autotext in autotexts:          # проценты — белым и жирным внутри секторов
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.set_title('Доля карт в общих тратах')

    fig.savefig(os.path.join(img_dir, 'cards.png'))
    plt.close(fig)

    return True
