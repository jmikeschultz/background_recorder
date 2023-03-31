# background_recorder

python app for recording background conversation.

## Description

background_recorder is a simple program for recording background conversation.  When the sound level is greater than 'trigger_rms' it starts
recording, and keeps recording until 'timeout_secs' of silence, at which time it will write the sound to a wave file in 'out_dir'.  The 
wave file will contain 'cushion_secs' of recording before and after the sound (i.e. not the entire timeout silence).  In addition to a 
'recorder' thread, main also defines and calls a 'cleanup' thread which will delete wave files older than 'delete_secs'.

## Getting Started

### Dependencies

* pyaudio
* struct
* wave

### Installing

### Executing program

* python3 main.py

## Help

## Authors

Mike Schultz

## Version History

* Initial Release

## License

Distributed under the MIT License. See LICENSE.txt for more information.

## Acknowledgments

Inspiration, code snippets, etc.
* [starting code] (https://stackoverflow.com/questions/18406570/python-record-audio-on-detected-sound)
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
