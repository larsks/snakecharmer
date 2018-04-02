import hardware as hw
import json


async def handle_request(reader, writer, sensors, config):
    data = (yield from reader.read())
    for line in data.split(b'\r\n'):
        if not line or line == b'\r\n':
            break

    relays = {k: v.value()
              for k, v in hw.relays.items()}

    data = {
        'sensors': sensors,
        'relays': relays,
    }

    yield from writer.awrite('HTTP/1.0 200 OK\r\n')
    yield from writer.awrite('Content-type: application/json\r\n')
    yield from writer.awrite('\r\n')
    yield from writer.awrite(json.dumps(data))
    yield from writer.aclose()
