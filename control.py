import config
import hardware as hw
import json
import machine
import select
import socket
import time
from ubinascii import hexlify

default_check_interval = 30000
default_sensor_interval = 10000
default_prep_interval = 800


class Control:
    def __init__(self,
                 check_interval=None,
                 sensor_interval=None,
                 prep_interval=None,
                 temp1_low=None,
                 temp1_high=None,
                 temp1_id=None,
                 temp2_low=None,
                 temp2_high=None,
                 temp2_id=None,
                 humid_low=None,
                 humid_high=None,
                 humid_id=None):

        self.check_interval = check_interval or default_check_interval
        self.sensor_interval = sensor_interval or default_sensor_interval
        self.prep_interval = prep_interval or default_prep_interval

        self.temp1_low = temp1_low
        self.temp1_high = temp1_high
        self.temp1_id = temp1_id

        self.temp2_low = temp2_low
        self.temp2_high = temp2_high
        self.temp2_id = temp2_id

        self.humid_low = humid_low
        self.humid_high = humid_high
        self.humid_id = humid_id

        self.sensors = {}
        self.last_read = 0

        self.init_timer()
        self.init_socket()
        self.init_poll()

    def init_timer(self):
        self.t_update = machine.Timer(-1)

    def start_timer(self):
        print('* starting sensor read timer')
        self.t_update.init(period=self.sensor_interval,
                           mode=machine.Timer.PERIODIC,
                           callback=self.update_sensors)

    def update_sensors(self, t):
        print('* updating sensors')
        self.prep_sensors()
        t = machine.Timer(-1)
        t.init(period=self.prep_interval,
               mode=machine.Timer.ONE_SHOT,
               callback=self.read_sensors)

    def prep_sensors(self):
        print('* prep sensors')
        for bus in hw.sensors_ds:
            bus.convert_temp()

        for sensor in hw.sensors_dht:
            sensor.measure()

    def read_sensors(self, t):
        print('* read sensors')
        self.sensors = {}
        for bus in hw.sensors_ds:
            for sensor in bus.scan():
                id = 'ds-%s' % (hexlify(sensor).decode())
                temp = bus.read_temp(sensor)
                self.sensors[id] = {'t': temp}

        for i, sensor in enumerate(hw.sensors_dht):
            id = 'dht-%d' % (i,)
            temp = sensor.temperature()
            humid = sensor.humidity()
            self.sensors[id] = {'t': temp, 'h': humid}

        self.last_read = time.ticks_ms()

    def stop_timer(self):
        print('* stopping sensor read timer')
        self.t_update.deinit()

    def init_socket(self):
        server = socket.socket()
        server.bind(('0.0.0.0', 80))
        server.listen(2)
        self.server = server

    def close_socket(self):
        print('* closing server socket')
        self.server.close()

    def init_poll(self):
        poll = select.poll()
        self.poll = poll

    def loop(self):
        poll = self.poll
        server = self.server
        poll.register(server, select.POLLIN)

        delta = int(self.check_interval * 0.9)

        last_check = 0
        while True:
            events = poll.poll(self.check_interval)
            now = time.ticks_ms()
            print('* sensors:', self.sensors)
            if time.ticks_diff(now, last_check) >= delta:
                print('* running maintenance tasks')
                last_check = time.ticks_ms()
                self.do_maintenance()

            if not events:
                continue

            for event in events:
                sock, flag = event[:2]
                if sock == self.server:
                    client, addr = sock.accept()
                    self.handle_client(client, addr)

    def handle_sensor(self, sensor_name, k, low, high, relay_name):
        sensor = self.sensors.get(sensor_name)
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

        if value <= low:
            print('* %s value %f <= %f activating %s' % (
                sensor_name, value, low, relay_name))
            relay.off()
        elif value >= high:
            print('* %s value %f >= %f deactivating %s' % (
                sensor_name, value, high, relay_name))
            relay.on()

    def do_maintenance(self):
        self.handle_sensor(self.temp1_id, 't',
                           self.temp1_low, self.temp1_high,
                           'heat1')

        self.handle_sensor(self.temp2_id, 't',
                           self.temp2_low, self.temp2_high,
                           'heat2')

        self.handle_sensor(self.humid_id, 'h',
                           self.humid_low, self.humid_high,
                           'humidifier')

    def handle_client(self, client, addr):
        print('* handling connection from', addr)
        while True:
            line = client.readline()
            if not line or line == b'\r\n':
                break

        relays = self.relay_state()
        data = {
            'sensors': self.sensors,
            'relays': relays,
            'last_read': self.last_read,
        }

        client.send(json.dumps(data))
        client.close()

    def relay_state(self):
        return {k: v.value()
                for k, v in hw.relays.items()}

    def start(self):
        try:
            self.start_timer()
            self.loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.close_socket()
            self.stop_timer()


c = Control(
    temp1_low=config.temp1_low,
    temp1_high=config.temp1_high,
    temp1_id=config.temp1_id,
    temp2_low=config.temp2_low,
    temp2_high=config.temp2_high,
    temp2_id=config.temp2_id,
    humid_low=config.humid_low,
    humid_high=config.humid_high,
    humid_id=config.humid_id,
)
c.start()
