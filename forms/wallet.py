from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import SubmitField


class WalletForm(FlaskForm):
    value = IntegerField("Количество")
    submit = SubmitField('Пополнить')
