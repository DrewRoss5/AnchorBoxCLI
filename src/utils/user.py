import base64
import json

from crypto.rsa import RSAKeyPair

class AuthorizationError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

class User:
    def __init__(self, username: str, key_path: str):
        self.name = username
        self.key_path = key_path
        self.key_pair = RSAKeyPair(key_path)
        self.password = None
        self.token = b' '
        self.challenge_signature = b' '
        self.login_method = None

    def get_token(self):
        if not self.login_method:
            raise AuthorizationError('You must login for this operation')
        return {'rsa': base64.b64encode(self.challenge_signature).decode(), 'token': self.token}[self.login_method]
    
    def save_config(self, server_addr: str):
        user_data = {
             'username': self.name,
             'priv_key_path': self.key_path,
             'anchorbox_addr': server_addr
        }
        with open('config.json', 'w') as f:
            json.dump(user_data, f)
             