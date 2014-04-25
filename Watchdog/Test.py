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

from allEvents import SpecificEventHandler

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

database = 'fileData.db'
specific = SpecificEventHandler()
SERVER = 'localhost:8000'
TOKEN = None


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


    @staticmethod
    def get_token():
      token = None

      while not token:
        username = raw_input('Enter your username: ')
        password = raw_input('Enter your password: ')

        post_data = {'name': username, 'password': password}
        r = requests.post('http://' + SERVER + '/tokens/login/', data=post_data)

        if r.status_code == 200:
          json_data = r.json()
          if json_data['success']:
            print 'Login successful!'
            token = json_data['token']
            return token
          else:
            print 'Login was not successful!'
        else:
          print 'Uh oh, status code was not 200!'

          with open('debug_gettoken.html', 'w') as f:
            f.write(r.text)


    @staticmethod
    def sync_now():
       r = requests.get("http://localhost:8000/sync/?token=%s" %TOKEN)
       fileList = r.json()
       for item in fileList:
           print item
           file_name = item["local_path"]
           timeS= item["last_modified"]
           tstamp = dateutil.parser.parse(timeS).replace(tzinfo = None)
           sId = item["id"]
           mod_type = "modified"


           conn = sqlite3.connect(database)
           with conn:
            c = conn.cursor()

            c.execute('''select file_path, date_stamp from fileData where file_path = ?''', (file_name,))
            query = c.fetchall()
            conn.commit()
            print query
            if not query:
                download = requests.get("http://localhost:8000/sync/%d/serve_file?token=%s" %(sId, TOKEN))
                fileCont = download.text
                with open (file_name, 'w') as f:
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
                    print ts
                    lastMod = dateutil.parser.parse(ts).replace(tzinfo = None)
                    print lastMod
                    conn.commit()
                    if tstamp == lastMod:
                        1

                    elif tstamp > lastMod:
                        download = requests.get("http://localhost:8000/sync/%d/serve_file?token=%s" %(sId,TOKEN))
                        fileCont = download.text
                        with open (file_name, 'w') as f:
                            f.write(fileCont)

                        conn = sqlite3.connect(database)
                        with conn:
                            c = conn.cursor()
                            sql_cmd = "update fileData set date_stamp = ?, modification_type = ? where file_path = ?"
                            c.execute(sql_cmd, (timeS, mod_type, file_name))
                            conn.commit()

                    elif lastMod > tstamp:
                         with open(file_name, 'r') as f:
                            file_cont = f.read()
                         params = {'token':TOKEN, "last_modified": lastMod, 'file_data': file_cont}
                         upL = requests.post("http://localhost:8000/sync/%d/update_file/" %sId, data = params)
                         code = upL.status_code
                         print code

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

            print

if __name__ == "__main__":
    TOKEN = EventHandler.get_token()
    #
    # EventHandler.command_line()

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