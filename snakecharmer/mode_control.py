import uasyncio as asyncio
import gc
import json
import machine
import network
import os
import time

from snakecharmer import iface
from snakecharmer import hardware
from snakecharmer import logging
from snakecharmer import utils
from snakecharmer import webserver

gc.collect()


class WebApp(webserver.Webserver):
    connect_timeout = 30000
    mode = 'control'

    def __init__(self, loop):
        super().__init__(loop)

        self.add_route('/', self.index)

    async def index(self, reader, writer, req):
        await self.send_file(
            writer, '/static/status.html')


async def display_address():
    await iface.wait_for_connection()
    hardware.display.scroll(iface.sta.ifconfig()[0])


def prep():
    iface.disable_ap()


def init_tasks(loop):
    ws = WebApp(loop)

    t_network = display_address()
    t_webserver = asyncio.start_server(
        ws.handle_request, '0.0.0.0', 80)

    return [t_network, t_webserver]
