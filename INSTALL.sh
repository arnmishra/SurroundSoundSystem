#!/bin/sh

brew install portaudio
brew install sox --with-lame --with-flac --with-libvorbis
sudo pip install -r requirements.txt
