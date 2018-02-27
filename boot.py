import gc
import machine
import network
import sys
import uasyncio as asyncio
import uos
import uio

import hashfile
from deaweb import Server, Response
import settings

try:
    import wlog
    from wlog import log
except Exception as e:
    print(e)


gc.collect()
app = Server()

@app.handler('/upload')
def upload(request):
    filename = request.get('filename')
    if not filename:
        return 'filename param not provided'
    filehash = request.get('filehash')
    if not filehash:
        return 'filehash param not provided'

    total_read = 0
    size = int(request.headers.get('Content-Length', 0))
    block_size = 128

    file_size_reopen = 1024
    reopen_every_n_block = int(file_size_reopen/128)
    if reopen_every_n_block <= 0:
        reopen_every_n_block = 1

    try:
        log('')
        f = open(filename+'_tmp', 'wb')
        while total_read < size:
            if total_read+block_size >= size:
                block_size = size-total_read

            read_buffer = await request.reader.read(block_size)
            f.write(read_buffer)

            block_read = int(total_read/block_size)
            if block_read % reopen_every_n_block == 0:
                f.close()
                f = open(filename+'_tmp', 'ab')
                gc.collect()

            total_read += len(read_buffer)
            if total_read % 1024 == 0:
                log('\r{:>6.2f}% {:0.2f}/{:0.2f} KB - {} ... '.format(total_read/size*100, total_read/1024, size/1024, filename))
        log(' done!')
        f.close()

        uos.rename(filename+'_tmp', filename)
        hashfile.put_filehash(filename, filehash, True)

        return 'ok'
    except Exception as e:
        log(exception_traceback_string(e))
        return 'failed'

@app.handler('/hashfile')
def hash(request):
    gc.collect()
    try:
        with open('.hashfile', 'r') as f:
            data = f.read()
    except Exception as e:
        log(exception_traceback_string(e))
        data = 'error'

    if not data.strip():
        data = 'empty'

    return data

@app.handler('/reset')
def reset(request):
    await Response('ok', request=request).awrite()
    await asyncio.sleep(0.5)
    log('Got reset request')
    machine.reset()

@app.handler('/ping')
def ping(request):
    return 'pong'

def exception_traceback_string(exc):
    buf = uio.StringIO()
    sys.print_exception(exc, buf)
    return buf.getvalue()

def main():
    global _ip

    gc.collect()
    _ip = connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)

    gc.collect()
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(wlog.logger.start())
        log('Logger initialized')
        asyncio.ensure_future(app.make_server('0.0.0.0', 80))
        log('Server initialized')

        gc.collect()
        try:
            loop.run_until_complete(run())
        except Exception as e:
            log(exception_traceback_string(e))
        while True:
            try:
                loop.run_forever()
            except Exception as e:
                log(exception_traceback_string(e))
        loop.close()
    except Exception as e:
        log(exception_traceback_string(e))


async def notify_memory(delay=5):
    while True:
        gc.collect()
        log('FM: {:0.2f} KB'.format(gc.mem_free()/1024))
        await asyncio.sleep(delay)

async def run():
    log('All initialized')

    try:
        asyncio.ensure_future(notify_memory())
        import app
        asyncio.ensure_future(app.main())
        import discovery
        asyncio.ensure_future(discovery.DiscoveryServer(local_ip=_ip).start())
    except Exception as e:
        log(exception_traceback_string(e), important=True)

    while True:
        await asyncio.sleep(1)

def connect(ssid, password):
    log('Connecting to "{}"... '.format(ssid), end='')
    client = network.WLAN(network.STA_IF)
    client.active(True)
    client.connect(ssid, password)

    while not client.isconnected():
        pass
    log('done')
    
    ip = client.ifconfig()[0]
    log('IP: {}'.format(ip))

    return ip


if __name__ == '__main__':
    main()
