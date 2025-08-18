from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Signature import pkcs1_15

from crypto.sha256 import SHA256

RSA_KEY_SIZE = 4096
RSA_CIPHER_SIZE = 512

class RSAKeyPair:
    def __init__(self, prv_file: str = None, passphrase: str =  None):
        with open(prv_file, 'rb') as f:
            private_pem = f.read()
        self.prv_key = RSA.import_key(private_pem, passphrase)
        self.pub_key = self.prv_key.public_key()
    
    # generates an RSAKeyPair with a random private key
    @classmethod
    def generate_key_pair(self):
        key = RSA.generate(RSA_KEY_SIZE)
        return RSAKeyPair(key.public_key().export_key('PEM'), key.export_key('PEM'))

    # returns a pem-encoded string of the public key
    def export_public_pem(self) -> bytes:
        return self.pub_key.export_key('PEM')

    # returns a pem-encoded string of the private key, complete with an optional passphrase
    def export_private_pem(self, passphrase: str = None) -> bytes:
        return self.prv_key.export_key('PEM', passphrase)
    
    # encrypts plaintext with the public key
    def encrypt(self, plaintext: bytes):
        cipher = PKCS1_v1_5.new(self.pub_key)
        return cipher.encrypt(plaintext)
    
    # decrypts a ciphertext with the private key, returns None if the ciphertext cannot be decrypted
    def decrypt(self, ciphertext: bytes):
        cipher = PKCS1_v1_5.new(self.prv_key)
        return cipher.decrypt(ciphertext, sentinel=None)

    # hashes the plaintext and returns the RSA signature
    def sign(self, plaintext: bytes):
        # hash the plaintext
        message_hash = SHA256.new()
        message_hash.update(plaintext)
        # return the signature of the hash
        signature = pkcs1_15.new(self.prv_key)
        return signature.sign(message_hash)
    
    # attempts to verify a signature given a plaintext, returns true if the signature can be verified, and if not, returns false
    def valid_signature(self, plaintext: bytes, signature: bytes) -> bool:
        # hash the plaintext
        message_hash = SHA256.new()
        message_hash.update(plaintext)
        # verify the plaintext
        verifier = pkcs1_15.new(self.pub_key)
        try:
            verifier.verify(message_hash, signature)
            return True
        except ValueError:
            return False