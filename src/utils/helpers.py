import os
import base64
import secrets
import getpass

from crypto.aes import AESCipher
from crypto.rsa import RSAKeyPair

# returns a stringified version of a dictionary, accounting for the possiblity of nested dictionaries
def str_dict(data: dict, depth: int = 0) -> str:
    left_space = max(map(len, data.keys())) + 5
    out = []
    for k, v in data.items():
        if type(v) == dict:
            out.append(f'{k}:')
            out.append(str_dict(v, depth+1))
        else:
            out.append(f'{"\t"*depth}{(k+":").ljust(left_space)}{v}')
    return '\n'.join(out)

# takes a list and updates with file IO objects in a directory, accounting for the possibility of nested directories
def generate_dir_list(base_path: str, path_name: str, files: list) -> None:
    for entry in map(lambda x: f'{path_name}/{x}', os.listdir(path_name)):
        if os.path.isdir(entry):
            generate_dir_list(base_path, entry, files)
        else:
            files.append(('upload_files', (f'{entry.removeprefix(base_path)}', open(entry, 'rb'))))

# generates a new random password
def generate_password(pw_len: int, include_special: bool) -> str:
    char_bank = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    if include_special:
        char_bank += '!@#$%^&*(){}|/`~,.<>?;:!@#$%^&*(){}|/`~,.<>?;:'
    out = ''
    for i in range(pw_len):
        out += secrets.choice(char_bank)
    return out

# recieves a password, or generates a random one if not provided
def get_new_password() -> str:
    password = getpass('New Password (Leave blank to randomize):')
    if password:
        return password
    pw_len = 0
    include_special = False
    while True:
        len_str = input('Password Length: ')
        if len_str.isdigit() or int(len_str) < 1:
            pw_len = int(len_str)
            break
        print('Please provide a valid integer greater than 0')
    while True:
        tmp_str = input('Include special characters? (y/n)').lower()
        if tmp_str in ('y', 'n'):
            include_special = (tmp_str == 'y')
            break
        else:
            print('Please enter either "Y" or "N"')
    return generate_password(pw_len, include_special)

# decrypts a provided base64-encoded encrypted password
def decrypt_password(key: str, password: str, prv_key: RSAKeyPair):
    aes_key = prv_key.decrypt(base64.b64decode(key))
    pass_cipher = base64.b64decode(password)
    return AESCipher(aes_key).decrypt_authenticated(pass_cipher)