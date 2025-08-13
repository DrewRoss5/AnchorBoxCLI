from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

RSA_KEY_SIZE = 4096

class RSAKeyPair:
    def __init__(self, private_pem: str = None, passphrase: str =  None):
        self.prv_key = RSA.import_key(private_pem, passphrase)
        self.pub_key = self.prv_key.public_key()
    
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