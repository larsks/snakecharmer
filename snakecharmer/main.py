import machine
import time

from snakecharmer import control

restart = True

try:
    control.main()
except KeyboardInterrupt:
    pass
except:  # NOQA
    print('* resetting in 10 seconds')
    time.sleep(10)
    machine.reset()
