import uasyncio as asyncio
import gc
import machine
import sys
import time

import hardware as hw


def handle_button_released(t):
    global button_released
    button_released = True


def file_exists(path):
    try:
        with open(path, 'r'):
            return True
    except OSError:
        return False


def check_config_mode():
    global button_released
    button_released = False

    print('# check for flag file')
    if not file_exists('/connected'):
        print('# no flag file')
        return True

    print('# check for button')
    if hw.btn_config.value() == 1:
        print('# check for long press')
        try:
            hw.btn_config.irq(trigger=machine.Pin.IRQ_FALLING,
                              handler=handle_button_released)

            time.sleep_ms(1000)
        finally:
            hw.btn_config.irq(handler=None)

        if not button_released:
            return True
    else:
        print('# no button')

    return False


try:
    hw.display.show('boot')

    if check_config_mode():
        from snakecharmer import mode_config as mode
        gc.collect()
        hw.display.show('conf')
    else:
        from snakecharmer import mode_control as mode
        gc.collect()
        hw.display.show('run ')

    loop = asyncio.get_event_loop()
    tasks = mode.register_tasks()

    try:
        loop.run_forever()
    finally:
        hw.display('stop')

        for task in tasks:
            task.close()

except KeyboardInterrupt:
    pass
except Exception as exc:
    sys.print_exception(exc)
    print('* resetting in 10 seconds')
    time.sleep(10)
    machine.reset()
