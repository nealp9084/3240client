__author__ = 'morganPietruszka, meganBishop'



import os
import datetime
import sys
import time
import logging
import requests
import sqlite3
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

database = 'fileData.db'
syncing = 1

#handle separate events in here

class SpecificEventHandler(FileSystemEventHandler):


    def on_moved1(self, event):
        print "moved"
        print event.src_path
        print event.dest_path

        source = event.src_path
        dest = event.dest_path

        if "oneDir" not in dest:
            self.on_deleted1(source)
        else:
            source = dest
        return source


    def on_deleted1(self, filePath):
        conn = sqlite3.connect(database)
        with conn:
            c = conn.cursor()
            c.execute('''select server_id from fileData where file_path = ?''', (filePath,))
            serverId = int(c.fetchall()[0][0])
            conn.commit()
        print serverId
        #read file
        if (syncing == 1):
            r = requests.delete("http://127.0.0.1:8000/sync/" +  str(serverId) + "/delete_file/?current_user=1")
            print r.text
        with conn:
            c = conn.cursor()
            sql_cmd = "DELETE FROM fileData WHERE file_path = ? and server_id = ? "
            c.execute(sql_cmd, (filePath, serverId))
            conn.commit()

    def on_modified1(self, filePath, time, eventType):
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
        if (syncing == 1):
            with open(filePath, 'r') as f:
                file_cont = f.read()
            params = {'current_user':1, "last_modified": time, 'file_data': file_cont}
            r = requests.post("http://127.0.0.1:8000/sync/%d/update_file/" %serverId, data = params)

            with open("file.html", 'w') as f:
                f.write(r.text)


    def on_create1(self, filePath, time, eventType):
        #read file
        serverID = -1
        if (syncing == 1):
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





