import glob
import requests
import time
import os


request_template = 'http://{ip}:{port}/upload?filename={filename}'
ip = '192.168.1.100'
port = 80


def upload(ip, filename, content, port=80, timeout=20):
    url = 'http://{}:{}/upload?filename={}'.format(ip, port, filename)
    requests.post(url, data=content, timeout=timeout)


def main():
    start_time = time.time()
    files = glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "*.py"))
    print('Starting uploading {} files to esp on {}'.format(len(files), ip))
    for i, file_name in enumerate(files):
        print('Uploading "{}"...'.format(file_name), end='', flush=True)

        with open(file_name, 'r') as f:
            upload(ip, os.path.basename(file_name), f.read())
            print(' done', flush=True)
    try:
        print('Restarting esp... ', end='', flush=True)
        requests.get('http://{}:{}/reset'.format(ip, port), timeout=3)
        print('done', flush=True)
    except:
        pass
    print('Done for {:0.2f} s'.format(time.time() - start_time), flush=True)


if __name__ == '__main__':
    main()
