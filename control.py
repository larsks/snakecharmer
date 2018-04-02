import uasyncio as asyncio

import hardware
import json
import tasks
import utils
import webserver

sensors = {}
config = {}


def request_handler(reader, writer):
    yield from webserver.handle_request(reader, writer, sensors, config)


def main():
    with open('config.json', 'r') as fd:
        config.update(json.load(fd))

    loop = asyncio.get_event_loop()

    t_display = tasks.task_display(sensors, config)
    t_control = tasks.task_control(sensors, config)
    t_reader = tasks.task_read_sensors(sensors, config)
    t_webserver = asyncio.start_server(
        request_handler, '0.0.0.0', 80)

    tasklist = [t_display, t_control, t_reader, t_webserver]
    for task in tasklist:
        loop.create_task(task)

    try:
        loop.run_forever()
        loop.close()
    except KeyboardInterrupt:
        pass
    finally:
        for task in tasklist:
            task.close()
