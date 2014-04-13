__author__ = 'morganPietruszka, meganBishop'

import logging
import os
import datetime
import sys
import time
import sqlite3
import requests
import json

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
        #compare the path the paths already in the db to determine if old file or new file
        serverId = -1
        if self.path_compare(event.src_path, serverId) is True:
            self.update_file(event.src_path, )
        else:
            self.upload_file(event.src_path, timeInfo, eventType)



    def path_compare(self, path_now, serverId):
        conn = sqlite3.connect(database)
        with conn:
            c = conn.cursor()
            if c.execute('''SELECT file_path AND server_id
                            FROM fileData
                            WHERE file_path = ?''', (path_now,)):
                serverId = c.fetchall()
                print serverId
                return True
            else:
                return False



    def update_file(self, filePath, serverId, time, eventType):
        with open(filePath, 'r') as f:
            file_cont = f.read()
        params = {'current_user':1, 'local_path': filePath, "last_modified": time, 'file_data': file_cont}
        r = requests.post("http://127.0.0.1:8000/sync/create_server_file/", data = params)
        print r.text
        serverID = json.loads(r.text)["file_id"]
        self.write_to_db(filePath, time, eventType, serverID)


    def upload_file(self, filePath, time, eventType):
        #read file
        with open(filePath, 'r') as f:
            file_cont = f.read()
        params = {'current_user':1, 'local_path': filePath, "last_modified": time, 'file_data': file_cont}
        r = requests.post("http://127.0.0.1:8000/sync/create_server_file/", data = params)
        print r.text
        serverID = json.loads(r.text)["file_id"]
        self.write_to_db(filePath, time, eventType, serverID)


    #somehow get server id in there
    def write_to_db(self, filePath, time, modType, serverID):
        conn = sqlite3.connect(database)
        with conn:
            c = conn.cursor()
            sql_cmd = "insert into fileData values(?, ?, ?, ?)"
            c.execute(sql_cmd, (filePath, serverID, time, modType))
            conn.commit()

    def update_db(self, filePath, time, modType, serverID):
        conn = sqlite3.connect(database)
        with conn:
            c = conn.cursor()
            sql_cmd = ('''UPDATE fileData
                        SET ''')
            c.execute(sql_cmd, (filePath, serverID, time, modType))
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