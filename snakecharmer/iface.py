import uasyncio as asyncio
import network
import time

from snakecharmer import logging


sta = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
cfg_file = '/network.json'


async def wait_for_connection(timeout=0):
    logging.info('waiting for connection')
    sta.active(True)

    t_start = time.ticks_ms()
    while not sta.isconnected():
        t_now = time.ticks_ms()
        if timeout > 0 and time.ticks_diff(t_now, t_start) >= timeout:
            return False

        await asyncio.sleep(1)

    return True


def enable_ap():
    logging.info('enabling ap mode')
    ap.active(True)


def disable_ap():
    logging.info('disabling ap mode')
    ap.active(False)


def enable_station():
    logging.info('enabling station mode')
    sta.active(True)


def disable_station():
    logging.info('disabling station mode')
    sta.active(False)


def get_network_state():
    return {
        'ap': {
            'active': ap.active(),
            'connected': sta.isconnected(),
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
