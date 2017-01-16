import pyaudio
from socket import *
import wave
import Queue
from threading import Thread
import pickle
import time
import sys

CHUNK = 1024
BUFFER = 100
MY_IP = "localhost"
IPS = sys.argv[1:]
num_clients = len(IPS)

UDPSock = socket(AF_INET, SOCK_DGRAM)
data_bytes = Queue.Queue()
clients = {}

def server():
    """ Server thread to get all ToF data and start playing client side music and sending data. """

    global start_time

    UDPSock.bind((MY_IP, 9000))
    max_delay = -1

    for i in range(num_clients):
        (data, addr) = UDPSock.recvfrom(1024)
        client_ip = addr[0]
        rec_time = time.time()
        rtt_time = rec_time - start_time
        time_of_flight = rtt_time/2.0
        if time_of_flight > max_delay:
            max_delay = time_of_flight
        clients[client_ip] = time_of_flight
        print "Client #", i, "Connected"

    my_player_thread = Thread(target=player_thread, args = (max_delay,))
    my_player_thread.daemon = True
    my_player_thread.start()

    send_song_no_thread(max_delay)
    # send_song_threaded(clients, max_delay)

def send_song_no_thread(rtt_delay):
    """ Send song chunks to each client in a single thread. """

    wf = wave.open("song.wav", 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        time.sleep(rtt_delay) # Live Stream Affect
        for ip in IPS:
            UDPSock.sendto(data, (ip, 8000))
        data_bytes.put(data)
        i += 1
        print "Sent Packet #", i
        data = wf.readframes(CHUNK)

def send_song_threaded(clients, max_delay):
    """ Send song chunks to each client in a separate thread. """

    wf = wave.open("song.wav", 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        time.sleep(rtt_delay) # Live Stream Affect
        for client_ip in clients:
            server_thread = Thread(target=server_transmission, args = (client_ip, clients[client_ip], data, max_delay))
            server_thread.daemon = True
            server_thread.start()
        data_bytes.put(data)
        i += 1
        print "Sent Packet #", i
        data = wf.readframes(CHUNK)

def server_transmission(client_ip, time_of_flight, data, max_delay):
    """ Sleep the appropriate ToF amount and send data to each server. """

    time.sleep(max_delay - time_of_flight)
    UDPSock.sendto(data, (client_ip, 8000))

def player_thread(rtt_delay):
    """ Play the music on the client. """
    global stream
    time.sleep(rtt_delay)
    while True:
        if data_bytes.qsize() >= BUFFER:
            while data_bytes.qsize() > 0:
                 stream.write(data_bytes.get(), CHUNK)

def initial_client_message():
    """ Send an initial message with metadata about the music to the Server. """

    global stream, start_time
    p = pyaudio.PyAudio()
    wf = wave.open("song.wav", 'rb')

    format = p.get_format_from_width(wf.getsampwidth())
    channels = wf.getnchannels()
    rate = wf.getframerate()

    stream = p.open(format = format,
                channels = channels,
                rate = rate,
                output = True)

    message = {}
    message['channels'] = channels
    message['rate'] = rate
    message['format'] = format

    pickled_data = pickle.dumps(message)
    start_time = time.time()

    for ip in IPS:  
        UDPSock.sendto(pickled_data, (ip, 8000))


def main():
    """ Main Function to start Client and Server Threads. """

    client_thread = Thread(target=initial_client_message)
    server_thread = Thread(target=server)
    client_thread.daemon = True
    server_thread.daemon = True
    client_thread.start()
    server_thread.start()
    
    while True:
        a = 0

if __name__ == "__main__":
    main()
