from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

students = []

def in_system(student_number, class_number):
  for student in students:
    if student[0] == student_number:
      return True

  return False 

def process_msg(student_number, class_number, msg):

  

  return None

def register_student(student_number, class_number, vnumber, firstname, lastname):
  # MY database
  students.append((student_number, class_number, vnumber, firstname, lastname))
