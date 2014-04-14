import requests
import json
from datetime import datetime

SERVER = '127.0.0.1:8000' # 172.27.123.220


def list_users():
  r = requests.get('http://' + SERVER + '/users/')
  users = r.json()

  print 'There are %d users' % len(users)

  for user in users:
    print json.dumps(user)


def show_user_details():
  user_id = int(raw_input('Enter a user id: '))
  api_endpoint = 'http://' + SERVER + '/users/%d/' % user_id
  r = requests.get(api_endpoint)

  if r.status_code == 200:
    print r.text
  else:
    print 'Could not get user details'


def create_user():
  username = raw_input('Enter a username: ')
  password = raw_input('Enter a password: ')

  post_data = {'name': username, 'password': password}

  r = requests.post('http://' + SERVER + '/users/create/', data=post_data)
  json_response = r.json()

  if json_response['success']:
    print 'Successfully created an account named %s' % username
  else:
    print 'Failed to create an account (%d)' % json_response['error']['code']
    print json_response['error']['message']


def delete_user():
  user_id = int(raw_input('Enter a user id: '))
  api_endpoint = 'http://' + SERVER + '/users/%d/delete/' % user_id
  r = requests.delete(api_endpoint)

  if r.status_code == 200:
    print 'Successfully deleted the user'
  else:
    print 'Could not delete the user'


def upload_file():
  with open('some_file.txt') as f:
    params = {'current_user': 1, 'local_path': '/var/junk',
              'last_modified': '2014-03-24 18:14:11+00:00', 'file_data': f.read()}

    r = requests.post('http://' + SERVER + '/sync/create_server_file/', data=params)

    if r.status_code == 200:
      json_response = r.json()
      if json_response['success']:
        print 'Successfully uploaded the file!'
      else:
        print 'Failed to upload the file (%d)' % json_response['error']['code']
        print json_response['error']['message']
    else:
      print 'Failed to upload the file! Server responded with %d.' % r.status_code

    html = r.text
    with open('debug_uploadfile.html', 'w') as f:
      f.write(html)

def get_file():
  # read the file with file id 1
  file_id = 1
  api_endpoint = 'http://' + SERVER + '/sync/%d/serve_file/?current_user=1' % file_id
  r = requests.get(api_endpoint)
  print 'Downloaded the file'
  html = r.text
  with open('debug_getfile.html','w') as f:
    f.write(html)


def update_file():
  # update the file with file id 1
  file_id = 1
  api_endpoint = 'http://' + SERVER + '/sync/%d/update_file/' % file_id

  with open('another_file.txt') as f:
    filedata = f.read()

  params = {'current_user': 1,
            'last_modified': str(datetime.now()),
            'file_data': filedata}
  r = requests.post(api_endpoint, data=params)

  if r.status_code == 200:
      json_response = r.json()
      if json_response['success']:
        print 'Successfully updated the file!'
      else:
        print 'Failed to update the file (%d)' % json_response['error']['code']
        print json_response['error']['message']
  else:
    print 'Failed to update the file! Server responded with %d.' % r.status_code

  html = r.text
  with open('debug_updatefile.html', 'w') as f2:
    f2.write(html)


def delete_file():
  file_id = 1
  api_endpoint = 'http://' + SERVER + '/sync/%d/delete_file/?current_user=1' % file_id
  r = requests.delete(api_endpoint)
  html = r.text
  with open('debug_deletefile.html','w') as f:
    f.write(html)


def start_cli():
  while True:
    print 'Enter a number to perform the corresponding task'
    print '1: List user accounts'
    print '2: Create a user account'
    print "3: Delete a user's account"
    print "4: Show a user's details"
    print "5: Create a file on the server"
    print "6: Get a file from the server"
    print "7: Update a file on the server"
    print "8: Delete file from the server"
    print '0: Quit'

    num = int(raw_input())

    if num == 0:
      exit(0)
    elif num == 1:
      list_users()
    elif num == 2:
      create_user()
    elif num == 3:
      delete_user()
    elif num == 4:
      show_user_details()
    elif num == 5:
      upload_file()
    elif num == 6:
      get_file()
    elif num == 7:
      update_file()
    elif num == 8:
      delete_file()
    else:
      exit(1)

    print


if __name__ == '__main__':
  start_cli()
