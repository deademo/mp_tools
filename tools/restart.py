import requests


def restart(ip, port):
    print('Restarting... ', end='')
    try:
        requests.get('http://{}:{}/reset'.format(ip, port), timeout=3)
    except:
        pass
    print('done')


def main():
    restart('192.168.1.100', 80)


if __name__ == '__main__':
    main()