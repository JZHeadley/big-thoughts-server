from flask import Flask, redirect, request, render_template
from flask_sockets import Sockets
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from twilio.twiml.messaging_response import MessagingResponse
from twilio import twiml

from thoughtio import init_msg, parse_signature, parsing_failure
from query_logic import in_system, process_msg

from sqlalchemy.orm import synonym
import json

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
    class_num = db.Column(db.Integer, db.ForeignKey('class.class_id'), primary_key = True)
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
        query = Class_TA.query.join(Class, Class_TA.class_num == Class.class_num).filter_by(Class_TA.ta_id = taid)
        return builtin_list(map(from_sql, query.all()))

@app.route('/classes/<classID>', methods=["GET"])
def get_class_members_handler(classID):
        distinct = Message.query.filter_by(class_id == class_id).all()
        query = Class.query.filter_by(user_id in distinct.user_id)
        return builtin_list(map(from_sql, query.all()))

@app.route('/classes/<classID>/<userID>/messages', methods=["GET"])
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

                res = process_msg(student_number, class_number, body)

                if res is not None:
                        send_to_student(student_number, class_number, res)
        elif (student_number, class_number) in waiting_list:
                err = parse_signature(student_number, class_number, body)

                if err is not None:
                        parsing_failure(student_number, class_number)
                else:
                        waiting_list.remove((student_number, class_number)) 
        else:
                init_msg(student_number, class_number)
                waiting_list.append((student_number, class_number))

@app.route('/secret', methods=["GET"])
def secret():
        return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
def catch_all(path):
        return render_template("index.html")

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)

    server.serve_forever()