#!/bin/sh

brew install portaudio
brew install sox --with-lame --with-flac --with-libvorbis
pip install -r requirements.txt
