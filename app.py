from flask import Flask, redirect, request
from flask_sockets import Sockets
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from thoughtio import init_msg, parse_signature, parsing_failure
from twilio.twiml.messaging_response import MessagingResponse
from twilio import twiml

from query_logic import in_system, process_msg

import json

DEBUG=True
app = Flask(__name__)
sockets = Sockets(app)
CORS(app)

db = SQLAlchemy(app)

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

@app.route('/{taid}/classes', methods=["GET"])
def get_class_list_by_taid_handler(taid):
        return getClassListByTaid(taid)

@app.route('/ta/{taid}/classes', methods=["GET"])
def populate_data_for_TA_handler(taid):
        return taid

@app.route('/classes/{classID}/members', methods=["GET"])
def get_class_members_handler(classID):
        return classID

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


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()