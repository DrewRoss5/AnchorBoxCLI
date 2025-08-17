import requests
import base64
import json
import os

from utils.user import User

# runs a specified post request, and returns the JSON respons, raising an error if the status code is
# not 200, or if the request was unseuccessful
def post_request(server_addr: str, data: dict) -> dict:
    res = requests.post(server_addr, json=data)
    if res.status_code != 200:
        print(f'Content: {res.content}')
        raise requests.RequestException(f'Failed to reach the server\nStatus Code: {res.status_code}')
    response = json.loads(res.content)
    if response['success'] == False:
        raise requests.RequestException(f'Invalid Request: {response["message"]}')
    return response

# recieves an RSA challenge from the Anchor and creates a signature to use for future authentication
def rsa_authenticate(server_addr: str,  user: User) -> None:
    response = post_request(f'{server_addr}/auth/rsa', {'username': user.name, 'password': ''})
    user.challenge_signature = user.key_pair.sign(base64.b64decode(response["message"]))

# recieves an authentication token from the server
def token_authenticate(server_addr: str, user: User) -> None:
    password = user.password
    user.password = None
    response = post_request(f'{server_addr}/auth/token', {'username': user.name, 'password': password})
    user.token = base64.b64decode(response['message'])

# a simple login test
def auth_test(server_addr: str, auth_type: str, user: User) -> bool:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[auth_type]
    payload = {'username': user.name, 'token': token.decode(), 'auth_method': auth_type}
    try:
        post_request(f'{server_addr}/auth_test', payload)
        return True
    except requests.RequestException as e:
        print(f'Error: {e}')
        return False
    
# uploads a file to the anchorbox
def upload_file(server_addr: str, src_path: str, dst_path: str, user: User) -> bool:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method, 'dst-path': dst_path}
    res = requests.post(f'{server_addr}/upload/{user.name}', headers=headers, files={'upload_file': open(src_path, 'rb')})
    if res.status_code != 200:
        print(requests.RequestException(f'Failed to reach the server\nStatus Code: {res.status_code}\n"{res.content}"'))
        return False
    response = json.loads(res.content)
    return response['success']

# retrieves a list of files in a particular path
def list_dir(server_addr: str, path: str, user: User) -> list[tuple[str, str, int]]:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    payload = {'auth': token.decode(), 'auth_type': user.login_method, 'path': path}
    res = post_request(f'{server_addr}/ls/{user.name}', payload)
    # parse the returned 
    out = []
    for name, entry in res['files'].items():
        if entry['type'] == 'dir':
            out.append((name, 'DIR', -1))
        else:
            out.append((name, 'FILE', entry['size']))
    return out