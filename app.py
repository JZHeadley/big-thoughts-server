from flask import Flask, redirect, request
from flask_sockets import Sockets
from flask_cors import CORS
from . import  get_model
from flask_sqlalchemy import SQLAlchemy

<<<<<<< HEAD
=======
from thoughtio import init_msg, parse_signature, parsing_failure
from twilio.twiml.messaging_response import MessagingResponse
from twilio import twiml

from query_logic import in_system, process_msg

import json
>>>>>>> 7dde75ac6ff58a3dbe4803ac2773aa8c6ae1bfa4

from .thoughtio import init_msg
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
DEBUG=True
app = Flask(__name__)
sockets = Sockets(app)
CORS(app)

@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)

@sockets.route('/ws')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)


@app.route('/hello')
def hello():
    return 'Hello World!'

@app.route('/users/{userID}', methods=["GET"])
def get_user_by_ID(userID):
        return userID

@app.route('/tas/{taid}/classes', methods=["GET"])
def get_class_list_by_taid_handler(taid):
        query = Session.query(Class_TA, Class).filter(Class_TA.class_num == Class.class_num).filter(Class_TA.ta_id == taid)
        return builtin_list(map(from_sql, query.all()))

@app.route('/ta/{taid}/classes', methods=["GET"])
def populate_data_for_TA_handler(taid):
        return taid

@app.route('/classes/<classID>', methods=["GET"])
def get_class_members_handler(classID):
        distinct = Message.query.filter_by(class_id == class_id).all()
        query = Class.query.filter_by(user_id in distinct.user_id)
        return builtin_list(map(from_sql, query.all()))

@app.route('/classes/{classID}/{userID}/messages', methods=["GET"])
def get_message_history_handler():
        return classID, userID

@app.route('/messages', methods=["POST"])
def post_message_handler():
        return ""

@app.route('/sms', methods=["POST"])
def text_handler():

        student_number = request.form['From']
        class_number = request.form['To']
        message_body = request.form['Body']

        if not student_number or not class_number or not message_body:
                return

        if in_system(student_number, class_numbers):
                process_msg(student_number, class_number, body)
                waiting_list.append((student_number, class_number))
        elif (student_number, class_number) in waiting_list:
                err = parse_signature(student_number, class_number, body)

                if err is not None:
                        parsing_failure(student_number, class_number)
                else:
                        waiting_list.remove((student_number, class_number)) 
        else:
                init_msg(student_number, class_number)

@app.route('/secret', methods=["GET"])
def secret():
        return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()