import os

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
    for entry in os.listdir(path_name):
        entry = f'{path_name}/{entry}'
        print(entry)
        if os.path.isdir(entry):
            generate_dir_list(base_path, entry, files)
        else:
            files.append(('upload_files', (f'{entry.removeprefix(base_path)}', open(f'{entry}', 'rb'))))
