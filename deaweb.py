try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class Server:
    handler_404 = lambda *_, **__: Response(body='Not found', status_code=400)

    def __init__(self, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._handlers = {}


    def handler(self, path):
        def make_handler(handler):
            self._handlers[path] = handler
            return handler
        return make_handler


    async def server_handler(self, reader, writer):
        request = Request(reader)
        await request.read_headers()
        response = self._handlers.get(request.path, self.handler_404)(request)

        if not isinstance(response, Response):
            response = Response(response)
        response.request = request
        await response.awrite(writer)


    def add_handler(self, path, handler):
        self._handlers[path] = handler


    def start_server(self, ip="0.0.0.0", port=8080):
        asyncio.ensure_future(asyncio.start_server(self.server_handler, ip, port), loop=self.loop)


class Request:
    def __init__(self, reader, *, loop=None):
        self.loop = loop
        self._reader = reader
        self.headers = None
        self.method = None
        self.path = None
        self.protocol = None
        self.query_params = {}


    async def read_headers(self):
        self.headers = {}

        # First request line
        line = await self._reader.readline()
        self.method, path, self.protocol = line.split()

        # Splitting path and query string
        path = path.split(b'?', 1)
        self.path = '/'+path[0].strip(b'/').decode()
        if len(path) > 1:
            query_string = path[1]
            self.query_params = parse_qs(query_string.decode())

        # Do ... while headers provided
        line = await self._reader.readline()
        while line != b"\r\n":
            k, v = line.split(b":", 1)
            self.headers[k.decode()] = v.decode().strip()
            line = await self._reader.readline()

        return self.headers


class Response:
    __response_template = (""
        "HTTP/1.1 {status_code} NA\r\n"
        "Server: micropython\r\n"
        "Content-Type: {content_type}\r\n"
        "Content-Length: {content_length}\r\n"
        "Connection: closed\r\n"
        "\r\n")


    def __init__(self, body=None, status_code=200):
        self.body = body
        self.status_code = status_code
        self.request = None # sets outside the class


    async def awrite(self, writer):
        async def __write(data):
            if hasattr(writer, 'awrite'):
                await writer.awrite(data.encode())
            else:
                writer.write(data.encode())

        headers_values = {
            'content_length': self.content_length,
        }
        headers_values.update(self.default_headers)
        await __write(self.__response_template.format(**headers_values))

        if self.body:
            await __write(self.body+"\r\n")

    # TODO: rename, because status_code is default values, not default header
    @property
    def default_headers(self):
        return {
            'status_code': self.status_code,
            'content_type': 'text/html',
        }

    @property
    def content_length(self):
        return len(self.body) if self.body else '0'


def unquote_plus(s):
    s = s.replace("+", " ")
    arr = s.split("%")
    arr2 = [chr(int(x[:2], 16)) + x[2:] for x in arr[1:]]
    return arr[0] + "".join(arr2)


def parse_qs(s):
    res = {}
    if s:
        pairs = s.split("&")
        for p in pairs:
            vals = [unquote_plus(x) for x in p.split("=", 1)]
            if len(vals) == 1:
                vals.append(True)
            if vals[0] in res:
                res[vals[0]].append(vals[1])
            else:
                res[vals[0]] = [vals[1]]
    return res


def main():
    app = Server()

    @app.handler('/')
    def hello(request):
        return 'Hello, world!'

    app.start_server()
        
    app.loop.run_forever()
    app.loop.close()    


if __name__ == '__main__':
    main()
