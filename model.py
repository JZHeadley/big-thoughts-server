from flask_sqlalchemy import SQLAlchemy
from app import app
import json

db = SQLAlchemy(app)
class Message(db.Model):
    time_stamp = db.Column(db.Timestamp)
    content = db.Column(db.String(512))
    author = db.Column(db.String(10), db.ForeignKey('person.user_id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.class_id'))
    message_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(10), db.ForeignKey('student.student_id'))

    def __repr__(self):
        return json.dumps({'time_stamp': self.time_stamp, 'content': self.content, 
            'author': self.author, 'class_id': self.class_id, 'message_id': self.message_id,
            'user_id': self.user_id})
class Class(db.Model):
    class_id = db.Column(db.Integer, primary_key)
    class_num = db.Column(db.String(30))
    class_name = db.Column(db.String(80))

    def __repr__(self):
        return json.dumps({'class_id': self.class_id, 'class_num': self.class_num, 
            'class_name': self.class_name})

class TA(db.Model):
    ta_id = db.Column(db.String(10), db.ForeignKey('person.user_id'))

    def __repr__(self):
        return json.dumps({'taid':self.ta_id})

class Student(db.Model):
    student_id = db.Column(db.String(10), db.ForeignKey('person.user_id'))
    phone_number = db.Column(db.String(30))

    def __repr__(self):
        return json.dumps({'student_id': self.student_id, 'phone_number': self.phone_number})

class Class_TA(db.Model):
    ta_id = db.Column(db.String(10), db.ForeignKey('person.user_id'))
    class_num = db.Column(db.Integer, db.ForeignKey('class.class_id'))


