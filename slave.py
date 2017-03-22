import pyaudio
from socket import *
from threading import Thread
import Queue
import pickle
import os,psutil

CHUNK = 1024
BUFFER = 12

data_bytes = Queue.Queue() # Queue of song data chunks to play
data_sock = socket(AF_INET, SOCK_DGRAM) # UDP Socket for receiving audio data
heartbeat_sock = socket(AF_INET, SOCK_DGRAM) # UDP Socket for managing heartbeats
process_data = psutil.Process(os.getpid())

def start_thread(method_name, arguments):
    """ Method to start new daemon threads.

    :args method_name: Name of method to start a thread of
    :args arguments: Arguments to pass into new thread
    """
    thread = Thread(target=method_name, args=arguments)
    thread.daemon = True
    thread.start()

def set_up_pyaudio(data, master_ip):
    """ Method to set up the PyAudio streams.

    :param data: the data sent from the master with information about the song format
    :param master_ip: The IP of the master that sen the information
    """
    global CHANNELS, stream
    response = pickle.loads(data)
    FORMAT = response["format"]
    CHANNELS = response["channels"]
    RATE = response["rate"]
    p = pyaudio.PyAudio()
    print "Received Set-Up Information."
    stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, output = True)
    data_sock.sendto("Acknowledge", (master_ip, 8010))

def accept_data():
    """ Method to accept data from the master. """
    global CHANNELS, stream
    data_sock.bind(("", 8000))
    data, addr = data_sock.recvfrom(CHUNK)
    set_up_pyaudio(data, addr[0])
    i = 0
    while True:
        data, addr = data_sock.recvfrom(CHUNK*CHANNELS*8)
        try:
            response = pickle.loads(data[0:CHUNK])
            print 'Finished song'
            i = 0
            p = pyaudio.PyAudio()
            stream = p.open(format = response["format"], channels = response["channels"], rate = response["rate"], output = True)
            data_sock.sendto("Acknowledge", (addr[0], 8010))
            continue
        except:
            pass
        data_bytes.put(data)
        i += 1
        #print "Received Packet #", i

    data_sock.close()

def run_music():
    """ Method to play the music once a buffer threshold has been reached. """
    global stream
    while True:
        if data_bytes.qsize() >= BUFFER:
            while data_bytes.qsize() > 0:
                stream.write(data_bytes.get(), CHUNK)

def heartbeats():
    """ Function to receive and send heartbeats to the master. """
    heartbeat_sock.bind(("", 9000))
    while True:
        (data, addr) = heartbeat_sock.recvfrom(1024)
        heartbeat_sock.sendto("Acknowledge Heartbeat", (addr[0], 9010))

def main():
    """ Main Function to start threads to playing music and accepting data. """
    print process_data.cpu_times()
    start_thread(run_music, ())
    start_thread(accept_data, ())
    start_thread(heartbeats, ())
    print "Waiting to receive music from master..."
    
    while True:
        a = 0

if __name__ == "__main__":
    main()
