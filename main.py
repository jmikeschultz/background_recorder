import recorder
import threading
import datetime
import logging
import time
import os
import sys

def record_thread(recorder):
    logging.info('recording thread started')
    recorder.record()

def cleanup_thread(out_dir, delete_secs):
    out_dir_fd = os.open(out_dir, os.O_RDONLY)

    # clean out old files
    while True:
        files = os.listdir(out_dir)
        for file in files:
            if '.wav' not in file:
                continue

            now = time.time()
            stat = os.stat(file)
            moded = int(stat.st_mtime)
            age_secs = int(now - moded)

            if age_secs > delete_secs:
                os.remove(file, dir_fd=out_dir_fd)
                logging.info(f'{file} age={age_secs} secs DELETING')
            else:
                logging.debug(f'{file} age={age_secs} secs')
                
        time.sleep(60)
    
if __name__ == '__main__':
    out_dir = '.'
    logfile = os.path.join(out_dir, 'recording.log')

    logging.basicConfig(level=logging.INFO,
                        #stream=sys.stderr,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logfile,
                        format='%(asctime)s %(name)s - %(levelname)s - %(message)s')

    recorder = recorder.Recorder(trigger_rms=10, out_dir=out_dir, timeout_secs=30)

    t1 = threading.Thread(target=record_thread, args=(recorder,))
    t1.start()

    delete_secs = 24 * 3600
#    delete_secs = 60

    t2 = threading.Thread(target=cleanup_thread, args=(out_dir, delete_secs))
    t2.start()
    