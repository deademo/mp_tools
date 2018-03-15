import asyncio
import glob
import hashlib
import os
import requests
import sys
import time

import discovery

import webrepluploader


_client = None


try:
    ip = discovery.first()
except discovery.NotFound:
    ip = '192.168.1.100'
    print('No esp found, tring to send to {}'.format(ip))


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


async def upload(ip, filename, content, port=8266, timeout=20, hashfile={}):
    global _client

    filehash = hashlib.md5()
    filehash.update(content)
    filehash = filehash.hexdigest()

    if hashfile.get(filename) != filehash:
        await webrepluploader.upload(ip, filename, client=_client)
        return True
    else:
        return False


async def main():
    global _client

    if not _client:
        _client = webrepluploader.WebREPLUploader(ip)
        _client.print_percent_inline = True
        await _client.connect()

    # hashfile = get_hashfile()
    hashfile = {}
    start_time = time.time()

    f = lambda x: glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), x))

    # higher - more priority
    buffer_files = [
        # f("*.mpy"), #TODO: byte files not supported at this moment 
        f("*.py"),
    ]

    files = {}
    for files_chunk in buffer_files[::-1]:
        for file in files_chunk:
            file_without_extension = '.'.join(file.split('.')[:-1])
            files[file_without_extension] = file
    files = list(sorted(list(files.values())))

    any_file_uploaded = False
    print('Uploading {} files to esp on {}'.format(len(files), ip))
    for i, file_name in enumerate(files):
        with open(file_name, 'rb') as f:
            if await upload(ip, file_name, f.read(), hashfile=hashfile):
                print(' done', flush=True)
                any_file_uploaded = True
            else:
                print(' not needed', flush=True)

    if any_file_uploaded:
        print('Restarting esp... ', end='', flush=True)
        await _client.restart()
        print('done', flush=True)
    await _client.close()
    print('Done for {:0.2f} s'.format(time.time() - start_time), flush=True)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
