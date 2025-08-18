import os

from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from crypto.sha256 import sha256_hash

AES_KEY_SIZE = 32
HEADER_SIZE = 48
IV_SIZE = 16 



# a wrapper for AES encryption functions, with added authentication
class AESCipher:
    def __init__(self, key: bytes):
        # validate the key
        if len(key) != AES_KEY_SIZE:
            raise ValueError('Invalid AES Key')
        self.key = key

    # encrypts the provided plaintext with a random IV and appends the iv to the start of the ciphertext
    def encrypt(self, plaintext: bytes):
        iv = os.urandom(IV_SIZE)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        return iv + ciphertext
    
    # decrypts plaintexts encrypted with the previous function
    def decrypt(self, ciphertext: bytes):
        iv = ciphertext[:IV_SIZE]
        ciphertext = ciphertext[IV_SIZE:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), AES.block_size)

    # encrypts the provided plaintext, and appends the IV and a checksum of the plaintext
    def encrypt_authenticated(self,  plaintext: bytes, iv: bytes = None) -> bytes:
        # create the IV as nessecary
        if not iv:
            iv = os.urandom(IV_SIZE)
        # create a checksum of the 
        checksum = sha256_hash(plaintext)
        # encrypt the plaintext
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        return iv + checksum + ciphertext
    
    # decrypts the provided plaintext, and validates the checksum, returns None if the checksum cannot be verified 
    def decrypt_authenticated(self, ciphertext: bytes):
        # parse the ciphertext block
        iv = ciphertext[:IV_SIZE]
        checksum = ciphertext[IV_SIZE:HEADER_SIZE]
        ciphertext = ciphertext[HEADER_SIZE:]
        # decrypt the ciphertext
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        # validate the checksum
        plaintext_hash = sha256_hash(plaintext)
        if plaintext_hash == checksum:
            return plaintext
        else: 
            return None