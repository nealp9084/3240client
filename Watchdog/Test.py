__author__ = 'morganPietruszka, meganBishop'

import logging
import os
import datetime
import sys
import time
import sqlite3
import requests
import json
import allEvents

from allEvents import SpecificEventHandler

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

database = 'fileData.db'
specific = SpecificEventHandler()


class EventHandler(FileSystemEventHandler):



    def on_any_event(self, event):

        if event.is_directory:
            return


        print("event noticed: " + event.event_type +
                 " on file " + event.src_path + " at " + str(datetime.datetime.now()))


        eventType = event.event_type
        timeInfo = str(datetime.datetime.now())

        if eventType == "moved":
            path = SpecificEventHandler.on_moved1(specific, event)
            SpecificEventHandler.on_create1(path, timeInfo,eventType)

        if eventType == "modified":
            SpecificEventHandler.on_modified1(event.src_path, timeInfo, eventType)

        if eventType == "deleted":
            SpecificEventHandler.on_deleted1(specific, event.src_path)

        if eventType == "created":
            SpecificEventHandler.on_create1(event.src_path, timeInfo, eventType)

   def sync_now(self):
       #do syncing stuff now
       #need to get server copy of database
       #compare their copy of database to ours
       #if database doesnt match then update theirs



@staticmethod
def command_line():

    sync = allEvents.syncing

    while True:
        print 'Enter a number to perform the corresponding task'
        if (sync == 1):
            print '1: Turn automatic sync off'
        else:
            print '1: Turn automatic sync on'
        print '2: Change password'

        num = int(raw_input())

        if num == 1:
            if sync == 1:
                allEvents.syncing = 0
            else:
                allEvents.syncing = 1
                #sync with server now
        else:
            print "Invalid Entry. Enter '1' or '2'"

        print

if __name__ == "__main__":
    command_line()

    event_handler = EventHandler()

    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    if not os.path.exists(os.path.join(path, 'oneDir')):
        path = os.path.join(path, 'oneDir')
        os.mkdir(path)

    else:
        path = path+'/oneDir'

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
        # Save (commit) the changes'
        conn.commit()

    handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



#git add "filename"
#git commit -m "messageiwant"
#git push