#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
import socket
from threading import Thread
import Queue
import time
import pickle

data_bites = Queue.Queue()
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
CHUNK = 1024
BUFFER = 10


def acknowledge_client():
    time.sleep(5)
    udp.sendto("Acknowledged", ("127.0.0.1", 9000))

def set_up_pyaudio(data):
    global FORMAT, CHANNELS, RATE, stream
    response = pickle.loads(data)
    FORMAT = response["format"]
    CHANNELS = response["channels"]
    RATE = response["rate"]
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, output = True)
    acknowledge_client()

def accept_data():
    global CHANNELS
    udp.bind(("", 8000))

    data, addr = udp.recvfrom(CHUNK)
    print "here"
    set_up_pyaudio(data)

    while True:
        data, addr = udp.recvfrom(CHUNK*CHANNELS*2)
        data_bites.put(data)

    udp.close()

def run_music():
    global stream
    while True:
        if data_bites.qsize() >= BUFFER:
            while data_bites.qsize() > 0:
                stream.write(data_bites.get(), CHUNK)

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

