import os
import sys
import json
from getpass import getpass
from requests import RequestException

import utils.api as api
from utils.user import User
from utils.helpers import str_dict

# size to indicate a directory in LS entries
DIR_SIZE = -1

# indexing for LS entries
PATH_INDEX = 0
TYPE_INDEX = 1
SIZE_INDEX = 2

# parses a command and returns a string to print to the user
def parse_command(command: str, user: User, server_addr: str) -> str:
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
                return 'Error: This command accepts exactly two arguments'
            src_path, dst_path = args[0], args[1]
            if not os.path.exists(src_path):
                return 'Error: Could not find the source file. Does it exist?'
            # TODO: Validate the destination path
            if os.path.isdir(src_path):
                success = api.upload_directory(server_addr, src_path, dst_path, user)
            else:
                success = api.upload_file(server_addr, src_path, dst_path, user)
            if success:
                return 'File upload successful'
            return 'File upload failed'
        
        case 'download':
            if len(args) != 2:
                return 'Error: This command accepts exactly two argument'
            server_path, local_path = args
            # validate the local path
            if not ((local_path.startswith('/') and os.path.exists (local_path)) or os.path.exists(f'{os.getcwd()}/{os.path.dirname(local_path)}')) : 
                return 'Error: Invalid download destination'
            if api.download_file(server_addr, server_path, local_path, user):
                return('File download successful')
            return 'File download failed'
        
        case 'ls':
            if len(args) == 1:
                path = args[0]
            elif len(args) > 1:
                return 'Error: This command accepts at most one argument'
            else:
                path = ''
            entries = api.list_dir(server_addr, path, user)
            output = [f'{"Path: ".ljust(40)}{"Type: ".ljust(40)}{"Size On AnchorBox (Bytes): "}', ]
            for entry in entries:
                size_str = '' if entries[SIZE_INDEX] == DIR_SIZE else str(entries[SIZE_INDEX])
                output.append(f'{entry[PATH_INDEX].ljust(40)}{entry[TYPE_INDEX].ljust(40)}{size_str}')
            return('\n'.join(output))
        
        case 'mkdir':
            if len(args) != 1:
                return 'Error: This command accepts at most one argument'
            dir_name = args[0]
            api.make_dir(server_addr, dir_name, user)
            return ''

        case 'rm':
            if len(args) != 1:
                return 'Error: This command accepts exactly one argument'
            path= args[0]
            api.delete_file(server_addr, path, user)
            return ''
        
        case 'syshealth':
            if len(args) == 0:
                info_type = 'all'
            elif len(args) > 1:
                return 'Error: This command accepts at most one argument'
            else:
                if args[0] not in ('temp', 'memory', 'storage', 'all'):
                    return 'Error: Unrecognized info type'
                info_type = args[0]
            response = api.get_sys_health(server_addr, info_type, user)
            return str_dict(response)

        case 'exit':
            print('Goodbye!')
            sys.exit(0)

        case 'clear':
            os.system('cls')
            return ''
        
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
        try:
            output = parse_command(command, user, server_addr)
            if output:
                print(output)
        except RequestException as e:
            print(f'Error: {e}')
               
if __name__ == '__main__':
    main()