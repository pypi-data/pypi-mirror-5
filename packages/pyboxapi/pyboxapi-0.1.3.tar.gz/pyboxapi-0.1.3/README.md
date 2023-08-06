pyboxapi
========


Usage
=====

```
from pyboxapi import BoxApi

box_api = BoxApi(client_id = 'YOUR_CLIENT_ID', client_secret = 'YOUR_CLIENT_SECRET')

# Allow the client_id above access to whatever account you specify here.
# The reason you need to provide a username and password is for the OAuth2 flow and
# because the access_tokens only live for 1 hour and refresh token for 14 days.
box_api.obtain_access_token(username = 'user@example.com', password = 'examplepassword')

# Alternatively set the access_token yourself
box_api.set_access_token(token="exampletoken123")

items = box_api.get_folders_items(folder_id=1234567890)

f = open('example.csv')
files = {
  'example.csv' : f
}

# Updating a file
box_api.create_files_content(file_id = box_file['id'], parent_id=folder_id, name='example.csv', files=files)

# Uploading a new file
box_api.create_file_content(parent_id=folder_id, name='example.csv', files=files)

```
