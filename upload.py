import gc

gc.collect()
from deaweb import Server, Response, FileResponse
gc.collect()

import machine
import uos
import uasyncio as asyncio

import hashfile
from wlog import log
from main import exception_traceback_string


app = Server()


@app.handler('/upload')
def upload(request):
    filename = request.get('filename')
    if not filename:
        return 'filename param not provided'
    filehash = request.get('filehash')
    if not filehash:
        return 'filehash param not provided'

    log('{} - {:0.2f} KB downloading started'.format(filename, request.content_length))
    result = await request.readinto_safe(filename)

    if not result:
        log('{} - {:0.2f} KB downloading failed'.format(filename, request.content_length))
        return 'failed'
    else:
        log('{} - {:0.2f} KB downloading done'.format(filename, request.content_length))
        hashfile.update_hashfile(filename, filehash)
        return 'ok'

@app.handler('/hashfile')
def hash(request):
    return FileResponse('.hashfile')

@app.handler('/reset')
def reset(request):
    await Response('ok', request=request).awrite()
    await asyncio.sleep(0.5)
    log('Got reset request')
    machine.reset()

@app.handler('/ping')
def ping(request):
    return 'pong'
