import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Market(SqlAlchemyBase):
    __tablename__ = 'market'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    product_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    value = sqlalchemy.Column(sqlalchemy.String, nullable=True)