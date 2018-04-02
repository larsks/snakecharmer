import hardware as hw
import json


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

    async def send_response(self, writer,
                            status=200,
                            status_text='OK',
                            message=None,
                            content_type='text/plain'):
        if message is None:
            message = status_text + '\r\n'

        await writer.awrite('HTTP/1.1 %d %s\r\n' % (status, status_text))
        await writer.awrite('Content-type: %s\r\n' % (content_type,))
        await writer.awrite('Content-length: %d\r\n' % (len(message),))
        await writer.awrite('\r\n')
        await writer.awrite(message)
        await writer.aclose()

    async def handle_request(self, reader, writer):
        data = (yield from reader.read())
        lines = data.decode().split('\r\n')

        if not lines:
            await writer.aclose()
            return

        line0 = lines.pop(0).split(' ')
        if len(line0) == 3:
            verb, uri, version = line0
        else:
            verb, uri = line0[:2]
            version = 'HTTP/1.0'

        try:
            remote_addr = writer.get_extra_info('peername')[0]
        except IndexError:
            remote_addr = '(unknown)'

        print('* %s %s %s %s' % (
            remote_addr, verb, uri, version))

        headers = {}
        for line in lines:
            if not line:
                break

            hdr_name, hdr_val = line.split(': ', 1)
            headers[hdr_name] = hdr_val

#        print('# request:', verb, '|', uri, '|', version)
#        print('# headers:', headers)
#        print('# routes:', self.routes)

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
                                 message=json.dumps(self._sensors),
                                 content_type='application/json')

    async def config(self, writer):
        await self.send_response(writer,
                                 message=json.dumps(self._config),
                                 content_type='application/json')

    async def relays(self, writer):
        relays = {k: v.value()
                  for k, v in hw.relays.items()}

        await self.send_response(writer,
                                 message=json.dumps(relays),
                                 content_type='application/json')

    async def index(self, writer):
        await self.send_response(writer,
                                 message='Running')
