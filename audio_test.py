# Save as server.py 
# Message Receiver
from threading import Thread
from socket import *
import pyaudio
import time
import wave

# Arnav's IP: 172.16.126.165
# Kush's IP: 172.16.126.207


SOCKET = None
CHUNK = 1024


def server():
    addr = ("", 9000)
    SOCKET.bind(addr)
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    output = True,
                    frames_per_buffer = CHUNK,
                    )

    while True:
        (soundData, addr) = SOCKET.recvfrom(CHUNK * CHANNELS * 2)
        stream.write(soundData)


def client():
    time.sleep(5)
    addr = ("172.16.126.207", 9000)
    wf = wave.open("temp.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
    data = wf.readframes(CHUNK)
    while data != '':
        SOCKET.sendto(data, addr)
        data = wf.readframes(CHUNK)


UDPSock = socket(AF_INET, SOCK_DGRAM)
SOCKET = UDPSock
server_thread = Thread(target=server)
server_thread.daemon = True
server_thread.start()
client_thread = Thread(target=client)
client_thread.daemon = True
client_thread.start()
while True:
    a = 0

