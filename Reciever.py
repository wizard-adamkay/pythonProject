import socket, pickle
from packet import Packet
import time
from _thread import *
import sys
nextAck = None
packetList = []


# setup server to receive acks
def receive():
    global nextAck
    myHost = ''
    transmitterPort = 8004
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, transmitterPort))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Client Connection:', address)  # Print the connected client address
        start_new_thread(sendToRelay(), ())
        print("got here")
        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print("received ack: " + str(data_variable.ackNum) + "\n", end='')
            packetList.append(data_variable)
            nextAck = data_variable
            if data_variable.packetType == 2:
                break
        connection.close()
    s.close()


def sendToRelay():
    global nextAck
    relayRecievePort = 8003
    relayHost = '192.168.0.19'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((relayHost, relayRecievePort))
    while 1:
        if nextAck != None:
            packet = pickle.dumps(nextAck)
            s.send(packet)
            nextAck = None
        time.sleep(1)
    s.close()


start_new_thread(receive, ())

done = False
while not done:
    time.sleep(1)
print('Data Sent to Server')
