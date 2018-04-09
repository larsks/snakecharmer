import uasyncio as asyncio
import machine
import network
import sys
import time

from snakecharmer import config
from snakecharmer import hardware
from snakecharmer import iface
from snakecharmer import logging
from snakecharmer import utils


def handle_button_released(t):
    global button_released
    button_released = True


def check_config_mode():
    global button_released
    button_released = False

    logging.debug('check for flag file')
    if not utils.file_exists(iface.cfg_file):
        logging.debug('no flag file')
        return True

    logging.debug('check for button')
    if hardware.btn_config.value() == 1:
        logging.debug('check for long press')
        try:
            hardware.btn_config.irq(trigger=machine.Pin.IRQ_FALLING,
                                    handler=handle_button_released)

            time.sleep_ms(1000)
        finally:
            hardware.btn_config.irq(handler=None)

        if not button_released:
            logging.debug('detected long press')
            return True

    return False


def main():
    try:
        config.read_config()
        logging.setLevel(config.config.get('loglevel', 'INFO'))
        hardware.display.show('boot')

        if check_config_mode():
            from snakecharmer import mode_config as mode
            logging.info('entering config mode')
            mode_name = 'conf'
        else:
            from snakecharmer import mode_control as mode
            logging.info('entering control mode')
            mode_name = 'ctrl'

        hardware.display.show(mode_name)
        mode.prep()

        loop = asyncio.get_event_loop()
        tasks = mode.init_tasks(loop)

        for task in tasks:
            loop.create_task(task)

        try:
            loop.run_forever()
        finally:
            hardware.display.show('stop')
            logging.warning('snakecharmer has stopped')

            for task in tasks:
                task.close()

    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logging.error('caught exception -- resetting in 10 seconds')
        sys.print_exception(exc)
        time.sleep(10)
        machine.reset()
