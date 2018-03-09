import gc
import uos

SKIP_COMPILED = ['main', 'boot']


def read_hashfile_raw(filename='.hashfile'):
    gc.collect()
    try:
        with open('.hashfile', 'r') as f:
            for line in f.readline():
                yield line
    except OSError as e:
        pass


def read_hashfile(separator=': '):
    gc.collect()

    file_map = {}
    for line in read_hashfile_raw():
        splitted_line = line.split(separator)
        filehash = splitted_line[-1]
        filename = separator.join(splitted_line[:-1])
        file_map[filename] = filehash
    return file_map


def update_hashfile(filename, filehash):
    remove_basename = ".".join(filename.split(".")[:-1])
    remove_ext = filename.split(".")[-1]
    removed_local_filename = None
    if remove_basename not in SKIP_COMPILED:
        for local_filename in uos.listdir():
            local_basename = ".".join(local_filename.split(".")[:-1])
            local_ext = local_filename.split(".")[-1]
            if remove_basename == local_basename and remove_ext != local_ext:
                uos.remove(local_filename)
                removed_local_filename = local_filename

    file_map = read_hashfile()
    if file_map.get(removed_local_filename):
        remove_filehash(removed_local_filename, file_map=file_map)
    put_filehash(filename, filehash, True, file_map=file_map) 


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
