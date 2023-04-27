from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class MarketForm(FlaskForm):
    product_name = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField("Описание")
    price = IntegerField("Цена")
    value = IntegerField("Количество")
    submit = SubmitField('Применить')