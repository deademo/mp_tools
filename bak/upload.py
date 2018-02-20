import glob
import requests
import time


request_template = 'http://{ip}:{port}/upload?filename={filename}'
ip = '192.168.1.100'


def upload(ip, filename, content, port=80, restart=False):
    url = 'http://{}:{}/upload?filename={}'.format(ip, port, filename)
    if restart:
        url += '&restart=1'
    requests.post(url, data=content, headers={'Content-Type': 'multipart/form-data'})

start_time = time.time()
files = glob.glob('*.lua')
print('Starting uploading {} files to esp on {}'.format(len(files), ip))
for i, file_name in enumerate(files):
    with open(file_name, 'r') as f:
        restart = False
        and_restarting = ''
        if i == len(files) - 1:
            restart = True
            and_restarting = ' and restarting esp'

        print('Uploading "{}"{}...'.format(file_name, and_restarting), end='', flush=True)
        upload(ip, file_name, f.read(), restart=restart)
        print(' done')
print('Done for {:0.2f} s'.format(time.time() - start_time))
