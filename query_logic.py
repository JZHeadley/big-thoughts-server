from flask_sqlalchemy import SQLAlchemy
import model
from model import db
from sqlalchemy.sql import text

students = []

def getClassListByTaid(taid):
  res = db.make_session().execute(""" select class.class_num, class.class_name, class.class_id from class_ta join class on class_ta.class_id = class.class_id where class_ta.ta_id = :taid""", taid).fetchall()
  return res

def in_system(student_number, class_number):
  for student in students:
    if student[0] == student_number:
      return True

  return False 

def process_msg(student_number, class_number, msg):
  return

def register_student(student_number, class_number, vnumber, firstname, lastname):
  # Because I'm tired of waiting
  students.append((student_number, class_number, vnumber, firstname, lastname))