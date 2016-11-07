#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
import socket
from threading import Thread
import wave
import Queue

data_bites = Queue.Queue()

def udpStream(CHUNK):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", 9000))

    while True:
        soundData, addr = udp.recvfrom(CHUNK*CHANNELS*2)
        data_bites.put(soundData)

    udp.close()

def run(CHUNK):
    BUFFER = 10
    while True:
        if data_bites.qsize() >= BUFFER:
            while data_bites.qsize() > 0:
                stream.write(data_bites.get(), CHUNK)

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

    run_music = Thread(target = run, args=(CHUNK,))
    get_data = Thread(target = udpStream, args=(CHUNK,))
    run_music.setDaemon(True)
    get_data.setDaemon(True)
    run_music.start()
    get_data.start()
    
    while True:
        a = 0