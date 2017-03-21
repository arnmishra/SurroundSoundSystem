import pyaudio
from socket import *
import wave
import Queue
from threading import Thread
import pickle
import time
import sys
import netifaces as ni

CHUNK = 1024
BUFFER = 100

UDPSock = socket(AF_INET, SOCK_DGRAM)
data_bytes = Queue.Queue()

def server(my_ip, slave_ips, song_path):
    """ Server thread to get all ToF data and start playing music and sending data. 

    :param my_ip: IP of current device
    :param slave_ips: list of IPs of all slaves
    """

    global start_time

    UDPSock.bind((my_ip, 9000))
    max_delay = -1
    slaves = {}

    for i in range(num_slaves):
        (data, addr) = UDPSock.recvfrom(1024)
        slave_ip = addr[0]
        rec_time = time.time()
        rtt_time = rec_time - start_time
        time_of_flight = rtt_time/2.0
        if time_of_flight > max_delay:
            max_delay = time_of_flight
        slaves[slave_ip] = time_of_flight
        print "Slave #", i, "Connected"

    my_player_thread = Thread(target=player_thread, args = (max_delay,))
    my_player_thread.daemon = True
    my_player_thread.start()

    send_song_no_thread(max_delay, slave_ips, song_path)
    # send_song_threaded(max_delay, slaves, song_path)

def send_song_no_thread(rtt_delay, slave_ips, song_path):
    """ Send song chunks to each slave in a single thread.

    :param rtt_delay: how long to wait to sync up the rtt times
    :param slave_ips: list of IPs of all slaves
    """
    wf = wave.open(song_path, 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        time.sleep(0.01) # Live Stream Affect
        for ip in slave_ips:
            UDPSock.sendto(data, (ip, 8000))
        data_bytes.put(data)
        i += 1
        print "Sent Packet #", i
        data = wf.readframes(CHUNK)

def send_song_threaded(max_delay, slaves, song_path):
    """ Send song chunks to each slave in a separate thread. 

    :param slaves: a list of slave ips to send the music too
    :param max_delay: the longest rtt, how long to wait to sync up the rtt times
    """

    wf = wave.open(song_path, 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        time.sleep(0.01) # Live Stream Affect
        for slave_ip in slaves:
            slave_thread = Thread(target=slave_transmission, args = (slave_ip, slaves[slave_ip], data, max_delay))
            slave_thread.daemon = True
            slave_thread.start()
        data_bytes.put(data)
        i += 1
        print "Sent Packet #", i
        data = wf.readframes(CHUNK)

def slave_transmission(slave_ip, time_of_flight, data, max_delay):
    """ Sleep the appropriate ToF amount and send data to each slave. 

    :param slave_ip: IP address of the slave which the music is being sent to
    :param time_of_flight: RTT for this specific slave
    :param data: the music data packets to be sent
    :param max_delay: the maximum RTT value between all slaves
    """

    time.sleep(max_delay - time_of_flight)
    UDPSock.sendto(data, (slave_ip, 8000))

def player_thread(rtt_delay):
    """ Play the music on the slave. 

    :param rtt_delay: how long to wait to sync up the rtt times
    """
    global stream
    while True:
        if data_bytes.qsize() >= BUFFER:
            while data_bytes.qsize() > 0:
                 stream.write(data_bytes.get(), CHUNK)

def initial_client_message(slave_ips, song_path):
    """ Send an initial message with metadata about the music to the Slaves. 

    :param slave_ips: list of IPs of all slaves
    """

    global stream, start_time
    p = pyaudio.PyAudio()
    wf = wave.open(song_path, 'rb')

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

    for ip in slave_ips:  
        UDPSock.sendto(pickled_data, (ip, 8000))


def main(my_ip, slave_ips, num_slaves, song_path):
    """ Main Function to start Client and Server Threads. 

    :param my_ip: IP of the client device
    :param slave_ips: list of IPs of all slaves
    :param num_slaves: total number of slaves
    """

    client_thread = Thread(target=initial_client_message, args=(slave_ips, song_path, ))
    server_thread = Thread(target=server, args=(my_ip, slave_ips, song_path, ))
    client_thread.daemon = True
    server_thread.daemon = True
    client_thread.start()
    server_thread.start()
    
    while True:
        a = 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python %s <wav_song_name> <list_of_slave_ips>' % sys.argv[0])
        print('e.g. python %s song.wav 1.1.1.1 2.2.2.2 3.3.3.3' % sys.argv[0])
        sys.exit(1)
    my_ip = ni.ifaddresses('en0')[2][0]['addr']
    song_path ="wav_files/" + sys.argv[1]
    slave_ips = sys.argv[2:]
    num_slaves = len(slave_ips)
    main(my_ip, slave_ips, num_slaves, song_path)
