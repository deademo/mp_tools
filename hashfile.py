import gc


def read_hashfile_raw(filename='.hashfile'):
    try:
        with open('.hashfile', 'r') as f:
            content = f.read()
    except OSError as e:
        if 'ENOENT' in str(e):
            content = ''
        else:
            raise

    return content


def read_hashfile(separator=': '):
    gc.collect()
    content = read_hashfile_raw()
    lines = [x for x in content.split('\n') if x]

    file_map = {}
    for line in lines:
        splitted_line = line.split(separator)
        filehash = splitted_line[-1]
        filename = separator.join(splitted_line[:-1])
        file_map[filename] = filehash
    return file_map


def write_hashfile(file_map, separator=': '):
    gc.collect()
    with open('.hashfile', 'w+') as f:
        for filename, filehash in file_map.items():
            f.write('{}: {}\n'.format(filename, filehash))


def remove_filehash(filename, file_map=None):
    if not file_map:
        file_map = read_hashfile()
    if filename not in file_map:
        return False
    del file_map[filename]
    write_hashfile(file_map)
    return True


def filehash_equal(filename, filehash, file_map=None):
    if not file_map:
        file_map = read_hashfile()
    return file_map.get(filename) == filehash


def put_filehash(filename, filehash, check=False, file_map=None):
    if check:
        file_map = read_hashfile()
        check_result = filehash_equal(filename, filehash, file_map)
        if check_result:
            return False
    if check and not check_result:
        remove_filehash(filename, file_map)
    with open('.hashfile', 'a+') as f:
        f.write('{}: {}\n'.format(filename, filehash))
    return True
