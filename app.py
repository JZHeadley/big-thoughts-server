from flask import Flask
from flask_sockets import Sockets
from flask_cors import CORS
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


@app.route('/')
def hello():
    return 'Hello World!

@app.route('/users/{userID}')
def get_user_by_ID():
        return ""

@app.route('/ta/{taid}/classes')
def populate_data_for_TA():
        return ""

@app.route('/classes/{classID}/members')
def get_class_members():
        return ""

@app.route('/classes/{classID}/{userID}/messages')
def get_message_history():
        return ""

@app.route('/messages/{content, author, classID, userID}')
def post_message():
        return ""


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()