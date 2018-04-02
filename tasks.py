import hardware as hw
import uasyncio as asyncio
import ubinascii as binascii
import utils


async def task_display(sensors, config, wait_on=None):
    hw.display.show('RUN ')

    if wait_on is not None:
        print('* display: waiting for sensors')
        await wait_on

    try:
        while True:
            for i, values in enumerate(sensors.values()):
                for k, v in values.items():
                    if k == 't' and config['units'] == 'f':
                        v = '%0.1fF' % (utils.C2F(v),)
                    elif k == 't':
                        v = '%0.1fC' % (v,)
                    else:
                        v = '%0.1f' % (v,)

                    hw.display.show('S%d %s' % (i, k))
                    await asyncio.sleep(1)
                    hw.display.show('%s    ' % (v,))
                    await asyncio.sleep(1)

            r = ['%d' % (not x.value(),) for x in hw.relays.values()]
            hw.display.show('r%s' % (''.join(r)))
            await asyncio.sleep(config['display_interval'])
    except GeneratorExit:
        hw.display.show('STOP')


async def task_read_sensors(sensors, config, notify=None):
    while True:
        for bus in hw.sensors_ds:
            bus.convert_temp()

        for sensor in hw.sensors_dht:
            sensor.measure()

        # allow sensors to settle
        await asyncio.sleep(1)

        sensors.clear()
        for bus in hw.sensors_ds:
            for sensor in bus.scan():
                id = 'ds-%s' % (binascii.hexlify(sensor).decode())
                temp = bus.read_temp(sensor)
                sensors[id] = {'t': temp}

        for i, sensor in enumerate(hw.sensors_dht):
            id = 'dht-%d' % (i,)
            temp = sensor.temperature()
            humid = sensor.humidity()
            sensors[id] = {'t': temp, 'h': humid}

        print('# sensors:', sensors)
        if notify is not None:
            notify.set()
        await asyncio.sleep(config['read_interval'])


def _handle_sensor(sensors, config, sensor_name, k, relay_name):
    print('* handling sensor %s -> %s' % (sensor_name, relay_name))

    sensor_id = config['%s_id' % (sensor_name,)]
    sensor = sensors.get(sensor_id)
    if sensor is None:
        print('! no reading for sensor %s' % (sensor_name,))
        return

    value = sensor.get(k)
    if value is None:
        print('! no value for sensor %s key %s' % (sensor_name, k))
        return

    relay = hw.relays.get(relay_name)
    if relay is None:
        print('! no relay named %s' % (relay_name,))
        return

    if config.get('units', 'c') == 'f' and k == 't':
        value = utils.C2F(value)

    low = config['%s_low' % (sensor_name,)]
    high = config['%s_high' % (sensor_name,)]

    if value <= low:
        print('* %s value %f <= %f activating %s' % (
            sensor_name, value, low, relay_name))
        relay.off()
    elif value >= high:
        print('* %s value %f >= %f deactivating %s' % (
            sensor_name, value, high, relay_name))
        relay.on()


async def task_control(sensors, config, wait_on=None):
    if wait_on is not None:
        print('* control: waiting for sensors')
        await wait_on

    try:
        while True:
            _handle_sensor(sensors, config, 'temp1', 't', 'heat1')
            _handle_sensor(sensors, config, 'temp2', 't', 'heat2')
            _handle_sensor(sensors, config, 'humid', 'h', 'humidifier')

            await asyncio.sleep(config['check_interval'])
    except GeneratorExit:
        print('* deactivating all relays')
        for relay in hw.relays.values():
            relay.on()
