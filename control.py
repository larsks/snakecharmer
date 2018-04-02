import uasyncio as asyncio

import hardware
import json
import tasks
import utils

sensors = {}


def make_signal(targets):
    for target in targets:
        target.send(None)


def main():
    with open('config.json', 'r') as fd:
        config = json.load(fd)

    loop = asyncio.get_event_loop()

    t_display = tasks.task_display(config, sensors)
    t_control = tasks.task_control(config, sensors)
    t_reader = tasks.task_read_sensors(config, sensors)

    for task in [t_display, t_control, t_reader]:
        loop.create_task(task)

    try:
        loop.run_forever()
        loop.close()
    finally:
        [relay.on() for relay in hardware.relays.values()]
