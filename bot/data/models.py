import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = db.create_engine('sqlite:///date.db', echo=False)
connection = engine.connect()
session = Session(engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer)
