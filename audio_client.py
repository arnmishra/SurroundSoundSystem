#http://stackoverflow.com/questions/21164804/udp-sound-transfer-played-sound-have-big-noise
import pyaudio
import socket
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

wf = wave.open("temp.wav", 'rb')

p = pyaudio.PyAudio()

stream = p.open(format =
            p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

chunk = 1024

data = wf.readframes(chunk)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

while data != '':
    udp.sendto(data, ("127.0.0.1", 12345))
    data = wf.readframes(chunk)

while True:
    a = 0
stream.close()
p.terminate()