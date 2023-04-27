import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Wallet(SqlAlchemyBase):
    __tablename__ = 'wallet'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    balance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"), unique=True)
    user = orm.relationship('User')