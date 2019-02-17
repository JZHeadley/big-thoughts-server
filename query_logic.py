from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
#import model
from sqlalchemy.sql import text


def getClassListByTaid(taid):
    return res