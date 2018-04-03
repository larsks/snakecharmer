import uasyncio as asyncio

import json
from snakecharmer import tasks
from snakecharmer import webserver

sensors = {}
config = {}


# via https://github.com/peterhinch/micropython-async/blob/master/asyn.py
class Event:
    def __init__(self):
        self.clear()

    def clear(self):
        self.flag = False

    def set(self):
        self.flag = True

    def __await__(self):
        while not self.flag:
            yield from asyncio.sleep(0)

    __iter__ = __await__


def main():
    with open('config.json', 'r') as fd:
        config.update(json.load(fd))

    loop = asyncio.get_event_loop()
    sensors_ready = Event()
    ws = webserver.Webserver(sensors, config)

    t_display = tasks.task_display(sensors, config, wait_on=sensors_ready)
    t_control = tasks.task_control(sensors, config, wait_on=sensors_ready)
    t_reader = tasks.task_read_sensors(sensors, config, notify=sensors_ready)
    t_webserver = asyncio.start_server(
        ws.handle_request, '0.0.0.0', 80)

    tasklist = [t_display, t_control, t_reader, t_webserver]
    for task in tasklist:
        loop.create_task(task)

    try:
        loop.run_forever()
        loop.close()
    finally:
        for task in tasklist:
            task.close()
