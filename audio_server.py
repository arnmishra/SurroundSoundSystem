import pyaudio
import socket
from threading import Thread
import Queue
import pickle

CHUNK = 1024
BUFFER = 100

data_bytes = Queue.Queue()
UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def set_up_pyaudio(data, client_ip):
    """ Method to set up the PyAudio streams.

    :param data: the data sent from the master with information about the song format
    :param client_ip: The IP of the client that sen the information
    """
    global CHANNELS, stream
    response = pickle.loads(data)
    FORMAT = response["format"]
    CHANNELS = response["channels"]
    RATE = response["rate"]
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, output = True)
    UDPSock.sendto("Acknowledge", (client_ip, 9000))

def accept_data():
    """ Method to accept data from the client. """
    global CHANNELS
    UDPSock.bind(("", 8000))
    data, addr = UDPSock.recvfrom(CHUNK)
    set_up_pyaudio(data, addr[0])
    i = 0
    while True:
        data, addr = UDPSock.recvfrom(CHUNK*CHANNELS*8)
        data_bytes.put(data)
        i += 1
        print "Received Packet #", i

    UDPSock.close()

def run_music():
    """ Method to play the music once a buffer threshold has been reached. """
    global stream
    while True:
        if data_bytes.qsize() >= BUFFER:
            while data_bytes.qsize() > 0:
                stream.write(data_bytes.get(), CHUNK)

def main():
    """ Main Function to start threads to playing music and accepting data. """
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

