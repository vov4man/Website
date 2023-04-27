from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CartForm(FlaskForm):
    value = IntegerField("Количество")
    submit = SubmitField('Добавить в корзину')
    change = SubmitField('Изменить')
