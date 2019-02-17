from flask_sqlalchemy import SQLAlchemy
import model
from model import db
from sqlalchemy.sql import text

def getClassListByTaid(taid):
    res = db.make_session().execute(""" select class.class_num, class.class_name, class.class_id from class_ta join class on class_ta.class_id = class.class_id where class_ta.ta_id = :taid""", taid).fetchall()
    return res
