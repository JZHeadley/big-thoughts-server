from flask_sqlalchemy import SQLAlchemy
import json
db = SQLAlchemy()
class Message(db.Model):
    time_stamp = db.Column(db.Date())
    content = db.Column(db.String(512))
    author = db.Column(db.String(10), db.ForeignKey('person.user_id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.class_id'))
    message_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(10), db.ForeignKey('student.student_id'))

class Class(db.Model):
    class_id = db.Column(db.Integer, primary_key = True)
    class_num = db.Column(db.String(30))
    class_name = db.Column(db.String(80))


class TA(db.Model):
    ta_id = db.Column(db.String(10), db.ForeignKey('person.user_id'), primary_key = True)


class Student(db.Model):
    student_id = db.Column(db.String(10), db.ForeignKey('person.user_id'), primary_key = True)
    phone_number = db.Column(db.String(30))


class Class_TA(db.Model):
    ta_id = db.Column(db.String(10), db.ForeignKey('person.user_id'), primary_key = True)
    class_num = db.Column(db.Integer, db.ForeignKey('class.class_id'), primary_key = True)

class Person(db.Model):
    user_id = db.Column(db.String(10), primary_key = True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))



def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data
