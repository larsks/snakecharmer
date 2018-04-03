import machine
import sys
import time

from snakecharmer import control

restart = True

try:
    control.main()
except KeyboardInterrupt:
    pass
except Exception as exc:
    sys.print_exception(exc)
    print('* resetting in 10 seconds')
    time.sleep(10)
    machine.reset()
