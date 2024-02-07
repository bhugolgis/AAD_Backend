def deep_flatten(lst):
    
    flat = []
    print(lst)
    
    while lst:
        val = lst.pop()
        if isinstance(val,list):
            lst.extend(val)
        else:
            flat.append(val)

    return flat


def error_simplifier(error_dict):
    error_key = error = ""
    value = []
    for key,val in error_dict.items():
        error_key = key
        error = val
        break

    if isinstance(error,str):
        if "field" in error:
            return error_key + ", " + error
        return error
    else:
        value = deep_flatten(error)
        if "field" in value:
            return error_key + ", " + value[0]
        return value[0]