import asyncio
import logging


logging.basicConfig(format='%(asctime)s %(msg)s')
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


async def main():
    host = '192.168.1.100'
    port = 81

    logger.info('Connecting to {}:{}...'.format(host, port))
    was_connected = False
    while True:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
            if not was_connected:
                logger.info('Connected!')
            was_connected = True
        except:
            continue
        _buffer = ''
        while True:
            try:
                data = await asyncio.wait_for(reader.read(10), timeout=5)
                data = data.decode('utf-8')
                _buffer += data
                if '\n' in _buffer:
                    tmp_buffer = _buffer.split('\n')
                    _buffer = ''.join(tmp_buffer[1:])
                    logger.info('[{}:{}] {}'.format(host, port, tmp_buffer[0]))
            except:
                await asyncio.sleep(1)
                break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
