from flask_socketio import socketio


def startWS(socketio):
    @socketio.on('message')
    def handle_message(data):
        print('received message: ' + data)
