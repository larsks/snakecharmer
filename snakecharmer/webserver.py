import hardware as hw
import json
import ure as re
import sys

chunksize = const(256)  # NOQA


class Webserver:
    def __init__(self, sensors, config):
        self._sensors = sensors
        self._config = config

        self.routes = (
            ('/sensors', 'GET', self.sensors),
            ('/relays', 'GET', self.relays),
            ('/config/(.*)', 'GET', self.get_one_config),
            ('/config/(.*)', 'PUT', self.set_one_config),
            ('/config', 'GET', self.config),

            # must be last!
            ('/', 'GET', self.index),
        )

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

    async def _handle_request(self, reader, writer, remote_addr):
        line0 = None

        while True:
            line = (await reader.readline())

            # read until we reach the end of the headers
            # (or the end of data)
            if not line or line == b'\r\n':
                break

            if line0 is None:
                line0 = line.decode().strip().split(' ')

        try:
            verb, uri = line0[:2]
        except (TypeError, ValueError):
            print('! invalid request from', remote_addr)
            return

        print('* %s %s %s' % (remote_addr, verb, uri))

        for route in self.routes:
            match = re.match(route[0], uri)

            if match and route[1] == verb:
                handler = route[2]
                await handler(reader, writer, match)
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

    async def sensors(self, reader, writer, match):
        await self.send_response(writer,
                                 content=json.dumps(self._sensors),
                                 content_type='application/json')

    async def one_sensor(self, reader, writer, match):
        sensor_id = match.group(1)
        await self.send_response(writer,
                                 content=json.dumps(self._sensors[sensor_id]),
                                 content_type='application/json')

    async def relays(self, reader, writer, match):
        relays = {k: int(not v.value())
                  for k, v in hw.relays.items()}

        await self.send_response(writer,
                                 content=json.dumps(relays),
                                 content_type='application/json')

    async def config(self, reader, writer, match):
        await self.send_response(writer,
                                 content=json.dumps(self._config),
                                 content_type='application/json')

    async def get_one_config(self, reader, writer, match):
        k = match.group(1)
        await self.send_response(writer,
                                 content=json.dumps(self._config[k]),
                                 content_type='application/json')

    async def set_one_config(self, reader, writer, match):
        k = match.group(1)
        v = json.loads(await reader.read())

        print('* setting config[%s] = %s' % (k, v))
        self._config[k] = v
        await self.send_response(writer,
                                 content=json.dumps(self._config[k]),
                                 content_type='application/json')

    async def index(self, reader, writer, match):
        with open('status.html', 'rb') as fd:
            await self.send_file(writer, fd, content_type='text/html')
