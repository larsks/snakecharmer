DEBUG = const(0)  # NOQA
INFO = const(1)  # NOQA
WARNING = const(2)  # NOQA
ERROR = const(3)  # NOQA

levelnames = [
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
]

loglevel = INFO


def setLevel(level):
    global loglevel

    if isinstance(level, str):
        level = levelnames.index(level)

    loglevel = level


def log(level, *args):
    if level >= loglevel:
        print('[%s]' % (levelnames[level],), *args)


def debug(*args):
    log(DEBUG, *args)


def info(*args):
    log(INFO, *args)


def warning(*args):
    log(WARNING, *args)


def error(*args):
    log(ERROR, *args)
