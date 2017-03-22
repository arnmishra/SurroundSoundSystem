# Wireless Surround Sound System

SurroundSoundSystem is a wireless surround sound system started in CS 439 at the University of Illinois at Urbana Champaign. The purpose of this project is to allow multiple devices to play audio files wirelessly in synchronous. 

### Usage

Clone the repository. You will need [Python 2.7][python] and [PyAudio][pyaudio]. To install requirements using [Pip][pip], run:
```sh
$  pip install -r requirements.txt
```

You MUST start the slaves before the master. To start the slaves, no extra set-up should be needed:

```sh
$ python slave.py
```

To start the master, run it with the ips of each of the slaves as command line arguments. To play a song, type "add <song_name>" in the terminal and hit enter for each song you want to add. Make sure to add the song file to the audio_files directory first:

```sh
$  python master.py <list_of_slave_ips>
```

example:

```sh
$  python master.py 1.1.1.1 2.2.2.2 3.3.3.3
```


### Todos

Work on many of the Todos has begun, so contact the maintainers before beginning.

 * Package deployment with an installation and configuration file.
 * Allow users to pause, play, and skip songs.

   [python]: <https://www.python.org/download/releases/2.7/>
   [pyaudio]: <https://people.csail.mit.edu/hubert/pyaudio/>
   [pip]: <https://pypi.python.org/pypi/pip/>
