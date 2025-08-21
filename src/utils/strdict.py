# returns a stringified version of a dictionary, accounting to the possiblity of nested dictionaries
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
