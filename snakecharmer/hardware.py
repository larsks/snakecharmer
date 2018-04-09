import dht
import ds18x20
import machine
import onewire
import tm1637

W1_PIN = 0
DHT_PIN = 2

RELAY_HEAT1_PIN = 12
RELAY_HEAT2_PIN = 13
RELAY_HUMID_PIN = 14

DISPLAY_CLK_PIN = 4
DISPLAY_DIO_PIN = 16

BTN_CONFIG_PIN = 5

w1 = onewire.OneWire(machine.Pin(W1_PIN))
ds = ds18x20.DS18X20(w1)
dht = dht.DHT22(machine.Pin(DHT_PIN))

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

btn_config = machine.Pin(BTN_CONFIG_PIN, machine.Pin.IN)
