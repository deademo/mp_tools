import glob
import hashlib
import os
import requests
import sys
import time

import discovery


try:
    ip = discovery.first()
except discovery.NotFound:
    print('No esp found')
    sys.exit()

request_template = 'http://{ip}:{port}/upload?filename={filename}'
port = 80


def get_hashfile(separator=': '):
    error = None
    for _ in range(5):
        try:
            response = requests.get('http://{}:{}/hashfile'.format(ip, port), timeout=5)
            content = response.text.strip()
        except Exception as e:
            error = e
            print(e)
            content = 'error'
        if content == 'error':
            continue
    if content == 'error' and error:
        raise error
    elif content == 'error' and not error:
        raise Exception('ESP returted error')
    lines = [x for x in response.text.split('\n') if x]

    file_map = {}
    for line in lines:
        splitted_line = line.split(separator)
        filehash = splitted_line[-1]
        filename = separator.join(splitted_line[:-1])
        file_map[filename] = filehash

    return file_map


def upload(ip, filename, content, port=80, timeout=20, hashfile={}):
    filehash = hashlib.md5()
    filehash.update(content)
    filehash = filehash.hexdigest()
    url = 'http://{}:{}/upload?filename={}&filehash={}'.format(ip, port, filename, filehash)

    if hashfile.get(filename) != filehash:
        response = requests.post(url, data=content, timeout=timeout)
        return True
    else:
        return False


def main():
    hashfile = get_hashfile()
    start_time = time.time()

    f = lambda x: glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), x))

    # higher - more priority
    buffer_files = [
        f("*.mpy"), 
        f("*.py"),
    ]

    files = {}
    for files_chunk in buffer_files[::-1]:
        for file in files_chunk:
            file_without_extension = '.'.join(file.split('.')[:-1])
            files[file_without_extension] = file
    files = list(sorted(list(files.values())))

    any_file_uploaded = False
    print('Starting uploading {} files to esp on {}'.format(len(files), ip))
    for i, file_name in enumerate(files):
        print('Uploading "{}"...'.format(file_name), end='', flush=True)

        with open(file_name, 'rb') as f:
            if upload(ip, os.path.basename(file_name), f.read(), hashfile=hashfile):
                print(' done', flush=True)
                any_file_uploaded = True
            else:
                print(' not needed', flush=True)

    if any_file_uploaded:
        try:
            print('Restarting esp... ', end='', flush=True)
            requests.get('http://{}:{}/reset'.format(ip, port), timeout=3)
            print('done', flush=True)
        except:
            pass
    print('Done for {:0.2f} s'.format(time.time() - start_time), flush=True)


if __name__ == '__main__':
    main()