__author__ = 'morganPietruszka, meganBishop'

import os
import datetime
import sys
import time
import logging
import requests
import sqlite3
import json
#import Test

from gi.repository import Notify

from getTokens import get_token
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

database = 'fileData.db'
syncing = 1
with open('IP.txt','r') as f:
    SERVER = f.read().strip()
Notify.init ("Watchdog")

#handle separate events in here

class SpecificEventHandler(FileSystemEventHandler):

    def on_moved1(self, time, event):
        #print "moved"
        #print event.src_path
        #print event.dest_path

        source = event.src_path
        dest = event.dest_path

        if "oneDir" not in dest:
            self.on_deleted1(source, time, 'deleted')
        if source == None:
            source = dest
            self.on_create1(source, time, event.event_type)
        else:
            self.on_deleted1(source, time, 'deleted')
            source = dest
            self.on_create1(source, time, event.event_type)
        return source

    def on_deleted1(self, filePath, time, eventType):
        #print "on_deleted1"
        token =  get_token()
        conn = sqlite3.connect(database)
        filePath = filePath.split('oneDir/')[1]

        with conn:
            c = conn.cursor()
            c.execute('''select server_id from fileData where file_path = ?''', (filePath,))
            query = c.fetchall()
            if not query:
                return
            serverId = int(query[0][0])
            conn.commit()
        #print serverId
        #read file
        if (syncing == 1):
            #import Test
            r = requests.delete("http://" + SERVER + "/sync/" +  str(serverId) + "/delete_file/?token=%s" %token)
            if r.json()['success']:
              message=Notify.Notification.new("File deleted",filePath,"dialog-information")
            else:
              message=Notify.Notification.new("FAILURE","Could not delete file on server.","dialog-information")            
            message.show()
        with conn:
            c = conn.cursor()
            sql_cmd = "update fileData set date_stamp = ?, modification_type = ? where file_path = ?"
            c.execute(sql_cmd, (time, eventType, filePath))
            conn.commit()

    def on_modified1(self, filePath, time, eventType):
        token =  get_token()
        #print "updating file"
        conn = sqlite3.connect(database)
        filePath = filePath.split('oneDir/')[1]

        with conn:
            c = conn.cursor()
            c.execute('''select server_id from fileData where file_path = ?''', (filePath,))
            serverId = int(c.fetchall()[0][0])

            sql_cmd = "update fileData set date_stamp = ?, modification_type = ? where file_path = ?"
            c.execute(sql_cmd, (time, eventType, filePath))

            conn.commit()
        #print serverId

        #by this point will have server id
        if (syncing == 1):
            with open('oneDir/' + filePath, 'r') as f:
                file_cont = f.read()
            #import Test
            params = {'token': token, "last_modified": time, 'file_data': file_cont}
            r = requests.post("http://" + SERVER + "/sync/%d/update_file/" %serverId, data = params)
            if r.json()['success']:
              message=Notify.Notification.new("File modified",filePath,"dialog-information")
            else:
              message=Notify.Notification.new("FAILURE","Could not modify file on server.","dialog-information")            
            message.show()

            with open("file.html", 'w') as f:
                f.write(r.text)


    def on_create1(self, filePath, time, eventType):
        #print "on create"
        token =  get_token()
        filePath = filePath.split('oneDir/')[1]

        #read file
        serverID = -1
        if (syncing == 1):
            with open('oneDir/' + filePath, 'r') as f:
                file_cont = f.read()
            #import Test
            params = {'token':token, 'local_path': filePath, "last_modified": time, 'file_data': file_cont}
            r = requests.post("http://" + SERVER + "/sync/create_server_file/", data = params)
            #print r.status_code
            if r.json()['success']:
              message=Notify.Notification.new("File created",filePath,"dialog-information")
              message.show()

            with open("create.html", 'w') as f:
                f.write(r.text)

            serverID = json.loads(r.text)["file_id"]
        conn = sqlite3.connect(database)
        with conn:
            c = conn.cursor()
            sql_cmd = "insert into fileData values(?, ?, ?, ?)"
            c.execute(sql_cmd, (filePath, serverID, time, eventType))
            conn.commit()
