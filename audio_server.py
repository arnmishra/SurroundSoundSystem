#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
import socket
from threading import Thread
import wave

data_bites = []

def udpStream(CHUNK):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", 12345))

    while True:
        soundData, addr = udp.recvfrom(CHUNK*CHANNELS*2)
        data_bites.append(soundData)

    udp.close()

def run(CHUNK):
    BUFFER = 1
    while True:
        if len(data_bites) == BUFFER:
            while len(data_bites) > 0:
                stream.write(data_bites.pop(0), CHUNK)

if __name__ == "__main__":
    FORMAT = 8
    CHANNELS = 2
    CHUNK = 1024
    RATE = 44100

    p = pyaudio.PyAudio()
    wf = wave.open("song.wav", 'rb')
    stream = p.open(format = FORMAT,
            channels = CHANNELS,
            rate = wf.getframerate(),
            output = True)

    Ts = Thread(target = run, args=(CHUNK,))
    Tp = Thread(target = udpStream, args=(CHUNK,))
    Tp.setDaemon(True)
    Ts.setDaemon(True)
    Tp.start()
    Ts.start()
    while True:
        a = 0