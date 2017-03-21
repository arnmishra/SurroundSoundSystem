# Wireless Surround Sound System

SurroundSoundSystem is a wireless surround sound system started in CS 439 at the University of Illinois at Urbana Champaign. The purpose of this project is to allow multiple devices to play audio files wirelessly in synchronous. 

### Usage

Clone the repository. You will need [Python 2.7][python] and [PyAudio][pyaudio]. To install requirements using [Pip][pip], run:
```sh
$  pip install -r requirements.txt
```

To change the song, add a new Wave file to the wav_files directory and run the file with the appropriate song name. To start the client, run it with your song name as the first argument followed by the ips of each of the servers:

```sh
$  python audio_client.py <song_name> <list_of_server_ips>
```

example:

```sh
$  python audio_client.py song.wav 1.1.1.1 2.2.2.2 3.3.3.3
```

To start the server, no extra set-up should be needed:

```sh
$ python audio_server.py
```

### Todos

 * Add compatability for audio files that aren't Wave files.
 * Package deployment with an installation and configuration file.
 * Allow users to add songs to a queue.
 * Allow users to pause, play, and skip songs.

   [python]: <https://www.python.org/download/releases/2.7/>
   [pyaudio]: <https://people.csail.mit.edu/hubert/pyaudio/>
   [pip]: <https://pypi.python.org/pypi/pip/>
