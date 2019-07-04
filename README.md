# EasyFFmpeg
A tool to make using common FFmpeg commands easier.
To use this, grab a [release](https://github.com/wolfinabox/EasyFFmpeg/releases). This program accepts command line arguments, and will ask for any input it *does not* get from them, from input. You can drag and drop video files onto it, as well.

To run this  from source, create a python 3.6(.7) virtualenv called "env", and run `pip install -r ./requirements.txt`. You will need to provide the `ffmpeg.exe` and `ffplay.exe` yourself, in a `resources` folder next to the script.