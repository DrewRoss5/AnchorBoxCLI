from utils.rsa import RSAKeyPair

class User:
    def __init__(self, username: str, key_path: str):
        self.name = username
        self.key_pair = RSAKeyPair(key_path)
        self.password = None
        self.token = None
        self.challenge_signature = None
        self.login_method = None