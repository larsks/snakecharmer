import dht
import ds18x20
import machine
import onewire
import tm1637

W1_PIN_0 = 4
W1_PIN_1 = 0
DHT_PIN_0 = 2

RELAY_HEAT1_PIN = 12
RELAY_HEAT2_PIN = 13
RELAY_HUMID_PIN = 14

DISPLAY_CLK_PIN = 5
DISPLAY_DIO_PIN = 4

# w1_0 = onewire.OneWire(machine.Pin(W1_PIN_0))
w1_1 = onewire.OneWire(machine.Pin(W1_PIN_1))
# ds_0 = ds18x20.DS18X20(w1_0)
ds_1 = ds18x20.DS18X20(w1_1)
dht_0 = dht.DHT22(machine.Pin(DHT_PIN_0))

sensors_ds = [ds_1]
sensors_dht = [dht_0]

heat1 = machine.Pin(RELAY_HEAT1_PIN, machine.Pin.OUT, value=1)
heat2 = machine.Pin(RELAY_HEAT2_PIN, machine.Pin.OUT, value=1)
humidifier = machine.Pin(RELAY_HUMID_PIN, machine.Pin.OUT, value=1)

relays = {
    'heat1': heat1,
    'heat2': heat2,
    'humidifier': humidifier,
}

display = tm1637.TM1637Decimal(clk=machine.Pin(DISPLAY_CLK_PIN),
                               dio=machine.Pin(DISPLAY_DIO_PIN))
