import hardware as hw
import json

chunksize = const(256)  # NOQA


class Webserver:
    def __init__(self, sensors, config):
        self._sensors = sensors
        self._config = config

        self.routes = {
            ('/', 'GET'): self.index,
            ('/sensors', 'GET'): self.sensors,
            ('/config', 'GET'): self.config,
            ('/relays', 'GET'): self.relays,
        }

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

        content_length = len(content)
        await self.send_header(writer,
                               status=status,
                               status_text=status_text,
                               content_length=content_length,
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

    async def handle_request(self, reader, writer):
        line0 = None

        try:
            remote_addr = writer.get_extra_info('peername')[0]
        except IndexError:
            remote_addr = '(unknown)'

        while True:
            line = (await reader.readline())
            if not line or line == b'\r\n':
                break

            if line0 is None:
                line0 = line.decode().strip().split(' ')

        try:
            if len(line0) == 3:
                verb, uri, version = line0
            else:
                verb, uri = line0[:2]
                version = 'HTTP/1.0'
        except (TypeError, ValueError):
            print('! invalid request from', remote_addr)
            await writer.aclose()
            return

        print('* %s %s %s %s' % (
            remote_addr, verb, uri, version))

        handler = self.routes.get((uri, verb))
        if handler is None:
            await self.send_response(writer,
                                     status=404,
                                     status_text='Not found')
            return
        else:
            await handler(writer)

    async def sensors(self, writer):
        await self.send_response(writer,
                                 content=json.dumps(self._sensors),
                                 content_type='application/json')

    async def config(self, writer):
        await self.send_response(writer,
                                 content=json.dumps(self._config),
                                 content_type='application/json')

    async def relays(self, writer):
        relays = {k: int(not v.value())
                  for k, v in hw.relays.items()}

        await self.send_response(writer,
                                 content=json.dumps(relays),
                                 content_type='application/json')

    async def index(self, writer):
        with open('status.html', 'rb') as fd:
            await self.send_file(writer, fd,
                                 content_type='text/html')
