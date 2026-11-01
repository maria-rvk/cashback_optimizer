from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange

from models import CATEGORIES


class TransactionForm(FlaskForm):
    """Форма добавления траты."""

    store_name = StringField(
        'Место покупки',
        validators=[
            DataRequired(message='Укажите место покупки'),
            Length(max=100, message='Не длиннее 100 символов'),
        ],
    )
    category = SelectField(
        'Категория',
        choices=[(c, c) for c in CATEGORIES],
        validators=[DataRequired()],
    )
    amount = FloatField(
        'Сумма, руб.',
        validators=[
            DataRequired(message='Введите сумму'),
            NumberRange(min=1, max=1_000_000,
                        message='Сумма должна быть от 1 до 1 000 000 руб.'),
        ],
    )
    spent_on = DateField('Дата', default=date.today,
                         validators=[DataRequired()])
    card_id = SelectField('Карта', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить трату')


class CardForm(FlaskForm):
    """Форма добавления карты."""

    name = StringField(
        'Название карты',
        validators=[
            DataRequired(message='Укажите название карты'),
            Length(max=100, message='Не длиннее 100 символов'),
        ],
    )
    default_percent = FloatField(
        'Кэшбэк «на всё остальное», %',
        default=1.0,
        validators=[
            DataRequired(message='Введите процент'),
            NumberRange(min=0, max=15,
                        message='Процент должен быть от 0 до 15'),
        ],
    )
    submit = SubmitField('Добавить карту')


class CashbackRuleForm(FlaskForm):
    """Форма добавления правила кэшбэка для карты."""

    category = SelectField(
        'Категория',
        choices=[(c, c) for c in CATEGORIES],
        validators=[DataRequired()],
    )
    percent = FloatField(
        'Кэшбэк в этой категории, %',
        validators=[
            DataRequired(message='Введите процент'),
            NumberRange(min=0, max=15,
                        message='Процент должен быть от 0 до 15'),
        ],
    )
    submit = SubmitField('Добавить правило')
