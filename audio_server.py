#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
import socket
from threading import Thread
import Queue
import time
import pickle

data_bytes = Queue.Queue()
udp_8000 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_9000 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
CHUNK = 1024
BUFFER = 100
MY_IP = "169.254.185.147"
YOUR_IP = "169.254.238.230"

def acknowledge_client():
    udp_9000.bind(("", 9005))
    udp_8000.sendto(MY_IP, (YOUR_IP, 9000))
    while True:
        data, addr = udp_9000.recvfrom(CHUNK)
        print "2"
        udp_9000.sendto("", (YOUR_IP, 9005))

def set_up_pyaudio(data):
    global FORMAT, CHANNELS, RATE, stream
    response = pickle.loads(data)
    FORMAT = response["format"]
    CHANNELS = response["channels"]
    RATE = response["rate"]
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, output = True)
    send_acks_thread = Thread(target = acknowledge_client)
    send_acks_thread.setDaemon(True)
    send_acks_thread.start()

def accept_data():
    global CHANNELS
    udp_8000.bind(("", 8000))
    data, addr = udp_8000.recvfrom(CHUNK)
    print "here"
    set_up_pyaudio(data)
    i = 0
    while True:
        data, addr = udp_8000.recvfrom(CHUNK*CHANNELS*8)
        data_bytes.put(data)
        #print data
        i += 1
        print i

    udp_8000.close()

def run_music():
    global stream
    while True:
        if data_bytes.qsize() >= BUFFER:
            while data_bytes.qsize() > 0:
                stream.write(data_bytes.get(), CHUNK)

def main():
    run_music_thread = Thread(target = run_music)
    accept_data_thread = Thread(target = accept_data)
    run_music_thread.setDaemon(True)
    accept_data_thread.setDaemon(True)
    run_music_thread.start()
    accept_data_thread.start()

    while True:
        a = 0

if __name__ == "__main__":
    main()

