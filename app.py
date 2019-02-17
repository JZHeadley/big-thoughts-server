from flask import Flask
from flask_sockets import Sockets
from flask_cors import CORS

from thoughtio import init_msg

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

        # Parse the twilio body

        if inSystem(from_number, To_numbers):
                process_msg(from_number, to_number, body)
                waiting_list.append((from_number, to_number))
        elif (from_number, to_number) in waiting_list:
                err = parse_signature(from_number, to_number, body)

                if err is not None:
                        parsing_failure(from_number, to_number)
                else:
                        waiting_list.remove((from_number, to_number)) 
        else:
                init_msg(from_number, to_number)


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()