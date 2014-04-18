__author__ = 'morganPietruszka, meganBishop'

import logging
import os
import datetime
import sys
import time
import sqlite3
import requests
import json

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
            self.upload_file(path, timeInfo,eventType)

        if eventType == "modified":
            self.update_file(event.src_path, timeInfo, eventType)

        if eventType == "deleted":
            SpecificEventHandler.on_deleted1(specific, event.src_path)

        if eventType == "created":
            self.upload_file(event.src_path, timeInfo, eventType)

    #
    #     # if self.path_compare(event.src_path) is True:
    #     #     self.update_file(event.src_path, timeInfo, eventType)
    #     # else:
    #     #     self.upload_file(event.src_path, timeInfo, eventType)
    #
    #
    #
    # def path_compare(self, path_now):
    #     conn = sqlite3.connect(database)
    #     with conn:
    #         c = conn.cursor()
    #         c.execute('''SELECT file_path AND server_id
    #                         FROM fileData
    #                         WHERE file_path = ?''', (path_now,))
    #         results = c.fetchall()
    #         if results:
    #             return True
    #         else:
    #             return False



    def update_file(self, filePath, time, eventType):
        print "updating file"
        conn = sqlite3.connect(database)
        #serverId = -1
        #print serverId

        with conn:
            c = conn.cursor()
            #c.execute('''update fileData set server_id =(?) where file_path = (?)''', (serverId, filePath))
            c.execute('''select server_id from fileData where file_path = ?''', (filePath,))
            serverId = int(c.fetchall()[0][0])
            conn.commit()
        print serverId

        #by this point will have server id
        with open(filePath, 'r') as f:
            file_cont = f.read()
        params = {'current_user':1, "last_modified": time, 'file_data': file_cont}
        r = requests.post("http://127.0.0.1:8000/sync/%d/update_file/" %serverId, data = params)

        with open("file.html", 'w') as f:
            f.write(r.text)


    def upload_file(self, filePath, time, eventType):
        #read file
        with open(filePath, 'r') as f:
            file_cont = f.read()
        params = {'current_user':1, 'local_path': filePath, "last_modified": time, 'file_data': file_cont}
        r = requests.post("http://127.0.0.1:8000/sync/create_server_file/", data = params)
        print r.text
        serverID = json.loads(r.text)["file_id"]
        conn = sqlite3.connect(database)
        with conn:
            c = conn.cursor()
            sql_cmd = "insert into fileData values(?, ?, ?, ?)"
            c.execute(sql_cmd, (filePath, serverID, time, eventType))
            conn.commit()

if __name__ == "__main__":
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