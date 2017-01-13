#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
from socket import *
import wave
import Queue
from threading import Thread
import pickle
import time
import sys

UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock2 = socket(AF_INET, SOCK_DGRAM)
UDPSockDynamic = socket(AF_INET, SOCK_DGRAM)


CHUNK = 1024
data_bites = Queue.Queue()
BUFFER = 100

clients = {}

rtts = []

MY_IP = "169.254.104.3"
IPS = sys.argv[1:]
num_clients = len(IPS)

# def calculate_rtt():
#     addr3 = (MY_IP, 9005)
#     UDPSockDynamic.bind(addr3)

#     while True:
#         first_time = time.time()
#         UDPSockDynamic.sendto("hello", (YOUR_IP, 9005))
#         (data, addr) = UDPSockDynamic.recvfrom(1024)
#         second_time = time.time()
#         # rtt.append(second_time - first_time)
#         print second_time - first_time
#         time.sleep(1)
#         # print "here"


def server():
    addr = (MY_IP, 9000)
    UDPSock.bind(addr)

    addr2 = (MY_IP, 9001)
    UDPSock2.bind(addr2)

    
    
    rec_time = []

    global current_time

    max_delay = -1

    print "yo"

    for i in range(num_clients):

        (data, addr) = UDPSock.recvfrom(1024)
        
        client = {}
        client["myIP"] = data
        client["rec_time"] = time.time()
        print client["rec_time"]
        client["rtt_time"] = client["rec_time"] - current_time
        client["single_time"] = client["rtt_time"]/2.0
        print client["single_time"]
        if client["single_time"] > max_delay:
            max_delay = client["single_time"]
        clients[data] = client
        print "client #", i



    # rtt_thread = Thread(target=calculate_rtt)
    # rtt_thread.daemon = True
    # rtt_thread.start()

    print "yo1"

    my_player_thread = Thread(target=player_thread, args = (max_delay,))
    my_player_thread.daemon = True
    my_player_thread.start()
    print "yo2"
    thread_id = 0

    send_song_no_thread()

    # for key in clients:
    #     client = clients[key]
    #     server_thread = Thread(target=send_song, args = (client,max_delay,thread_id))
    #     server_thread.daemon = True
    #     server_thread.start()
    #     thread_id += 1

def send_song_no_thread():
    wf = wave.open("song.wav", 'rb')
    data = wf.readframes(CHUNK)
    i = 0
    while data != '':
        i += 1
        print i
        # UDPSock.sendto(data, (ip1, 8000))
        time.sleep(.015)
        data_bites.put(data)
        for ip in IPS:
            UDPSock.sendto(data, (ip, 8000))
        # data_bites.put(data)
        #UDPSock2.sendto(data, (YOUR_IP_2, 8000))
        # UDPSock2.sendto(str(i), (ip2, 8000))
        # time.sleep(.1)
        
            
        data = wf.readframes(CHUNK)

def player_thread(rtt_delay):
    global stream
    print str(rtt_delay)
    time.sleep(rtt_delay)
    while True:
        if data_bites.qsize() >= BUFFER:
            while data_bites.qsize() > 0:
                 stream.write(data_bites.get(), CHUNK)



def send_song(client,max_delay,thread_id):
    wf = wave.open("song.wav", 'rb')
    data = wf.readframes(CHUNK)

    print(client["single_time"])
    print( max_delay)


    time.sleep(max_delay - client["single_time"])
    i = 0
    j=0
    print "here"
    while data != '':
        #time.sleep(.01)
        if thread_id == 0:
            UDPSock.sendto(data, (client["myIP"], 8000))
            data_bites.put(data)
            i += 1
            print i,thread_id
        else:
            UDPSock2.sendto(data, (client["myIP"], 8000))
            j += 1
            print j,thread_id
            
        data = wf.readframes(CHUNK)

    # stream.close()
    # global p
    # p.terminate()


def initial_client_message():
    global stream
    global p
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
    global current_time
    current_time = time.time()
    print current_time

    for ip in IPS:  
        UDPSock.sendto(pickled_data, (ip, 8000))
        print time.time()
    #UDPSock.sendto(pickled_data, (YOUR_IP_2, 8000))
    #print time.time()
    print "---------"





server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()
client_thread = Thread(target=initial_client_message)
client_thread.daemon = True
client_thread.start()







while True:
    a = 0