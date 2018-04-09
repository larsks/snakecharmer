import uasyncio as asyncio
import gc
import json
import machine
import network
import os
import time

from snakecharmer import iface
from snakecharmer import logging
from snakecharmer import utils
from snakecharmer import webserver

gc.collect()

STATE_INITIAL = 0
STATE_CONNECTING = 1
STATE_FAILED = 2
STATE_CONNECTED = 3


class WebApp(webserver.Webserver):
    connect_timeout = 30000
    mode = 'conf'

    def __init__(self, loop):
        super().__init__(loop)

        self.state = STATE_INITIAL

        if iface.sta.isconnected():
            if utils.file_exists('/connected'):
                self.state = STATE_CONNECTED
        else:
            iface.disable_station()

        self.add_route('/api/status', self.api_status)
        self.add_route('/api/scan', self.api_scan)
        self.add_route('/api/connect', self.api_connect, 'POST')
        self.add_route('/', self.index)

    async def index(self, reader, writer, req):
        await self.send_file(
            writer, '/static/config.html')

    async def api_status(self, reader, writer, req):
        data = {'state': self.state}
        data.update(iface.get_network_state())
        return data

    async def api_scan(self, reader, writer, req):
        iface.enable_station()
        return [{'ssid': net[0], 'channel': net[2],
                 'rssi': net[3], 'authmode': net[4]}
                for net in sorted(iface.sta.scan(), key=lambda x: x[3])]

    async def api_connect(self, reader, writer, req):
        data = json.loads(await reader.read())

        if 'ssid' not in data:
            return {'status': 'error',
                    'message': 'no ssid in request'}

        ssid = data['ssid']
        password = data.get('password')

        self.t_connect = self._loop.create_task(
            self.connect(ssid, password))

        return {'status': 'ok',
                'message': 'connecting to network'}

    async def connect(self, ssid, password):
        logging.info('trying to connect to network %s' % (ssid,))

        try:
            os.remove('/network.json')
        except OSError:
            pass

        iface.enable_station()
        iface.sta.connect(ssid, password)
        self.state = STATE_CONNECTING

        connected = (await iface.wait_for_connection(self.connect_timeout))
        if not connected:
            logging.error('failed to connect to network %s' % (ssid,))
            iface.disable_station()
            self.state = STATE_FAILED
        else:
            logging.info('connected to network %s' % (ssid,))
            with open('/network.json', 'wb') as fd:
                fd.write(json.dumps({'ssid': ssid, 'password': password}))
                self.state = STATE_CONNECTED


def prep():
    iface.enable_ap()


def init_tasks(loop):
    ws = WebApp(loop)

    t_webserver = asyncio.start_server(
        ws.handle_request, '0.0.0.0', 80)

    return [t_webserver]
