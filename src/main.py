import os
import json
from getpass import getpass
from requests import RequestException

import utils.api as api
from utils.user import User

# parses a command and returns a string to print to the user
def parse_command(command: str, user: User, server_addr: str):
    segments = command.split()
    command = segments[0]
    args = segments[1:]
    match command:
        case 'login':
            if len(args) != 1:
                return 'Error: This command accepts exactly one argument'
            match args[0]:
                case 'rsa':
                    user.login_method = 'rsa'
                    api.rsa_authenticate(server_addr, user)
                    return 'Login successful'
                case 'password':
                    user.login_method = 'token'
                    user.password = getpass('Password: ')
                    api.token_authenticate(server_addr, user)
                    return 'Login successful'
                case _:
                    return f'Unrecognized authentication method: "{args[0]}"'
        
        case 'upload':
            if len(args) != 2:
                return 'Error: This command acceptes exactly two arguments'
            src_path, dst_path = args[0], args[1]
            if not os.path.exists(src_path):
                return 'Error: Could not find the source file. Does it exist?'
            # TODO: Validate the destination path
            if api.upload_file(server_addr, src_path, dst_path, user):
                return 'File upload successful'
            return 'File upload failed'
        
        case 'clear':
            os.system('cls')
            return ' '
        
        case _:
            return f'Error: Unrecognized Command "{command}"'

def main():
    print('⚓ Welcome to AnchorBox CLI! ⚓\n')
    if not os.path.exists('config.json'):
        username = input('Username: ')
        prv_key_path = input('Private Key Path: ')
        server_addr = input('AnchorBox Address: ')
        with open('config.json', 'w') as f:
            json.dump(server_addr, f)
    else:
        with open('config.json') as f:
            username, prv_key_path, server_addr = json.load(f).values()
    user = User(username, prv_key_path)
    while True:
        command = input(f'{username} > ')
        if command.startswith('exit'):
            print('Goodbye!')
            break
        try:
            output = parse_command(command, user, server_addr)
            print(output)
        except RequestException as e:
            print(f'Error: {e}')
            

if __name__ == '__main__':
    main()