from flask import Flask, redirect, request
from flask_sockets import Sockets
from flask_cors import CORS

from thoughtio import init_msg, parse_signature, parsing_failure
from twilio.twiml.messaging_response import MessagingResponse
from twilio import twiml

from query_logic import in_system, process_msg

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


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()