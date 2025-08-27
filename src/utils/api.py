import requests
import base64
import json

from crypto.rsa import RSA_CIPHER_SIZE
from crypto.aes import AESCipher
from utils.user import User
from utils.helpers import generate_dir_list

# runs a specified post request, and returns the JSON response, raising an error if the status code is
# not 200, or if the request was unsuccessful
def json_request(req_type: str, server_addr: str, data: dict = None, headers: dict = None) -> dict:
    match req_type:
        case 'post':
            res = requests.post(server_addr, json=data, headers=headers)
        case 'get':
            res = requests.get(server_addr, headers=headers)
    if res.status_code != 200:
        raise requests.RequestException(f'Failed to reach the server\nStatus Code: {res.status_code}')
    response = json.loads(res.content)
    if res.headers['result'] != 'OK':
        raise requests.RequestException(response['message'])
    return response

# recieves an RSA challenge from the Anchor and creates a signature to use for future authentication
def rsa_authenticate(server_addr: str,  user: User) -> None:
    response = json_request('post', f'{server_addr}/auth/rsa', data={'username': user.name, 'password': ''})
    user.challenge_signature = user.key_pair.sign(base64.b64decode(response["message"]))

# recieves an authentication token from the server
def token_authenticate(server_addr: str, user: User) -> None:
    password = user.password
    user.password = None
    response = json_request('post', f'{server_addr}/auth/token', data={'username': user.name, 'password': password})
    user.token = base64.b64decode(response['message'])
    
# uploads a file to the anchorbox
def upload_file(server_addr: str, src_path: str, dst_path: str, user: User) -> bool:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method, 'dst-path': dst_path}
    res = requests.post(f'{server_addr}/upload/{user.name}', headers=headers, files={'upload_file': open(src_path, 'rb')})
    if res.status_code != 200:
        raise requests.RequestException(f'Failed to reach the server\nStatus Code: {res.status_code}\n"{res.content}"')
    return res.headers['result'] == 'OK'

# uploads a directory to the anchorbox
def upload_directory(server_addr: str, src_path: str, dst_path: str, user: User) -> bool:
    # generate the file list
    files = []
    generate_dir_list(src_path, src_path, files)
    # send the post request
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method, 'dst-path': dst_path}
    res = requests.post(f'{server_addr}/upload_dir/{user.name}', headers=headers, files=files)
    if res.status_code != 200:
        raise requests.RequestException(f'Failed to reach the server\nStatus Code: {res.status_code}\n"{res.content}"')
    return res.headers['result'] == 'OK'

# retrieves a list of files in a particular path
def list_dir(server_addr: str, path: str, user: User) -> list[tuple[str, str, int]]:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    payload = {'path': path}
    headers = {'auth': token.decode(), 'auth-type': user.login_method}
    res = json_request('post', f'{server_addr}/ls/{user.name}', data=payload, headers=headers)
    # parse the returned 
    out = []
    for name, entry in res['files'].items():
        if entry['type'] == 'dir':
            out.append((name, 'DIR', -1))
        else:
            out.append((name, 'FILE', entry['size']))
    return out

# downloads a file from the anchorbox
def download_file(server_addr: str, server_path: str, local_path: str, user: User) -> bool:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method}
    payload = {'path': server_path}
    res = requests.post(f'{server_addr}/download/{user.name}', json=payload, headers=headers)
    if res.headers['result'] != 'OK':
        return False
    # decrypt the image
    content = res.content
    key_ciphertext = content[:RSA_CIPHER_SIZE]
    file_key = user.key_pair.decrypt(key_ciphertext)
    if not file_key:
        return False
    file_cipher = AESCipher(file_key)
    file_content = file_cipher.decrypt(content[RSA_CIPHER_SIZE:])
    with open(local_path, 'wb') as f:
        f.write(file_content)
    return True

# creates a directory on the anchorbox
def make_dir(server_addr: str, dir_name: str, user: User) -> None:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method}
    payload = {'path': dir_name}
    json_request('post', f'{server_addr}/mkdir/{user.name}', data=payload, headers=headers)

# deletes a specified direcotory or file on the anchorbox
def delete_file(server_addr: str, dir_name: str, user: User) -> None:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method}
    payload = {'path': dir_name}
    json_request('post', f'{server_addr}/rm/{user.name}', data=payload, headers=headers)

# returns specified system health information
def get_sys_health(server_addr: str, info_type: str, user: User) -> dict:
    # ensure the information type is valid
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'username': user.name,'auth': token.decode(), 'auth-type': user.login_method}
    return json_request('get', f'{server_addr}/health/{info_type}', headers=headers)

# creates a password in the password database
def create_password(server_addr: str, pw_name: str, password: str, user: User) -> dict:
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'auth': token.decode(), 'auth-type': user.login_method}
    payload = {'pw_name': pw_name, 'password': password, 'username': user.name}
    return json_request('post', f'{server_addr}/new_pw/{user.name}', data=payload, headers=headers)

# recieves a password from the password database
def get_password(server_addr: str, pw_name: str, user: User):
    token = {'rsa': base64.b64encode(user.challenge_signature), 'token': user.token}[user.login_method]
    headers = {'pw-name': pw_name, 'auth': token.decode(), 'auth-type': user.login_method}
    return json_request('get', f'{server_addr}/get_pw/{user.name}', headers=headers)