import zmq
import sys
import time
import threading

server_port = "5556"
publisher_port = "5557"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

if len(sys.argv) > 2:
    port1 =  sys.argv[2]
    int(port1)

class ZMQSubscriber:
    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.port = port

    def subscribe(self, channel):
        self.socket.connect ("tcp://localhost:%s" % self.port)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, channel)
        print(f"joined channel: {channel}")
        worker = threading.Thread(target=self.fetch_updates)
        worker.start()
    def fetch_updates(self):
        while True:
            message =  self.socket.recv()
            messagedata = message.decode().split()
            topic = messagedata[0]
            del messagedata[0]
            message_value = " ".join(messagedata)
            print(message_value)
            #print(f"processing message {topic} {message_value}",flush=True)


class ZMQClient:
    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.port = port

    def connect(self):
        print("Connecting to server...")
        self.socket.connect("tcp://localhost:%s" % self.port)

    def send_string(self,string):
        self.socket.send_string(string)
        message = self.socket.recv()
        return message.decode() == "Ok"

    def disconnect(self):
        pass

class Client:

    def __init__(self, server_port, publisher_port):
        self.client = ZMQClient(server_port)
        self.subscriber = ZMQSubscriber(publisher_port)

    def connect(self):
        self.client.connect()

    def login(self, username):
        return self.client.send_string(f"login:{username}")

    def logout(self, username):
        pass

    def join_channel(self, username, channel):
        success = self.client.send_string(f"create_channel:{username},{channel}")
        if success:
            self.subscriber.subscribe(channel)
        return success


    def send_message(self,username, channel, message):
        return self.client.send_string(f"send_message:{username}/{channel}/{message}")


def start_client():

    client = Client(server_port, publisher_port)
    client.connect()

    nickname = input("Nickname?")
    channel_name = None
    client.login(nickname)
    while True:
        command_input = input(">")

        if command_input.startswith("\\"):
            command = command_input.split("\\")[1]
            channel_name = command.split(" ")[1]

            if command.split(" ")[0] == 'join':
                #channel_name = input("channel?")
                if client.join_channel(nickname,channel_name):
                    print(f"succesfully joined channel {channel_name}")
                else:
                    print(" command not recognized")
                    #client.send_message(nickname, command_input)
        else:
            if channel_name is not None:
                client.send_message(nickname, channel_name, command_input)
                sys.stdout.flush()
            else:
                print("not in channel")
start_client()

#zmq_subscriber = ZMQSubscriber(publisher_port)
#zmq_subscriber.subscribe("test")
#print("????")
#while True:
#    print("running")
#    sys.stdout.flush()
#    time.sleep(1)
