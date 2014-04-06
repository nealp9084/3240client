__author__ = 'morganPietruszka, meganBishop'

import logging
import os
import datetime
import sys
import time
import sqlite3

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

database = 'fileData.db'

class EventHandler(FileSystemEventHandler):

    # def is_directory(self):
    #     return self._is_directory()

    def on_any_event(self, event):
        if event.is_directory:
            return
            # files_in_dir = [event.src_path+"/"+f for f in os.listdir(event.src_path)]
            # #print str(os.path.getmtime)
            #
            # mod_file_path = max(files_in_dir, key=os.path.getmtime)
            # print " "
            # print mod_file_path


        print("event noticed: " + event.event_type +
                 " on file " + event.src_path + " at " + str(datetime.datetime.now()))

        # print " "
        # print event.event_type
        eventType = event.event_type
        # print " "
        # print event.src_path
        # print " "
        # print str(datetime.datetime.now())
        timeInfo = str(datetime.datetime.now())
        # print " "
        self.write_to_db(event.src_path, timeInfo, eventType)

    #somehow get server id in there
    def write_to_db(self, filePath, time, modType):
        conn = sqlite3.connect(database)
        with conn:

            c = conn.cursor()
            # Create table
            c.execute('''CREATE TABLE if not exists fileData(
                file_path text,
                server_id text,
                date_stamp text,
                modification_type text
                );''')
            # Save (commit) the changes
            conn.commit()

            sql_cmd = "insert into fileData values(?, -1, ?, ?)"
            c.execute(sql_cmd, (filePath, modType, time))
            conn.commit()


if __name__ == "__main__":
    event_handler = EventHandler()
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    if not os.path.exists(os.path.join(path, 'oneDir')):
        path = os.path.join(path, 'oneDir')
        os.mkdir(path)

    else:
        path = path+'\oneDir'


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