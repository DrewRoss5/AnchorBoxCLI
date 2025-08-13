import requests
import base64
import json

from utils.user import User

# runs a specified post request, and returns the JSON respons, raising an error if the status code is
# not 200, or if the request was unseuccessful
def post_request(server_addr: str, data: dict) -> dict:
    res = requests.post(server_addr, data=data)
    if res.status_code != 200:
        raise requests.RequestException(f'Failed to reach the server\nStatus Code: {res.status_code}')
    response = json.loads(res.content)
    if response['success'] == False:
        raise requests.RequestException(f'Invalid Request: {response["message"]}')
    return response

# recieves an RSA challenge from the Anchor and creates a signature to use for future authentication
def rsa_authenticate(server_addr: str,  user: User) -> None:
    response = post_request(f'{server_addr}/auth/rsa', {'username': user.name})
    user.challenge_signature = user.key_pair.sign(base64.b64decode(response["message"]))

# recieves an authentication token from the server
def token_authenticate(server_addr: str, user: User) -> None:
    response = post_request(f'{server_addr}/auth/token', {'username': user.name, 'password': user.password})
    user.token = base64.b64decode(response['message'])

# a simple login test
def auth_test(server_addr: str, auth_type: str, user: User) -> bool:
    token = {'rsa': user.challenge_signature, 'token': user.token}[auth_type]
    payload = {'username': user.name, 'token': token, 'auth_type': auth_type}
    try:
        post_request(f'{server_addr}/auth_test', payload)
        return True
    except requests.RequestException:
        return False