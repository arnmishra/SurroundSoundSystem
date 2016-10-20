# Save as server.py 
# Message Receiver
import os
from threading import Thread
from socket import *

SOCKET = None


def server():
    addr = ("", 9000)
    SOCKET.bind(addr)
    #print "Waiting to receive messages..."
    while True:
        (data, addr) = SOCKET.recvfrom(1024)
        print "Received message: " + data
        if data == "exit":
            break
    SOCKET.close()
    os._exit(0)

def client():
    addr = ("172.16.126.191", 9000)
    while True:
        data = raw_input()#"Enter message to send or type 'exit': ")
        SOCKET.sendto(data, addr)
        if data == "exit":
            break

UDPSock = socket(AF_INET, SOCK_DGRAM)
SOCKET = UDPSock
server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()
client_thread = Thread(target=client)
client_thread.daemon = True
client_thread.start()
while True:
    a = 0

