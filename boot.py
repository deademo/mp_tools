import gc
import network
import picoweb
import uasyncio as asyncio
import machine
import uos
try:
    import wlog
    from wlog import log
except Exception as e:
    print(e)

gc.collect()
app = picoweb.WebApp(__name__)

@app.route("/upload")
def upload(req, resp):

    req.parse_qs()
    params = req.form

    if 'filename' in params and len(params['filename']):
        filename = params['filename'][0]
    else:
        data = 'filename param not provided'
        await picoweb.start_response(resp, headers={'Content-Length': str(len(data))})
        await resp.awrite(data)
        gc.collect()

    total_read = 0
    size = int(req.headers[b"Content-Length"])
    block_size = 128

    try:
        log('')
        with open(filename+'_tmp', 'wb') as f:
            while total_read < size:
                if total_read+block_size >= size:
                    block_size = size-total_read

                read_buffer = await req.reader.read(block_size)
                f.write(read_buffer)

                total_read += len(read_buffer)
                log('\rDownloading file "{}": {:>6.2f}% {:0.2f}/{:0.2f} KB ... '.format(filename, total_read/size*100, total_read/1024, size/1024), end='')
            log(' done!')


        data = 'ok'
        await picoweb.start_response(resp, headers={'Connection': 'close', 'Content-Length': str(len(data))})
        await resp.awrite(data)

        uos.rename(filename+'_tmp', filename)
    except:
        data = 'failed'
        await picoweb.start_response(resp, headers={'Connection': 'close', 'Content-Length': str(len(data))})
        await resp.awrite(data)
    gc.collect()

@app.route("/reset")
def reset(req, resp):
    data = 'ok'
    await picoweb.start_response(resp, headers={'Connection': 'close', 'Content-Length': str(len(data))})
    await resp.awrite(data)
    await resp.aclose()
    await asyncio.sleep(0.5)
    log('Got reset request')
    machine.reset()

def main():
    gc.collect()
    connect('dea', '25801234d')

    gc.collect()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(app.make_task('0.0.0.0', 80))
    asyncio.ensure_future(run())
    try:
        asyncio.ensure_future(wlog.logger.start())
    except Exception as e:
        print(e)
    loop.run_forever()
    loop.close()

async def run():
    log('All initialized')
    while True:
        log('Free memory: {:0.2f} KB'.format(gc.mem_free()/1024))
        log('Hey, seems like all works!')
        await asyncio.sleep(3)
    # await app.make_task('0.0.0.0', 80)

def connect(ssid, password):
    log('Connecting to "{}"... '.format(ssid), end='')
    client = network.WLAN(network.STA_IF)
    client.active(True)
    client.connect(ssid, password)

    while not client.isconnected():
        pass
    log('done')


if __name__ == '__main__':
    main()
