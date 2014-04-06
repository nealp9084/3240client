__author__ = 'morganpietruszka'

import logging
import os
import datetime
import sys
import time

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        if(event.is_directory):
            files_in_dir = [event.src_path+"/"+f for f in os.listdir(event.src_path)]
            mod_file_path = max(files_in_dir, key=os.path.getmtime)
            print " "
            print mod_file_path


        print("event noticed: " + event.event_type +
                 " on file " + event.src_path + " at " + str(datetime.datetime.now()))

        print " "
        print event.event_type
        print " "
        print event.src_path
        print " "
        print str(datetime.datetime.now())
        print " "


if __name__ == "__main__":
    event_handler = EventHandler()
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    handler = LoggingEventHandler()
    observer = Observer()
    # observer.schedule(handler, path, recursive=True)
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# def dateChange(base_path, filename):
#     t = os.path.getmtime(os.path.join(base_path, filename))
#     return datetime.datetime.fromtimestamp(t)
#
# def dirChange(base_path):
#     for file in os.listdir(base_path):
#         #figure out what type of change (C, M, D)
#         #notify server of what type of change was made
#         print file, dateChange(base_path, file)
#
# def timeRecord(dateTime):
#     epoch = datetime.datetime.utcfromtimestamp(0)
#     delta = dateTime - epoch
#     return delta.total_seconds()
#
# def milliSecs(dateTime):
#     return timeRecord(dateTime) * 1000.0

#git add "filename"
#git commit -m "messageiwant"
#git push