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
        try:
            level = levelnames.index(level)
        except ValueError:
            error('unknown log level: %s' % (level,))
            return
    elif isinstance(level, int):
        if level < 0 or level >= len(levelnames):
            error('unknown log level: %d' % (level,))
            return
    else:
        error('bad value for log level: %s' % (repr(level),))
        return

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
