import zmq
import time
import sys
import datetime

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)


class ZMQServer:

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)


    def start(self,cls):
        while True:
            print("Waiting for incoming messages..")
            #  Wait for next request from client
            message = self.socket.recv()
            print ("Received request: ", message)
            message_type = message.decode().split(':')[0]
            message_value = message.decode().split(':')[1]
            self.socket.send_string(cls.handle_incoming_message(message_type, message_value))

    def send_string(self, string):
        pass


class Server:

    def __init__(self, port):
        server = ZMQServer(port)
        self.users = {}
        self.channels = {}
        server.start(self)

    def handle_incoming_message(self, type, value):

        if type == 'login':
            self.users[value] = datetime.datetime.now()
            print(f"user {value} logged in")
            return "Ok"
        elif type == 'send_message':
            username = value.split("/")[0]
            channel_name = value.split("/")[1]
            message = value.split("/")[2]
            print(f"user {username} sent message to {channel_name} message: {message}")
            return "Ok"

        elif type == 'create_channel':
            username = value.split(",")[0]
            channel_name = value.split(",")[1]
            if channel_name in self.channels:
                self.channels[channel_name][username] = datetime.datetime.now()
                print(f"user {username} added to existing channel {channel_name}")
            else:
                self.channels[channel_name] = {username: datetime.datetime.now()}
                print(f"user {username} created channel {channel_name}")
            return "Ok"

server = Server(port)
