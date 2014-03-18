import requests
import json


def list_users():
  r = requests.get('http://127.0.0.1:8000/users/')
  users = r.json()

  print 'There are %d users' % len(users)

  for user in users:
    print json.dumps(user)


def create_user():
  username = raw_input('Enter a username: ')
  password = raw_input('Enter a password: ')

  post_data = {'name': username, 'password': password}

  r = requests.post('http://127.0.0.1:8000/users/create/', data=post_data)
  json_response = r.json()

  if json_response['success']:
    print 'Successfully created an account named %s' % username
  else:
    print 'Failed to create an account (%d)' % json_response['error']['code']
    print json_response['error']['message']


def delete_user():
  user_id = int(raw_input('Enter a user id: '))
  api_endpoint = 'http://127.0.0.1:8000/users/%d/delete/' % user_id
  r = requests.delete(api_endpoint)

  if r.status_code == 200:
    print 'Successfully deleted the user'
  else:
    print 'Could not delete the user'


def start_cli():
  while True:
    print 'Enter a number to perform the corresponding task'
    print '1: List user accounts'
    print '2: Create a user account'
    print "3: Delete a user's account"
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
    else:
      exit(1)

    print


if __name__ == '__main__':
  start_cli()
