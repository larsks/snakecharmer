import uasyncio as asyncio
import gc
import json
import machine
import network
import os
import time

from snakecharmer import logging
from snakecharmer import utils
from snakecharmer import webserver

gc.collect()

STATE_INITIAL = 0
STATE_CONNECTING = 1
STATE_FAILED = 2
STATE_CONNECTED = 3

sta = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)


class WebApp(webserver.Webserver):
    connect_timeout = 30000
    mode = 'conf'

    def __init__(self, loop):
        super().__init__(loop)

        self.state = STATE_INITIAL

        if sta.isconnected():
            if utils.file_exists('/connected'):
                self.state = STATE_CONNECTED
        else:
            sta.active(False)

        self.add_route('/api/status', self.api_status)
        self.add_route('/api/scan', self.api_scan)
        self.add_route('/api/connect', self.api_connect, 'POST')
        self.add_route('/', self.index)

    async def index(self, reader, writer, req):
        await self.send_file(
            writer, '/static/config.html')

    async def api_status(self, reader, writer, req):
        return self.get_network_state()

    async def api_scan(self, reader, writer, req):
        sta.active(True)
        return [{'ssid': net[0], 'channel': net[2],
                 'rssi': net[3], 'authmode': net[4]}
                for net in sorted(sta.scan(), key=lambda x: x[3])]

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
            os.remove('/connected')
        except OSError:
            pass

        sta.active(True)
        sta.connect(ssid, password)
        self.state = STATE_CONNECTING

        t_start = time.ticks_ms()
        while True:
            logging.debug('retry connection to network %s' % (ssid,))
            if sta.isconnected():
                logging.info('connected to network %s' % (ssid,))
                with open('/connected', 'wb'):
                    self.state = STATE_CONNECTED
                break

            t_now = time.ticks_ms()
            if time.ticks_diff(t_now, t_start) > self.connect_timeout:
                logging.error('failed to connect to network %s' % (ssid,))
                sta.active(False)
                self.state = STATE_FAILED
                break

            await asyncio.sleep(1)

    def get_network_state(self):
        return {
            'state': self.state,
            'ap': {
                'active': ap.active(),
                'ssid': ap.config('essid'),
                'ifconfig': ap.ifconfig(),
            },
            'sta': {
                'active': sta.active(),
                'connected': sta.isconnected(),
                'ifconfig': sta.ifconfig(),
                'rssi': sta.status('rssi'),
            },
        }


def init_tasks(loop):
    ws = WebApp(loop)

    t_webserver = asyncio.start_server(
        ws.handle_request, '0.0.0.0', 80)

    return [t_webserver]
