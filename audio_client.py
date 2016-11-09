#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
from socket import *
import wave
import Queue
from threading import Thread
import pickle
import time

UDPSock = socket(AF_INET, SOCK_DGRAM)
CHUNK = 1024
wf = wave.open("song.wav", 'rb')
data_bites = Queue.Queue()
BUFFER = 10

def server():
    addr = ("172.16.126.116", 9000)
    UDPSock.bind(addr)
    (data, addr) = UDPSock.recvfrom(1024)
    print data
    rec_time = time.time()
    global current_time
    rtt_delay = rec_time - current_time
    print str(rtt_delay)
    my_player_thread = Thread(target=player_thread, args = (rtt_delay,))
    my_player_thread.daemon = True
    my_player_thread.start()
    send_song(rtt_delay)

def player_thread(rtt_delay):
    global stream
    time.sleep(rtt_delay/2)
    while True:
        if data_bites.qsize() >= BUFFER:
            while data_bites.qsize() > 0:
                 stream.write(data_bites.get(), CHUNK)



def send_song(rtt_delay):
    data = wf.readframes(CHUNK)

    # udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

    while data != '':
        UDPSock.sendto(data, ("172.16.126.165", 8000))
        data_bites.put(data)
        data = wf.readframes(CHUNK)

    stream.close()
    global p
    p.terminate()


def initial_client_message():
    global stream
    global p
    p = pyaudio.PyAudio()

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
    UDPSock.sendto(pickled_data, ("172.16.126.165", 8000))
    # UDPSock.sendto(pickled_data, ("172.16.126.165", 8000))
  



server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()
client_thread = Thread(target=initial_client_message)
client_thread.daemon = True
client_thread.start()


while True:
    a = 0






    

    


    
