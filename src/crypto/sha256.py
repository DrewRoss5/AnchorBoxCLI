from Crypto.Hash import SHA256

def sha256_hash(plaintext: bytes):
    sha_hash = SHA256.new()
    sha_hash.update(plaintext)
    return sha_hash.digest()