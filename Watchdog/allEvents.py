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
        r = requests.delete("http://127.0.0.1:8000/sync/" +  str(serverId) + "/delete_file/?current_user=1")
        print r.text
        with conn:
            c = conn.cursor()
            sql_cmd = "DELETE FROM fileData WHERE file_path = ? and server_id = ? "
            c.execute(sql_cmd, (filePath, serverId))
            conn.commit()







