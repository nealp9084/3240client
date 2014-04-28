__author__ = 'morganPietruszka, meganBishop'

#import logging
#import os
#import datetime
#import sys
#import time
#import sqlite3
import requests
import json
#import dateutil.parser

#from allEvents import SpecificEventHandler

#from watchdog.events import LoggingEventHandler
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler

#database = 'fileData.db'
#specific = SpecificEventHandler()
SERVER = '172.27.123.207:8000'
TOKEN = None



def get_token():
   global TOKEN  
   token = None

   if TOKEN:
       return TOKEN

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
         #return token

         TOKEN = token
         return TOKEN
       else:
         print 'Login was not successful!'
     else:
       print 'Uh oh, status code was not 200!'

     with open('debug_gettoken.html', 'w') as f:
       f.write(r.text)
