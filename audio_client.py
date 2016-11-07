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
current_time = -1
rtt_delay = -1


my_song = Queue.Queue()


def server():
    UDPSock.bind(("", 9000))
    (data, addr) = UDPSock.recvfrom(1024)
    rec_time = time.time()
    rtt_delay = current_time - rec_time

    my_player_thread = Thread(target=player)
    my_player_thread.daemon = True
    my_player_thread.start()
    send_song()

def player_thread():
    while True:
        while data_bites.qsize() > 0:
             stream.write(data_bites.get(), CHUNK)



def send_song():
    data = wf.readframes(CHUNK)

    # udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

    while data != '':
        UDPSock.sendto(data, ("172.16.126.165", 9000))
        my_song.put(data)
        data = wf.readframes(CHUNK)

    stream.close()
    p.terminate()


def initial_client_message():
    wf = wave.open("song.wav", 'rb')
    p = pyaudio.PyAudio()

    format = p.get_format_from_width(wf.getsampwidth())
    channels = wf.getnchannels()
    rate = wf.getframerate()
    output = None

    stream = p.open(format = format,
                channels = channels ,
                rate = rate,
                output = True)

    message = {}
    message['channels'] = channels
    message['rate'] = rate
    message['format'] = format


    
    addr = ("172.16.126.165", 8000)

    pickled_data = pickle.dumps(message)
    current_time = time.time()  
    UDPSock.sendto(pickled_data, addr)
    print "here"



server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()
client_thread = Thread(target=initial_client_message)
client_thread.daemon = True
client_thread.start()


while True:
    a = 0






    

    


    
