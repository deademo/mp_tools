import asyncio


async def main():
    host = '192.168.1.100'
    port = 81
    while True:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
        except:
            continue
        while True:
            try:
                data = await asyncio.wait_for(reader.read(1), timeout=5)
                data = data.decode('utf-8')
                print(data, end='', flush=True)
            except:
                await asyncio.sleep(1)
                break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
