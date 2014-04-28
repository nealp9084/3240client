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
import dateutil.parser
import thread

import getTokens

from allEvents import SpecificEventHandler

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

database = 'fileData.db'
specific = SpecificEventHandler()
with open('IP.txt','r') as f:
    SERVER = f.read().strip()

class EventHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        #print event
        if event.is_directory:
            return

        eventType = event.event_type
        timeInfo = str(datetime.datetime.now())

        if eventType == "moved":
            path = specific.on_moved1(timeInfo, event)
           # specific.on_create1(path, timeInfo,eventType)

        if eventType == "modified":
            #SpecificEventHandler.on_modified1(event.src_path, timeInfo, eventType)
            specific.on_modified1(event.src_path, timeInfo, eventType)

        if eventType == "deleted":
            specific.on_deleted1(event.src_path, timeInfo, eventType)

        if eventType == "created":
            #SpecificEventHandler.on_create1(event.src_path, timeInfo, eventType)
            specific.on_create1(event.src_path, timeInfo, eventType)

    
    @staticmethod
    def sync_now():
       r = requests.get("http://"+SERVER+"/sync/?token=%s" %TOKEN)
       fileList = r.json()
       for item in fileList:
           #print item
           file_name = item["local_path"]
           timeS= item["last_modified"]
           tstamp = dateutil.parser.parse(timeS).replace(tzinfo = None)
           sId = item["id"]
           mod_type = "modified"

           conn = sqlite3.connect(database)
           with conn:
            c = conn.cursor()

            c.execute('''select file_path, date_stamp, modification_type from fileData where file_path = ?''', (file_name,))
            query = c.fetchall()
            conn.commit()
            #print query
            if not query:
                download = requests.get("http://"+SERVER+"/sync/%d/serve_file?token=%s" %(sId, TOKEN))
                fileCont = download.content
                with open('oneDir/'+file_name, 'wb') as f:
                    f.write(fileCont)

                conn = sqlite3.connect(database)
                with conn:
                    c = conn.cursor()
                    sql_cmd = "insert into fileData values(?, ?, ?, ?)"
                    c.execute(sql_cmd, (file_name, sId, timeS, mod_type))
                    conn.commit()
            else:
                conn = sqlite3.connect(database)
                with conn:
                    c = conn.cursor()
                    sql_cmd = "select date_stamp from fileData where file_path = ?"
                    c.execute(sql_cmd, (file_name,))
                    ts = c.fetchall()[0][0]
                    #print ts
                    lastMod = dateutil.parser.parse(ts).replace(tzinfo = None)
                    #print lastMod
                    conn.commit()
                    if tstamp == lastMod:
                        1
                    elif tstamp > lastMod:
                        download = requests.get("http://"+SERVER+"/sync/%d/serve_file?token=%s" %(sId,TOKEN))
                        fileCont = download.text
                        with open ('oneDir/'+file_name, 'wb') as f:
                            f.write(fileCont.encode('utf-8'))

                        conn = sqlite3.connect(database)
                        with conn:
                            c = conn.cursor()
                            sql_cmd = "update fileData set date_stamp = ?, modification_type = ? where file_path = ?"
                            c.execute(sql_cmd, (timeS, mod_type, file_name))
                            conn.commit()

                    elif lastMod > tstamp:
                         path = query[0][0]
                         time = query[0][1]
                         mod = query[0][2]
                         if mod == 'deleted':
                             specific.on_deleted1(path, time, mod)
                         else:
                             with open('oneDir/'+file_name, 'r') as f:
                                 file_cont = f.read()
                             params = {'token':TOKEN, "last_modified": lastMod, 'file_data': file_cont}
                             upL = requests.post("http://"+SERVER+"/sync/%d/update_file/" %sId, data = params)
                             code = upL.status_code
                             #print code
            #dump fileData
              
            conn = sqlite3.connect(database)
            with conn:
                c = conn.cursor()

                sql_cmd = ("select * from fileData where server_id = ?")
                c.execute(sql_cmd, ("-1",))
                query = c.fetchall()
          
                #print "THIS IS WHERE -1"
                #print query
                for item in query:
                    (filePath, serverID, timeStamp, modType) = item
                    with open('oneDir/'+filePath, 'r') as f:
                        file_cont = f.read()
                    params = {'token':TOKEN, 'local_path': filePath, "last_modified": timeStamp, 'file_data': file_cont}
                    r = requests.post("http://"+SERVER+"/sync/create_server_file/", data = params)
                    #print r.text
                    serverID = json.loads(r.text)["file_id"]
                    c = conn.cursor()
                    sql_cmd =( "update fileData set server_id = ? where file_path = ?")
                    c.execute(sql_cmd, (serverID, filePath))
                    conn.commit()
                    #print "finished"

            conn = sqlite3.connect(database)
            with conn:
                c = conn.cursor()

                sql_cmd = ("select * from fileData")
                c.execute(sql_cmd)
                query = c.fetchall()

                for item in query:
                     (filePath, serverID, timeStamp, modType) = item
                     if not filePath in map(lambda x: x['local_path'], fileList) and not modType == 'deleted':
                         try:
                             os.remove('oneDir/'+filePath)
                         except:
                             None
                         wand = conn.cursor()
                         avada_kedavra = ("delete from fileData where file_path = ?")
                         wand.execute(avada_kedavra, (filePath,))
                         conn.commit()

    @staticmethod
    def command_line():
        sync = allEvents.syncing
        while True:
            print 'Enter a number to perform the corresponding task'
            if (sync == 1):
                print '1: Turn automatic sync off'
            else:
                print '1: Turn automatic sync on'

            num = int(raw_input())

            if num == 1:
                if sync == 1:
                    allEvents.syncing = 0
                    sync = 0
                else:
                    allEvents.syncing = 1
                    sync = 1
                    EventHandler.sync_now()
            else:
                print "Invalid Entry. Enter '1'"

def sync_run(a, b):
    while True:
       # print "sync value "+ str(allEvents.syncing)
        time.sleep(20)
        if allEvents.syncing == 1:
            EventHandler.sync_now()

def start_commandLine(a, b):
    EventHandler.command_line()

def start_eventHandler(a, b):
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
    #handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    
    TOKEN = getTokens.get_token()
    #print "just got token" + TOKEN
    EventHandler.sync_now()

    # EventHandler.command_line()

    event_handler = EventHandler()
    thread.start_new_thread(start_eventHandler, (None, None))
    #print "2nd thread"

    #thread.start_new_thread(start_commandLine, (None, None))
    #print "AYO out of sync"

    thread.start_new_thread(sync_run, (None, None))

    start_commandLine(None, None)
