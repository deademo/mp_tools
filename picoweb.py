import gc
import sys
import micropython

import ure as re
import uasyncio as asyncio

from wlog import log


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

def start_response(writer, content_type="text/html", status="200", headers=None):
    yield from writer.awrite("HTTP/1.0 %s NA\r\n" % status)
    yield from writer.awrite("Content-Type: ")
    yield from writer.awrite(content_type)
    if not headers:
        yield from writer.awrite("\r\n\r\n")
        return
    yield from writer.awrite("\r\n")
    if isinstance(headers, bytes) or isinstance(headers, str):
        yield from writer.awrite(headers)
    else:
        for k, v in headers.items():
            yield from writer.awrite(k)
            yield from writer.awrite(": ")
            yield from writer.awrite(v)
            yield from writer.awrite("\r\n")
    yield from writer.awrite("\r\n")


class HTTPRequest:

    def __init__(self):
        pass

    def parse_qs(self):
        form = parse_qs(self.qs)
        self.form = form


class WebApp:

    def __init__(self, pkg, routes=None, serve_static=True):
        if routes:
            self.url_map = routes
        else:
            self.url_map = []
        if pkg and pkg != "__main__":
            self.pkg = pkg.split(".", 1)[0]
        else:
            self.pkg = None
        self.mounts = []
        self.inited = False
        self.template_loader = None
        self.headers_mode = "parse"

    def parse_headers(self, reader):
        headers = {}
        while True:
            l = yield from reader.readline()
            if l == b"\r\n":
                break
            k, v = l.split(b":", 1)
            headers[k] = v.strip()
        return headers

    def _handle(self, reader, writer):
        if self.debug:
            micropython.mem_info()

        close = True
        try:
            request_line = yield from reader.readline()
            if request_line == b"":
                print(reader, "EOF on request start")
                yield from writer.aclose()
                return
            req = HTTPRequest()
            request_line = request_line.decode()
            method, path, proto = request_line.split()
            log('%s %s "%s %s"' % (req, writer, method, path))
            path = path.split("?", 1)
            qs = ""
            if len(path) > 1:
                qs = path[1]
            path = path[0]


            app = self
            while True:
                found = False
                for subapp in app.mounts:
                    root = subapp.url
                    print(path, "vs", root)
                    if path[:len(root)] == root:
                        app = subapp
                        found = True
                        path = path[len(root):]
                        if not path.startswith("/"):
                            path = "/" + path
                        break
                if not found:
                    break

            found = False
            for e in app.url_map:
                pattern = e[0]
                handler = e[1]
                extra = {}
                if len(e) > 2:
                    extra = e[2]

                if path == pattern:
                    found = True
                    break
                elif not isinstance(pattern, str):
                    m = pattern.match(path)
                    if m:
                        req.url_match = m
                        found = True
                        break

            if not found:
                headers_mode = "skip"
            else:
                headers_mode = extra.get("headers", self.headers_mode)

            if headers_mode == "skip":
                while True:
                    l = yield from reader.readline()
                    if l == b"\r\n":
                        break
            elif headers_mode == "parse":
                req.headers = yield from self.parse_headers(reader)
            else:
                assert headers_mode == "leave"

            if found:
                req.method = method
                req.path = path
                req.qs = qs
                req.reader = reader
                close = yield from handler(req, writer)
            else:
                yield from start_response(writer, status="404")
                yield from writer.awrite("404\r\n")
            #print(req, "After response write")
        except Exception as e:
            print("%s %s %r" % (req, writer, e))
            sys.print_exception(e)

        if close is not False:
            yield from writer.aclose()
        if __debug__ and self.debug > 1:
            print(req, "Finished processing request")

    def mount(self, url, app):
        app.url = url
        self.mounts.append(app)

    def route(self, url, **kwargs):
        def _route(f):
            self.url_map.append((url, f, kwargs))
            return f
        return _route

    def add_url_rule(self, url, func, **kwargs):
        self.url_map.append((url, func, kwargs))

    def make_task(self, host="127.0.0.1", port=8081, debug=False):
        gc.collect()
        self.debug = int(debug)
        return asyncio.start_server(self._handle, host, port)
