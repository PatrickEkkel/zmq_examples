import zmq
import sys

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

if len(sys.argv) > 2:
    port1 =  sys.argv[2]
    int(port1)

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
        return str(message) == "Ok"

    def disconnect(self):
        pass

class Client:

    def __init__(self, port):
        self.zmq = ZMQClient(port)

    def connect(self):
        self.zmq.connect()

    def login(self, username):
        return self.zmq.send_string(f"login:{username}")

    def logout(self, username):
        pass

    def join_channel(self, username, channel):
        return self.zmq.send_string(f"create_channel:{username},{channel}")

    def send_message(self,username, channel, message):
        return self.zmq.send_string(f"send_message:{username}/{channel}/{message}")

#if len(sys.argv) > 2:
#    socket.connect ("tcp://localhost:%s" % port1)

client = Client(port)

client.connect()

client.join_channel('patrick','mychannel')
client.send_message('patrick','mychannel','even kijken of het werkt')

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
        else:
            print("not in channel")
