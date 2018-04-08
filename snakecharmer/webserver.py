import json
import ure as re
import sys

chunksize = const(256)  # NOQA
content_type_map = {
    'js': 'application/javascript',
    'png': 'image/png',
    'jpg': 'image/jpg',
    'css': 'text/css',
    'txt': 'text/plain',
    'html': 'text/html',
}
default_content_type = 'application/octet-stream'


class Webserver:
    def __init__(self):
        self._routes = []
        self._static_path = '/static'

    def add_route(self, pattern, cb, method='GET'):
        self._routes.append((pattern, method, cb))

    def del_route(self, pattern, cb, method='GET'):
        self._routes.remove((pattern, method, cb))

    def clear_routes(self):
        del self._routes[:]

    async def send_header(self, writer,
                          status=200,
                          status_text='OK',
                          content_type='text/plain',
                          **headers):
        await writer.awrite('HTTP/1.1 %d %s\r\n' % (status, status_text))
        await writer.awrite('Content-type: %s\r\n' % (content_type,))
        for hdr, hdr_val in headers.items():
            await writer.awrite('%s: %s\r\n' % (hdr, hdr_val))
        await writer.awrite('\r\n')

    async def send_response(self, writer,
                            content=None,
                            status=200,
                            status_text='OK',
                            **kwargs):
        if content is None:
            content = status_text + '\r\n'

        kwargs.update({'content-length': len(content)})
        await self.send_header(writer,
                               status=status,
                               status_text=status_text,
                               **kwargs)

        await writer.awrite(content)
        await writer.aclose()

    async def send_file(self, writer, content, **kwargs):
        buf = bytearray(chunksize)
        bufview = memoryview(buf)

        await self.send_header(writer, **kwargs)

        while True:
            nb = content.readinto(buf)
            if nb == 0:
                break

            await writer.awrite(bufview[:nb])

        await writer.aclose()

    async def _handle_request(self, reader, writer, remote_addr):
        line0 = None
        req = {
            'remote_addr': remote_addr,
        }

        while True:
            line = (await reader.readline())

            # read until we reach the end of the headers
            # (or the end of data)
            if not line or line == b'\r\n':
                break

            if line0 is None:
                line0 = line.decode().strip().split(' ')

        try:
            method, uri = line0[:2]
        except (TypeError, ValueError):
            print('! invalid request from', remote_addr)
            return

        req.update(dict(method=method, uri=uri))
        print('* {remote_addr} {method} {uri}'.format(**req))

        for route in self._routes:
            match = re.match(route[0] + '$', uri)

            if match and route[1] == method:
                req.update(dict(match=match))
                handler = route[2]
                res = await handler(reader, writer, req)
                if isinstance(res, (dict, list)):
                    await self.send_response(
                        writer,
                        content_type='application/json',
                        content=json.dumps(res))
                break
        else:
            await self.send_response(writer,
                                     status=404,
                                     status_text='Not found')

    async def handle_request(self, reader, writer):
        remote_addr = '(unknown)'

        try:
            try:
                remote_addr = writer.get_extra_info('peername')[0]
            except (TypeError, IndexError):
                pass

            await self._handle_request(reader, writer, remote_addr)
        except Exception as exc:
            print('! error handling connection from', remote_addr)
            sys.print_exception(exc)
        finally:
            await writer.aclose()

    async def static(self, reader, writer, req):
        filename = req['match'].group(1)
        dot = filename.rfind('.')
        if dot >= 0:
            ext = filename[dot+1:]
            content_type = content_type_map.get(
                ext, default_content_type)
        else:
            content_type = default_content_type

        with open('%s/%s' % (self._static_path, filename,), 'rb') as fd:
            await self.send_file(writer, fd,
                                 content_type=content_type)
