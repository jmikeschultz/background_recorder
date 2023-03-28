#
# https://stackoverflow.com/questions/18406570/python-record-audio-on-detected-sound
#
import pyaudio
import math
import struct
import wave
import time
import datetime
import logging
import os

#RATE = 44100 # = 300MB/hour
#RATE = 22050 # = 150MB/hour

SHORT_NORMALIZE = (1.0/32768.0)
FORMAT = pyaudio.paInt16
CHANNELS = 1
SHORT_WIDTH = 2

class Recorder:
    @staticmethod
    def rms(frame):
        count = len(frame) / SHORT_WIDTH
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self, 
                 timeout_secs=5, 
                 out_dir='.', 
                 rate=22050,
                 cushion_secs=1,
                 trigger_rms=5,
                 frame_secs=0.25):
        
        self.p = pyaudio.PyAudio()

        self.out_dir = out_dir
        self.timeout_secs = timeout_secs
        self.rate = rate
        self.cushion_secs = cushion_secs
        self.chunk = int(rate * frame_secs)
        self.trigger_rms = trigger_rms

        self.stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=rate,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)
        
        self.start_time = time.time()
        self.quiet = []
        self.quiet_idx = -1
        self.timeleft = 0
        self.cushion_frames = int(cushion_secs / frame_secs)
        self.timeout_frames = int(timeout_secs / frame_secs)

    def record(self):
        sound = []
        start = time.time()
        begin_time = None

        while True:
            data = self.stream.read(self.chunk)
            rms_val = self.rms(data)

            if self.inSound(data):
                sound.append(data)
                if begin_time == None:
                    begin_time = datetime.datetime.now()
                    logging.info('starting recording')
            else:
                self.queueQuiet(data)
                if len(sound) > 0:
                    self.write(sound, begin_time)
                    sound.clear()
                    begin_time = None

            curr = time.time()
            secs = int(curr - start)
            tout = 0 if self.timeleft == 0 else int(self.timeleft - curr)
            label = 'listening' if self.timeleft == 0 else 'recording'
            logging.debug('%s: level=%4.2f secs=%d timeout=%d' % (label, rms_val, secs, tout))
        
    # quiet is a circular buffer of size cushion 
    def queueQuiet(self, data):
        self.quiet_idx += 1
        if self.quiet_idx == self.cushion_frames:
            self.quiet_idx = 0

        if len(self.quiet) < self.cushion_frames:
            self.quiet.append(data)
        else:            
            self.quiet[self.quiet_idx] = data

    def dequeueQuiet(self, sound):
        if len(self.quiet) == 0:
            return sound
        
        ret = []
        
        # either quiet not full or full and in order
        if len(self.quiet) < self.cushion_frames or self.quiet_idx == 0:
            ret.extend(self.quiet)
            ret.extend(sound)

        else:
            ret.extend(self.quiet[self.quiet_idx:])
            ret.extend(self.quiet[0:self.quiet_idx])
            ret.extend(sound)

        return ret
    
    def inSound(self, data):
        rms = self.rms(data)
        curr = time.time()

        if rms >= self.trigger_rms:
            self.timeleft = curr + self.timeout_secs
            return True
        
        if curr < self.timeleft:
            return True

        self.timeleft = 0
        return False

    def write(self, sound, begin_time):
        # insert the pre-sound quiet frames into sound
        sound = self.dequeueQuiet(sound)

        # sound ends with TIMEOUT_FRAMES of quiet
        # remove all but CUSHION_FRAMES
        keep_frames = len(sound) - self.timeout_frames + self.cushion_frames
        recording = b''.join(sound[0:keep_frames])

        filename = begin_time.strftime('%Y-%m-%d_%H.%M.%S')
        pathname = os.path.join(self.out_dir, '{}.wav'.format(filename))

        wf = wave.open(pathname, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(self.rate)
        wf.writeframes(recording)
        wf.close()
        logging.info('writing: {}'.format(pathname))

