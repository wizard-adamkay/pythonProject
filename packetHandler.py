import socket, pickle
import sys
from _thread import *
from packet import Packet
import time

myHost = '192.168.0.19'
transmitterHost = '192.168.0.18'
receiverHost = '192.168.0.20'
myPortTransmitter = 8000
myPortReceiver = 8003
receiverPort = 8004
transmitterPort = 8001
packetsFromTransmitter = []
lastPacketSentToReceiver = 0
packetsFromReceiver = []
lastPacketSentToTransmitter = 0

def listenToTransmitter():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, myPortTransmitter))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Transmitter Connection:', address)  # Print the connected client address

        while True:
            print("send help")
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print(data_variable.seqNum)
            packetsFromTransmitter.append(data_variable)
            if data_variable.packetType == 2:
                break
        connection.close()
    s.close()


def listenToReceiver():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, myPortReceiver))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Receiver Connection:', address)  # Print the connected client address

        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print(data_variable.seqNum)
            packetsFromReceiver.append(data_variable)
            if data_variable.packetType == 2:
                break
        connection.close()
    s.close()


def sendToTransmitter():
    time.sleep(5)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((transmitterHost, transmitterPort))
    global lastPacketSentToTransmitter
    while 1:
        if len(packetsFromReceiver) > lastPacketSentToTransmitter:
            packet = pickle.dumps(packetsFromReceiver[lastPacketSentToTransmitter])
            s.send(packet)
            lastPacketSentToTransmitter += 1
            continue
        time.sleep(.1)
    s.close()


def sendToReceiver():
    time.sleep(5)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((receiverHost, receiverPort))
    global lastPacketSentToReceiver
    while 1:
        print("in send to receiver")
        if len(packetsFromTransmitter) > lastPacketSentToReceiver:
            packet = pickle.dumps(packetsFromTransmitter[lastPacketSentToReceiver])
            print("packet sent: " + str(lastPacketSentToReceiver))
            lastPacketSentToReceiver += 1
            s.send(packet)
            continue
        time.sleep(.1)
    s.close()


start_new_thread(listenToTransmitter, ())
start_new_thread(listenToReceiver, ())
start_new_thread(sendToTransmitter, ())
start_new_thread(sendToReceiver, ())
while 1:
    time.sleep(1)
