import requests
import json
from datetime import datetime

SERVER = 'localhost:8000'

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


# TODO: this will only work for admins. code should address that.
def list_users():
  r = requests.get('http://' + SERVER + '/users/')
  users = r.json()

  print 'There are %d users' % len(users)

  for user in users:
    print json.dumps(user)


# TODO: this will only work for the current user, and for admins. code should address that.
def show_user_details():
  user_id = int(raw_input('Enter a user id: '))
  api_endpoint = 'http://' + SERVER + '/users/%d/' % user_id
  r = requests.get(api_endpoint)

  if r.status_code == 200:
    print r.text
  else:
    print 'Could not get user details'

    with open('debug_userdetails.html', 'w') as f:
        f.write(r.text)


def show_me():
  token = get_token()

  r = requests.get('http://' + SERVER + '/users/me/?token=%s' % token)

  if r.status_code == 200:
    print r.text
  else:
    print "Failed to show current user's info!"
    with open('debug_showme.html', 'w') as f:
      f.write(r.text)


def create_user():
  username = raw_input('Enter a username: ')
  password = raw_input('Enter a password: ')

  post_data = {'name': username, 'password': password}

  r = requests.post('http://' + SERVER + '/users/create/', data=post_data)

  with open('debug_createuser.html', 'w') as f:
    f.write(r.text)

  json_response = r.json()

  if json_response['success']:
    print 'Successfully created an account named %s' % username
  else:
    print 'Failed to create an account (%d)' % json_response['error']['code']
    print json_response['error']['message']


def delete_user():
  token = get_token()
  user_id = int(raw_input('Enter a user id: '))
  api_endpoint = 'http://' + SERVER + '/users/%d/delete/?token=%s' % (user_id, token)
  r = requests.delete(api_endpoint)

  if r.status_code == 200:
    print 'Successfully deleted the user'
  else:
    print 'Could not delete the user'
    with open('debug_deleteuser.html', 'w') as f:
      f.write(r.text)


def upload_file():
#  FILENAME = 'some_file.txt'
  FILENAME = 'D3_00.png'
  token = get_token()

  with open(FILENAME,'rb') as f:
    params = {'local_path': '/var/junk/%s' % FILENAME,
              'last_modified': '2014-03-24 18:14:11+00:00',
              'file_data': f.read(),
              'token': token}

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

    with open('debug_uploadfile.html', 'wb') as f:
      f.write(r.content)


def get_file():
  # read the file with file id 1
  FILE_ID = 1
  token = get_token()

  api_endpoint = 'http://' + SERVER + '/sync/%d/serve_file/?token=%s' % (FILE_ID, token)
  r = requests.get(api_endpoint)
  print 'Downloaded the file'

  with open('debug_getfile.html','w') as f:
    f.write(r.content)


def update_file():
  # update the file with file id 1
  FILE_ID = 1
  token = get_token()

  api_endpoint = 'http://' + SERVER + '/sync/%d/update_file/' % FILE_ID

  with open('another_file.txt') as f:
    filedata = f.read()

  params = {'last_modified': str(datetime.now()),
            'file_data': filedata,
            'token': token}
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

  with open('debug_updatefile.html', 'w') as f2:
    f2.write(r.text)


def delete_file():
  # delete the file with file id 1
  FILE_ID = 1
  token = get_token()

  api_endpoint = 'http://' + SERVER + '/sync/%d/delete_file/?token=%s' % (FILE_ID, token)
  r = requests.delete(api_endpoint)

  with open('debug_deletefile.html','w') as f:
    f.write(r.text)


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
