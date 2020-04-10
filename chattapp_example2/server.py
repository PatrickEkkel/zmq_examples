import zmq
import time
import sys
import datetime
import threading

server_port = "5556"
publisher_port = "5557"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)


class ZMQPublisher:

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port

    def start(self):
        self.socket.bind("tcp://*:%s" % self.port)

    def publish(self,username, channel_name, messagedata):
        topic = channel_name
        self.socket.send_string(f"{topic} {username}:{messagedata} ")
        print(f"sending update to subscriber: {topic} {messagedata}")

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



class Server:

    def __init__(self, server_port, publisher_port):
        self.server = ZMQServer(server_port)
        self.publisher = ZMQPublisher(publisher_port)
        self.users = {}
        self.channels = {}


    def start(self):
        server_thread = threading.Thread(target=self.server.start,args=(self,))
        server_thread.start()

        self.publisher.start()
        #self.publisher.publish('test','test')
        #while True:
        #    print('running')
        #    time.sleep(1)
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
            worker = threading.Thread(target=self.publisher.publish, args=(username, channel_name, message))
            worker.start()
            #self.publisher.publish(channel_name, message)
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

server = Server(server_port, publisher_port)
server.start()
