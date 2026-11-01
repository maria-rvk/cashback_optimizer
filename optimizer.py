from models import Card


class CashbackOptimizer:
    """Считает, какой картой выгоднее оплатить покупку."""

    def __init__(self, cards):
        # cards — список объектов Card из базы
        self.cards = cards

    def cashback_for(self, card, category, amount):
        """Сколько кэшбэка даст эта карта за покупку в категории."""
        for rule in card.rules:
            if rule.category == category:
                return amount * rule.percent / 100
        # правила для категории нет — работает базовый процент
        return amount * card.default_percent / 100

    def best_card(self, category, amount):
        """Возвращает тройку: лучшая карта, её кэшбэк, полный рейтинг.

        Рейтинг — список пар (карта, кэшбэк), отсортированный по убыванию.
        """
        if not self.cards:
            return None, 0.0, []

        rating = [
            (card, self.cashback_for(card, category, amount))
            for card in self.cards
        ]
        rating.sort(key=lambda pair: pair[1], reverse=True)
        best_card, best_cashback = rating[0]
        return best_card, best_cashback, rating
