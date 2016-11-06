#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
import socket
from threading import Thread
import wave

def udpStream(CHUNK):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", 12345))

    while True:
        soundData, addr = udp.recvfrom(CHUNK)
        stream.write(soundData)

    udp.close()

if __name__ == "__main__":
    FORMAT = 32
    CHUNK = 1024
    RATE = 11000

    p = pyaudio.PyAudio()
    wf = wave.open("temp.wav", 'rb')
    stream = p.open(format = FORMAT,
            channels = 1,
            rate = wf.getframerate(),
            output = True)

    Ts = Thread(target = udpStream, args=(CHUNK,))
    Tp = Thread(target = play, args=(stream, CHUNK,))
    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Ts.start()
    Tp.start()
    while True:
        a = 0