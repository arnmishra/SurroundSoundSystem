import pyaudio
from socket import *
import wave
import Queue
from threading import Thread, Lock
import pickle
import time
import sys

CHUNK = 1024
BUFFER = 12

data_sock = socket(AF_INET, SOCK_DGRAM) # UDP Socket for sending data
heartbeat_sock = socket(AF_INET, SOCK_DGRAM) # UDP Socket for managing heartbeats
data_bytes = Queue.Queue() # Queue of song data chunks to play
song_queue = Queue.Queue() # Queue of songs to play next
heartbeat_slaves = {} # Hashmap of IP of slave to expected heartbeat arrival time.
slave_ips = [] # List of IPs of all slaves.
heartbeat_lock = Lock() # Lock to prevent access during modification of hearbeat data structures during node failure.
playing_song = False

def start_thread(method_name, arguments):
    """ Method to start new daemon threads.

    :args method_name: Name of method to start a thread of
    :args arguments: Arguments to pass into new thread
    """
    thread = Thread(target=method_name, args=arguments)
    thread.daemon = True
    thread.start()

def config_messages(song_path):
    """ Send a message with metadata about the song to the Slaves. 

    :param song_path: path to the song
    """

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

    heartbeat_lock.acquire()
    for ip in slave_ips:  
        data_sock.sendto(pickled_data, (ip, 8000))
    heartbeat_lock.release()

    return start_time, stream

def player_thread(rtt_delay, stream):
    """ Play the music on the slave. 

    :param rtt_delay: how long to wait to sync up the rtt times
    :param stream: stream configuration for playing the audio file
    """
    while True:
        if data_bytes.qsize() >= BUFFER:
            while data_bytes.qsize() > 0:
                 stream.write(data_bytes.get(), CHUNK)

def slave_transmission(slave_ip, time_of_flight, data, max_delay):
    """ Sleep the appropriate ToF amount and send data to each slave. 

    :param slave_ip: IP address of the slave which the music is being sent to
    :param time_of_flight: RTT for this specific slave
    :param data: the music data packets to be sent
    :param max_delay: the maximum RTT value between all slaves
    """

    time.sleep(max_delay - time_of_flight)
    data_sock.sendto(data, (slave_ip, 8000))

def send_song_threaded(max_delay, slaves, song_path):
    """ Send song chunks to each slave in a separate thread. 

    :param max_delay: the longest rtt, how long to wait to sync up the rtt times
    :param slaves: a list of slave ips to send the music too
    :param song_path: path to the song
    """

    wf = wave.open(song_path, 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        playing_song = True
        time.sleep(0.01) # Live Stream Affect
        for slave_ip in slaves:
            start_thread(slave_transmission, (slave_ip, slaves[slave_ip], data, max_delay))
        data_bytes.put(data)
        i += 1
        print "Sent Packet #", i
        data = wf.readframes(CHUNK)
    playing_song = False
    if(song_queue.qsize() > 0):
        start_thread(player_thread, (max_delay, stream))
        start_thread(send_song_no_thread, (max_delay, "wav_files/" + song_name))
        playing_song = True

def send_song_no_thread(rtt_delay, song_path):
    """ Send song chunks to each slave in a single thread.

    :param rtt_delay: how long to wait to sync up the rtt times
    :param song_path: path to the song
    """
    wf = wave.open(song_path, 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        time.sleep(0.01) # Live Stream Affect
        heartbeat_lock.acquire()
        for ip in slave_ips:
            data_sock.sendto(data, (ip, 8000))
        heartbeat_lock.release()
        data_bytes.put(data)
        i += 1
        print "Sent Packet #", i
        data = wf.readframes(CHUNK)


def send_heartbeats(ip):
    """ Thread to send heartbeats to each of the slaves

    :param ip: IP to send heartbeat to
    """
    heartbeat_lock.acquire()
    for ip in heartbeat_slaves:
        heartbeat_sock.sendto("Heartbeat", (ip, 9000))
        heartbeat_slaves[ip] = time.time() + 1
    heartbeat_lock.release()

def receive_heartbeats():
    """ Thread to receive heartbeats from each of the slaves 

    If a heartbeat is received from an ip that doesn't exist, it must have been marked failed
    and removed from the list. Print error message and quit. Otherwise set the expected arrival 
    time to -1 so that the ip isn't marked failed and send a new heartbeat.
    """
    while True:
        (data, addr) = heartbeat_sock.recvfrom(1024)
        heartbeat_lock.acquire()
        if addr[0] not in heartbeat_slaves:
            print "%s incorrectly marked failed. Expected at time %s but current time is %s" % (addr[0], heartbeat_slaves[addr[0]], time.time())
            sys.exit(1)
        heartbeat_slaves[addr[0]] = -1
        heartbeat_lock.release()
        start_thread(send_heartbeats, (addr[0],))

def identify_failures():
    """ Thread to identify failures among nodes
    
    Loop through slaves every 1 second to check if a heartbeat is not recieved in time. If 
    it isn't received, remove the slave if it has failed from the dictionary and the send list. 
    """
    while True:
        for slave_ip in heartbeat_slaves.keys():
            if heartbeat_slaves[slave_ip] != -1 and heartbeat_slaves[slave_ip] < time.time():
                heartbeat_lock.acquire()
                print "%s failed. Expected at time %s but current time is %s" % (slave_ip, heartbeat_slaves[slave_ip], time.time())
                slave_ips.remove(slave_ip)
                del heartbeat_slaves[slave_ip]
                heartbeat_lock.release()
        time.sleep(1)

def start_song(song_path):
    start_time, stream = config_messages(song_path)
    max_delay = -1
    slaves = {}

    for i in range(len(slave_ips)):
        (data, addr) = data_sock.recvfrom(1024)
        slave_ip = addr[0]
        rec_time = time.time()
        rtt_time = rec_time - start_time
        time_of_flight = rtt_time/2.0
        if time_of_flight > max_delay:
            max_delay = time_of_flight
        slaves[slave_ip] = time_of_flight
        print "Slave #", i, "Connected"

    start_thread(player_thread, (max_delay, stream))
    start_thread(send_song_no_thread, (max_delay, song_path))
    #start_thread(send_song_threaded, (max_delay, slaves, song_path))

def main(song_path):
    """ Main thread to get all ToF data and start playing music and sending data. 

    :param song_path: path to the song
    """

    start_song(song_path)

    for ip in slave_ips:
        heartbeat_slaves[ip] = -1
        start_thread(send_heartbeats, (ip,))
    start_thread(receive_heartbeats,())
    start_thread(identify_failures, ())
    
    while True:
        request = raw_input()
        command = request.split(' ')[0]
        song_name = request.split(' ')[1]
        if(command == 'add'):
            if(playing_song == True):
                song_queue.put(song_name)
                print 'Added song to queue'
            else:
                start_song('wav_files/'+ song_name)
        a = 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python %s <wav_song_name> <list_of_slave_ips>' % sys.argv[0])
        print('e.g. python %s song.wav 1.1.1.1 2.2.2.2 3.3.3.3' % sys.argv[0])
        sys.exit(1)
    song_path ="wav_files/" + sys.argv[1]
    slave_ips = sys.argv[2:]
    data_sock.bind(("127.0.0.1", 8010))
    heartbeat_sock.bind(("127.0.0.1", 9010))
    main(song_path)
