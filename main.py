import gc
import machine
import sys
import uasyncio as asyncio
import uio

import settings
import wifi

try:
    
    gc.collect()
   
except:
    pass

try:
    import wlog
    from wlog import log
except Exception as e:
    print(e)


SKIP_COMPILED = ['main', 'boot']


def exception_traceback_string(exc):
    buf = uio.StringIO()
    sys.print_exception(exc, buf)
    return buf.getvalue()


def process_requirements():
    gc.collect()
    installed_modules = dir('modules')
    if 'deaweb' not in installed_modules:
        import upip
        upip.install('deaweb')
        machine.reset()


def main():
    gc.collect()
    wifi.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)
    # process_requirements()

    gc.collect()
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(wlog.logger.start())
        log('Logger initialized')
        gc.collect()
        import upload
        asyncio.ensure_future(upload.app.make_server('0.0.0.0', 80))
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
        asyncio.ensure_future(discovery.DiscoveryServer(local_ip=wifi.get_ip()).start())
    except Exception as e:
        log(exception_traceback_string(e), important=True)

    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    main()
