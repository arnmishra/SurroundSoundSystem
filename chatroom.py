# Save as server.py 
# Message Receiver
import os
from threading import Thread
from socket import *
import pickle
import time

# Arnav's IP: 172.16.126.165
# Kush's IP: 172.16.126.207


SOCKET = None


def server():
    addr = ("", 9000)
    SOCKET.bind(addr)
    #print "Waiting to receive messages..."
    while True:
        (data, addr) = SOCKET.recvfrom(1024)
        response = pickle.loads(data)
        while time.time() < response["time"]:
            continue
        print "Received message: " + response["message"]
        if data == "exit":
            break
    SOCKET.close()
    os._exit(0)

def client():
    addr = ("172.16.126.207", 8000)
    while True:
        message = raw_input()
        current_time = time.time()
        data = {"message": message, "time": current_time+10}
        pickled_data = pickle.dumps(data)
        SOCKET.sendto(pickled_data, addr)
        print data
        while time.time() < data["time"]:
            continue
        print "Sent message: " + data["message"]
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

