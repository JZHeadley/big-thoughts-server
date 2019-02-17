from flask import Flask, redirect, request, render_template
from flask_sockets import Sockets
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from twilio.rest import Client
import datetime
from twilio.twiml.messaging_response import MessagingResponse
from twilio import twiml

# from thoughtio import init_msg, parse_signature, parsing_failure, send_to_student

from sqlalchemy.orm import synonym
from sqlalchemy import text
import json

classNumber = '+15402355581'
DEBUG=True
app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")

sockets = Sockets(app)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bigthoughtsthoughtsbig@34.73.68.172/bigthoughts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

class Message(db.Model):
    __tablename__ = 'message'
    time_stamp = db.Column(db.Date())
    content = db.Column(db.String(512))
    author = db.Column(db.String(10), db.ForeignKey('person.user_id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.class_id'))
    message_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(10), db.ForeignKey('student.student_id'))
    id = synonym("message_id")

class Class(db.Model):
    __tablename__ = 'class'
    class_id = db.Column(db.Integer, primary_key = True)
    class_num = db.Column(db.String(30))
    class_name = db.Column(db.String(80))
    id = synonym("class_id")


class TA(db.Model):
    __tablename__ = 'ta'
    ta_id = db.Column(db.String(10), db.ForeignKey('person.user_id'), primary_key = True)
    id = synonym("ta_id")


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.String(10), db.ForeignKey('person.user_id'), primary_key = True)
    phone_number = db.Column(db.String(30))
    id = synonym("student_id")


class Class_TA(db.Model):
    __tablename__ = 'class_ta'
    ta_id = db.Column(db.String(10), db.ForeignKey('person.user_id'), primary_key = True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.class_id'), primary_key = True)
    id = synonym("ta_id")

class Person(db.Model):
    __tablename__ = 'person'
    user_id = db.Column('user_id', db.String(10), primary_key = True)
    first_name = db.Column('first_name', db.String(30))
    last_name = db.Column('last_name', db.String(30))
    id = synonym("user_id")
    def toJSON(self):
            return json.dumps({'user_id': self.user_id, 'first_name': self.first_name, 'last_name': self.last_name})



def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


@sockets.route('/ws')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)


@app.route('/users/<userID>', methods=["GET"])
def get_user_by_ID(userID):
        user = Person.query.get(userID)
        print(user)
        return user.toJSON()

@app.route('/tas/<taid>/classes', methods=["GET"])
def get_class_list_by_taid_handler(taid):
        # query = Class_TA.query.join(Class, Class_TA.class_num == Class.class_num).filter_by(Class_TA.ta_id == taid)
        query = 'select * from class where class_id IN (select class_id FROM class_ta where ta_id=\'' + taid + '\')'
        res = db.engine.execute(text(query))
        classes = []
        for row in res:
                classes.append({
                        'classId': row[0],
                        'classNum': row[1],
                        'className': row[2]
                })
        print(classes)
        return json.dumps(classes)

@app.route('/classes/<classID>/students', methods=["GET"])
def get_class_members_handler(classID):
        query = 'select p.first_name, p.last_name, s.phone_number, p.user_id from person as p join student as s on p.user_id = s.student_id where p.user_id in (select user_id from message where class_id = \'' + classID + '\')'
        res = db.engine.execute(text(query))
        classes = []
        for row in res:
                print(row)
                classes.append({
                        'studentId': row[3],
                        'firstName': row[0],
                        'lastName': row[1],
                        'phoneNumber': row[2]
                })
        print(classes)
        return json.dumps(classes)
        



@app.route('/classes/<classID>/<userID>/messages', methods=["GET"])
def get_message_history_handler(classID, userID):
        query = 'select * from message where class_id = ' + classID + ' and user_id = \'' + userID + '\''
        name_query = 'select concat( first_name, \' \' , last_name) as full_name from person where user_id = \'' + userID + '\''
        res = db.engine.execute(text(query))
        name = db.engine.execute(text(name_query))
        fullname = ""
        for val in name:
                print(val)
                fullname += val[0]
        classes = []
        for row in res:
                print(row)
                classes.append({
                        'timeStamp': str(row[0]),
                        'content': row[1],
                        'author': fullname,
                        'classID': row[3],
                        'messageID': row[4],
                        'userID': row[5]
                })
        print(classes)
        return json.dumps(classes)

