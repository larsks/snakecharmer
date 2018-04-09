import json

config = {
    'loglevel': 'INFO',
}


def read_config():
    try:
        with open('/config.json') as fd:
            config.update(json.load(fd))
    except OSError:
        pass
