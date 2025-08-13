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
                    api.rsa_authenticate(server_addr, user)
                    return 'Login successful'
                case 'password':
                    if not user.password:
                        user.password = getpass('Password: ')
                    api.token_authenticate(server_addr, user)
                    return 'Login successful'
                case _:
                    return f'Unrecognized authentication method: "{args[0]}"'
        
        case 'auth_test':
            if len(args) != 1:
                return 'Error: This command accepts no arguments'
            if args[0] not in ('rsa', 'token'):
                return f'Unrecognized authentication method: "{args[0]}"'
            if api.auth_test(server_addr, args[0], user):
                return 'Authentication successful'
            return 'Authentication failed'
        
        case _:
            return f'Error: Unrecognized Command "{command}"'

def main():
    print('⚓ Welcome to AnchorBox CLI! ⚓\n')
    username = input('Username: ')
    prv_key_path = input('Private Key Path: ')
    server_addr = input('AnchorBox Address: ')
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