@app.route('/messages', methods=["POST"])
def post_message_handler():
        global classNumber
        json = request.json
        class_name = json['classId']
        student_number = json['studentNumber']
        send_to_student(json['phoneNumber'],classNumber, json['message'])
        return ""

def in_system(student_number, class_number):
        query = 'select * from student where phone_number=\'' +student_number+'\''
        res = db.engine.execute(text(query))
        for row in res:
                print(row)
                return True
        return False

waiting_list=[]
@app.route('/sms', methods=["GET","POST"])
def text_handler():
        student_number = request.form['From']
        class_number = request.form['To']
        message_body = request.form['Body']
        print(request.form)

        if in_system(student_number, class_number):
                res = process_msg(student_number, class_number, message_body)
                if res is not None:
                        send_to_student(student_number, class_number, res)
        elif (student_number, class_number) in waiting_list:
                err = parse_signature(student_number, class_number, message_body)
                print(err)
                if err is True:
                        parsing_failure(student_number, class_number)
                else:
                        waiting_list.remove((student_number, class_number)) 
        else:
                init_msg(student_number, class_number)
                waiting_list.append((student_number, class_number))
        return "accepted"

@app.route('/secret', methods=["GET"])
def secret():
        return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
def catch_all(path):
        return render_template("index.html")

def process_msg(student_number, class_number, msg):
        # sid = Student.query(phone_number=student_number).first().student_id
        query = 'select student_id from student where phone_number=\'' +student_number+'\''
        res = db.engine.execute(text(query))
        sid = None

        for row in res:
                print(row[0])
                sid = row[0]
        query = 'select class_id from class where class_num=\'' +class_number+'\''
        res = db.engine.execute(text(query))
        cid = None
        for row in res:
                print(row[0])
                cid = row[0]
        mesg = {
          'time_stamp': datetime.datetime,
          'content': msg,
          'author': sid,
          'class_id': cid,
          'message_id': None,
          'user_id': sid
        }
        mess = Message(**mesg)
        db.session.add(mess)
        db.session.commit()
        return None

sid = os.getenv("TWILIO_SID")
token = os.getenv("TWILIO_TOKEN")
client = Client(sid, token)

#######################################################
###### CLASS NUMBER: (540) 486-2896 ###################
#######################################################

# List of tuples git
# Tuples are arranged like so
# (FromNumber, ToNumber)
waiting_list = []

def init_msg(student_number, class_number):
    send_to_student(student_number, class_number, "Welcome to BigThoughts! Please send your V# and Full Name so we can get you in the system first :)",)

def register_student(from_number, to_number, body, studentId,firstName,lastName):
        query = 'select class_id from class where class_num=\'' +to_number+'\''
        res = db.engine.execute(text(query))
        cid = None

        for row in res:
                print(row[0])
                cid = row[0]
        print(cid)
        query = 'insert into person(user_id,first_name,last_name) values(\''+studentId+'\',\''+firstName+'\',\''+lastName+'\')'
        res = db.engine.execute(text(query))
        query = 'insert into student(student_id,phone_number) values(\''+studentId+'\',\''+from_number+'\')'
        res = db.engine.execute(text(query))
        mesg = {
          'time_stamp': str((datetime.datetime.now())),
          'content': body,
          'author': studentId,
          'class_id': cid,
          'message_id': None,
          'user_id': studentId
        }
        mess = Message(**mesg)
        db.session.add(mess)
        db.session.commit()

def parse_signature(from_number, to_number, body):
    personal_info = body.split(' ')

    # It's gotta be three things
    if len(personal_info) != 3:
        return True
    
    # It's gotta start with a V
    if personal_info[0][0] not in ["V", "v"]:
        return True

    #############################
    # Send into to the database 
    #############################
    register_student(from_number, to_number, personal_info, personal_info[0],personal_info[1],personal_info[2])

    return False

def parsing_failure(student_number, class_number, body):
    msg = "We were unable to understand your message: " + body
    send_to_student(student_number, class_number, msg)

def send_to_student(student_number, class_number, msg):
    message = client.messages \
                .create(
                    body=msg,
                    from_=class_number,
                    to=student_number
                
                )


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()