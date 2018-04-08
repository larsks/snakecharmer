import uasyncio as asyncio
import json
import network

import snakecharmer.webserver

sta = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
connected = False


def get_network_state():
    return {
        'ap': {
            'active': ap.active(),
            'ifconfig': ap.ifconfig(),
        },
        'sta': {
            'active': sta.active(),
            'connected': sta.isconnected(),
            'ifconfig': sta.ifconfig(),
            'rssi': sta.status('rssi'),
        },
    }


class WebApp(snakecharmer.webserver.Webserver):
    def __init__(self):
        self.add_route('/mode', self.mode)
        self.add_route('/network', self.network)
        self.add_route('/static', self.static)

    async def mode(self, reader, writer, req):
        await self.send_response(
            writer,
            content=json.dumps(dict(mode='conf')))

    async def network(self, reader, writer, req):
        return get_network_state()


async def task_watch_network():
    global connected

    while True:
        if sta.isconnected():
            with open('/connected', 'w'):
                connected = True
            break

        await asyncio.asleep(1)


def register_tasks(loop):
    ws = WebApp()

    t_network = loop.create_task(task_watch_network)
    t_webserver = asyncio.start_server(
        ws.handle_request, '0.0.0.0', 80)

    return [t_network, t_webserver]
